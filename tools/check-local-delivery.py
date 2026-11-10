"""Read-only delivery check: no login, save write, order, clock or model call."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DEPENDENCIES = ['deploy-server-1', 'deploy-mongo-1', 'deploy-qdrant-1',
                'deploy-elasticsearch-1', 'deploy-neo4j-1', 'ainpc-v2-redis-dev',
                'ainpc-v2-mongo-dev', 'ainpc-v2-nats-dev', 'org-flow-engine-postgres-dev-postgres-1']


def load_manifest(path: Path) -> dict:
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if manifest.get('schemaVersion') != 1:
        raise ValueError('unsupported delivery manifest schema')
    containers = manifest.get('containers')
    package = manifest.get('package')
    if not isinstance(containers, dict) or not containers:
        raise ValueError('delivery manifest has no containers')
    if not isinstance(package, dict) or not package.get('path') or not package.get('sha256'):
        raise ValueError('delivery manifest has no package contract')
    for name, contract in containers.items():
        if not name or not isinstance(contract, dict) or not contract.get('image'):
            raise ValueError('delivery manifest contains an invalid container contract')
    return manifest


def root_path(relative: str) -> Path:
    candidate = (ROOT / relative).resolve()
    if candidate != ROOT and ROOT not in candidate.parents:
        raise ValueError('delivery manifest path escapes repository root')
    return candidate

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument(
        '--manifest', type=Path,
        default=ROOT / 'config/local-delivery-manifest.json',
    )
    args = parser.parse_args()
    manifest = load_manifest(args.manifest.resolve())
    roles = list(manifest['containers'])
    checks = []
    for name in roles + DEPENDENCIES:
        result = subprocess.run(['docker', 'inspect', name], capture_output=True, text=True, encoding='utf-8')
        if result.returncode:
            checks.append({'container': name, 'passed': False, 'error': 'inspect_failed'})
            continue
        row = json.loads(result.stdout)[0]
        health = row['State'].get('Health', {}).get('Status')
        expected = row['Config']['Image'] if name in DEPENDENCIES else manifest['containers'][name]['image']
        health_required = name not in DEPENDENCIES and manifest['containers'][name].get('healthRequired', True)
        checks.append({'container': name, 'running': row['State']['Running'], 'health': health,
                       'imageMatches': None if name in DEPENDENCIES else row['Config']['Image'] == expected,
                       'restartPolicy': row['HostConfig']['RestartPolicy']['Name'],
                       'passed': row['State']['Running'] and row['Config']['Image'] == expected
                           and row['HostConfig']['RestartPolicy']['Name'] == 'unless-stopped'
                           and (health == 'healthy' or not health_required and health is None or name in DEPENDENCIES and health is None),
                       'imagePinnedByCheck': name not in DEPENDENCIES})
    readiness = None
    for path, expected in [('/', 200), ('/health/live', 200), ('/health/ready', 200), ('/api/dongzhou/v1/save', 401)]:
        try:
            with urllib.request.urlopen('http://127.0.0.1:8780' + path, timeout=10) as response:
                status = response.status
                if path == '/health/ready':
                    readiness = json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as error:
            status = error.code
            error.close()
        except (urllib.error.URLError, TimeoutError):
            status = 'unavailable'
        checks.append({'path': path, 'status': status, 'passed': status == expected})
    required_capabilities = manifest.get('requiredCapabilities', [])
    readiness_data = readiness.get('data', readiness) if isinstance(readiness, dict) else {}
    services = readiness_data.get('services', {}) if isinstance(readiness_data, dict) else {}
    capability_states = {
        name: bool(isinstance(services.get(name), dict) and services[name].get('online'))
        for name in required_capabilities
    }
    checks.append({
        'requiredCapabilities': capability_states,
        'passed': bool(required_capabilities) and all(capability_states.values()),
    })
    package = root_path(str(manifest['package']['path']))
    digest = None
    if package.exists():
        with package.open('rb') as stream:
            hasher = hashlib.sha256()
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                hasher.update(chunk)
            digest = hasher.hexdigest()
    checks.append({'package': package.name, 'sha256': digest, 'passed': digest == manifest['package']['sha256']})
    fulltext_report = root_path(str(manifest['fulltextReport']))
    fulltext_verified = False
    if fulltext_report.exists():
        try:
            fulltext = json.loads(fulltext_report.read_text(encoding='utf-8'))
            fulltext_verified = fulltext.get('result') == 'PASS' and fulltext.get('mode') == 'live-no-api-interception'
        except (OSError, json.JSONDecodeError):
            pass
    checks.append({'fulltextReport': fulltext_report.name, 'passed': fulltext_verified})
    report = {'passed': all(c['passed'] for c in checks), 'scope': 'local-delivery-readonly',
              'manifest': str(args.manifest.resolve()), 'manifestSchemaVersion': manifest['schemaVersion'],
              'publicProductionVerified': False, 'fulltextVerified': fulltext_verified, 'businessWrites': 0, 'checks': checks}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report['passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
