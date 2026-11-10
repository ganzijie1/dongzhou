"""Run real nginx in a disposable internal Docker network, with no published ports.
Uses a synthetic certificate and mock upstream; not production TLS/firewall acceptance.
"""
from __future__ import annotations

import ipaddress
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
NGINX = "nginx:stable-alpine"
PYTHON = "python:3.12.12-slim"


def run(*args):
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    if result.returncode:
        raise RuntimeError(f"{args[0:3]} failed: {result.stdout} {result.stderr}")
    return result.stdout.strip()


def main():
    suffix = uuid.uuid4().hex[:10]
    network, upstream, proxy = [f"dz-ingress-{name}-{suffix}" for name in ("net", "mock", "proxy")]
    created = []
    network_created = False
    openssl = shutil.which("openssl")
    if not openssl:
        raise RuntimeError("openssl is required for the temporary test certificate")
    try:
        run("docker", "network", "create", "--internal", network)
        network_created = True
        info = json.loads(run("docker", "network", "inspect", network))[0]
        subnet = ipaddress.ip_network(info["IPAM"]["Config"][0]["Subnet"])
        trusted, untrusted = str(subnet.network_address + 10), str(subnet.network_address + 11)
        with tempfile.TemporaryDirectory(prefix="nginx-isolation-", dir=ROOT / "output") as temp:
            folder = Path(temp)
            (folder / "openssl.cnf").write_text("[req]\ndistinguished_name=dn\n[dn]\n", encoding="utf-8")
            run(openssl, "req", "-config", str(folder / "openssl.cnf"), "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1", "-subj", "/CN=dongzhou.example.invalid", "-keyout", str(folder / "privkey.pem"), "-out", str(folder / "fullchain.pem"))
            reference = (ROOT / "config/nginx-dongzhou-production.conf.example").read_text(encoding="utf-8")
            reference = reference.replace("127.0.0.1:8780", f"{upstream}:8780").replace("10.0.0.10:8782", "0.0.0.0:8782").replace("10.0.0.0/24", f"{trusted}/32").replace("/etc/nginx/tls/", "/test/")
            (folder / "nginx.conf").write_text("events {}\nhttp {\n" + reference + "\n}\n", encoding="utf-8")
            mock = "from http.server import BaseHTTPRequestHandler,HTTPServer\nclass Handler(BaseHTTPRequestHandler):\n def do_GET(self):\n  self.send_response(200); self.send_header('X-Mock-Upstream','isolated'); self.end_headers(); self.wfile.write(b'mock')\n do_POST=do_GET\nHTTPServer(('0.0.0.0',8780),Handler).serve_forever()"
            (folder / "mock.py").write_text(mock, encoding="utf-8")
            mount = f"{folder.resolve()}:/test:ro"
            run("docker", "run", "--detach", "--name", upstream, "--network", network, "--volume", mount, PYTHON, "python", "/test/mock.py")
            created.append(upstream)
            syntax = run("docker", "run", "--rm", "--network", network, "--volume", mount, NGINX, "nginx", "-t", "-c", "/test/nginx.conf")
            run("docker", "run", "--detach", "--name", proxy, "--network", network, "--volume", mount, NGINX, "nginx", "-g", "daemon off;", "-c", "/test/nginx.conf")
            created.append(proxy)
            for name in created:
                inspection = json.loads(run("docker", "inspect", name))[0]
                assert not inspection["HostConfig"].get("PortBindings"), "Test must never publish a host port"
            client = r'''
import http.client,json,ssl,sys,time
host,mode=sys.argv[1:]
def request(path,port,method='GET'):
 for attempt in range(20):
  try:
   c=http.client.HTTPSConnection(host,port,context=ssl._create_unverified_context(),timeout=5) if port==443 else http.client.HTTPConnection(host,port,timeout=5)
   c.request(method,path); r=c.getresponse(); result=(r.status,r.getheader('X-Mock-Upstream')); r.read(); c.close(); return result
  except ConnectionRefusedError:
   if attempt==19: raise
   time.sleep(.1)
results=[]
if mode=='trusted':
 for path in ['/', '/api/dongzhou/v1/save']:
  for method in ['GET','POST']:
   status,marker=request(path,443,method); assert (status,marker)==(200,'isolated'),(path,status,marker); results.append([method,path,status])
 for path in ['/api','/api/v1','/api/v1/NDLLMAllAILogin','/api/v1/ainpc/login-ready','/api/v2/NDLLMSendPrivateMessage','/internal','/internal/v1/organization-tasks/dialogues/report','/docs','/redoc','/openapi.json','/health/ready','/metrics','/api%2Fv1/NDLLMAllAILogin','/api/dongzhou/v1/../../v1/NDLLMAllAILogin','/api/dongzhou/v1/..%2f..%2fv1/NDLLMAllAILogin','//api//v1//NDLLMAllAILogin']:
  for method in ['GET','POST']:
   status,marker=request(path,443,method); assert status==403 and marker is None,(path,status,marker); results.append([method,path,status])
 for path in ['/api/v1/NDLLMAllAILogin','/api/v2/NDLLMSendPrivateMessage','/health/ready']:
  status,marker=request(path,8782); assert (status,marker)==(200,'isolated'),(path,status,marker); results.append(['GET',path,status])
 assert request('/api/dongzhou/v1/save',8782)[0]==404
else:
 for path in ['/api/v1/NDLLMAllAILogin','/api/v2/NDLLMSendPrivateMessage','/health/ready']:
  status,marker=request(path,8782); assert status==403 and marker is None,(path,status,marker); results.append(['GET',path,status])
print(json.dumps({'mode':mode,'passed':True,'checks':len(results)}))
'''
            (folder / "client.py").write_text(client, encoding="utf-8")
            results = []
            for address, mode in ((trusted, "trusted"), (untrusted, "untrusted")):
                results.append(json.loads(run("docker", "run", "--rm", "--network", network, "--ip", address, "--volume", mount, PYTHON, "python", "/test/client.py", proxy, mode)))
            digest = json.loads(run("docker", "image", "inspect", NGINX))[0]["RepoDigests"]
            print(json.dumps({"passed": True, "nginxSyntax": True, "image": digest, "internalNetwork": info["Internal"], "hostPortsPublished": False, "probes": results, "publicProductionAcceptance": False, "testOnlyCertificate": True}, ensure_ascii=False))
    finally:
        for name in reversed(created):
            run("docker", "rm", "--force", name)
        if network_created:
            run("docker", "network", "rm", network)


if __name__ == "__main__":
    main()
