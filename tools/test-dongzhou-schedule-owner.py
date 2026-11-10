"""Validate the true Gateway catalog owner without deploying or regenerating plans."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess


def execute(arguments):
    result = subprocess.run(arguments, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    if result.returncode:
        # Compose errors can contain expanded settings; do not echo their bodies.
        raise RuntimeError(f"Validation command failed: {arguments[0]} (exit {result.returncode})")
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ainpc-root", type=Path, default=Path("E:/game/ainpc"))
    args = parser.parse_args()
    base = args.ainpc_root / "docker/v2/dev/docker-compose.yml"
    overlay = args.ainpc_root / "docker/v2/docker-compose-dongzhou.yml"
    common = ["docker", "compose", "--project-directory", str(base.parent), "-f", str(base)]
    baseline = json.loads(execute(common + ["config", "--no-interpolate", "--format", "json"]))
    merged = json.loads(execute(common + ["-f", str(overlay), "config", "--no-interpolate", "--format", "json"]))
    prior, current = baseline["services"]["gateway"], merged["services"]["gateway"]
    for service in (prior, current):
        if isinstance(service.get("environment"), list):
            service["environment"] = dict(item.split("=", 1) if "=" in item else (item, None) for item in service["environment"])
    variable = "AINPC_CONST_CSV_SCHEDULE_TRANSACTIONS"
    assert current["environment"][variable] == "app2/resources/transaction/dongzhou_schedule_transactions.csv"
    for key, value in prior["environment"].items():
        assert current["environment"][key] == value, f"Unexpected Gateway environment change: {key}"
    for key in set(prior) | set(current):
        if key not in {"image", "environment"}:
            assert prior.get(key) == current.get(key), f"Unexpected Gateway configuration change: {key}"
    global_image = merged["services"]["global"]["image"]
    assert global_image == "${DONGZHOU_AINPC_GLOBAL_IMAGE:-ainpc-app:v20261109-dongzhou-authority-retry19}"
    prefix = "${DONGZHOU_AINPC_GATEWAY_IMAGE:-"
    assert current["image"].startswith(prefix) and current["image"].endswith("}")
    image = current["image"][len(prefix):-1]
    assert image == "ainpc-app:v20261109-dongzhou-authority-retry19"
    for number in range(6):
        assert merged["services"][f"business-{number}"]["image"] == "${DONGZHOU_AINPC_IMAGE:-" + image + "}"
    code = r'''
import ast,asyncio,json
from pathlib import Path
import yaml
from app2.infrastructure.providers.const_store import CsvConstStoreProvider
root=Path('/app')
def collections(path,classname):
 tree=ast.parse((root/path).read_text())
 cls=next(node for node in tree.body if isinstance(node,ast.ClassDef) and node.name==classname)
 for node in cls.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='const_collections' for t in node.targets): return ast.literal_eval(node.value)
  if isinstance(node,ast.AnnAssign) and isinstance(node.target,ast.Name) and node.target.id=='const_collections': return ast.literal_eval(node.value)
 raise AssertionError('owner metadata missing')
assert 'schedule_transactions' in collections(Path('app2/modules/action_catalog/module.py'),'ActionCatalogModule')
assert collections(Path('app2/modules/action_catalog/remote_module.py'),'ActionCatalogRemoteModule')==[]
async def validate():
 config=root/'config/const_tables.yaml'
 table=yaml.safe_load(config.read_text())
 store=CsvConstStoreProvider()
 loaded=await store.load_from_csv(str(config),project_root=str(root),excluded_collections=set(table['tables'])-{'schedule_transactions'})
 entries=list(store.get_all('schedule_transactions').values())
 ids=sorted(int(item.id) for item in entries)
 assert ids==list(range(9100101,9100113)),ids
 print(json.dumps({'result':'PASS','catalogOwner':'Gateway','businessCatalogIsProxy':True,'count':loaded['schedule_transactions'],'ids':ids}))
asyncio.run(validate())
'''
    output = execute(["docker", "run", "--rm", "--network", "none", "--read-only", "--env", f"{variable}={current['environment'][variable]}", "--entrypoint", "python", image, "-c", code])
    evidence = json.loads(output.strip().splitlines()[-1])
    print(json.dumps({"result": "PASS", "changedGatewayKeys": ["image", "environment.AINPC_CONST_CSV_SCHEDULE_TRANSACTIONS"], "changedGlobalKeys": ["image"], "gatewayInheritedKeysPreserved": True, "globalNotificationFixImageSelected": True, "imageCatalog": evidence, "deployed": False, "plansRegenerated": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
