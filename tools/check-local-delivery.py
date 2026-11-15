"""Read-only delivery check: no login, save write, order, clock or model call."""
import argparse
import hashlib
import http.client
import json
from pathlib import Path, PurePosixPath
import subprocess
import urllib.error
import urllib.request
import zipfile

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
    source_files = package.get('sourceFiles')
    if not isinstance(source_files, dict) or not source_files:
        raise ValueError('delivery manifest package has no source-file contract')
    for source, archive_name in source_files.items():
        if not isinstance(source, str) or not source or not valid_archive_path(archive_name):
            raise ValueError('delivery manifest contains an invalid package source-file contract')
    source_trees = package.get('sourceTrees')
    if not isinstance(source_trees, dict) or not source_trees:
        raise ValueError('delivery manifest package has no source-tree contract')
    for source, archive_name in source_trees.items():
        if not isinstance(source, str) or not source or not valid_archive_path(archive_name):
            raise ValueError('delivery manifest contains an invalid package source-tree contract')
    for name, contract in containers.items():
        if not name or not isinstance(contract, dict) or not contract.get('image'):
            raise ValueError('delivery manifest contains an invalid container contract')
    return manifest


def root_path(relative: str, root: Path = ROOT) -> Path:
    resolved_root = root.resolve()
    candidate = (resolved_root / relative).resolve()
    if candidate != resolved_root and resolved_root not in candidate.parents:
        raise ValueError('delivery manifest path escapes repository root')
    return candidate


def valid_archive_path(value) -> bool:
    if not isinstance(value, str) or not value:
        return False
    normalized = PurePosixPath(value.replace('\\', '/'))
    return not normalized.is_absolute() and '..' not in normalized.parts


def sha256_stream(stream) -> str:
    hasher = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        hasher.update(chunk)
    return hasher.hexdigest()


def check_package_sources(
    package: Path,
    source_files: dict[str, str],
    root: Path = ROOT,
    source_trees: dict[str, str] | None = None,
) -> list[dict]:
    checks = []
    if not package.exists():
        return [{'package': package.name, 'passed': False, 'error': 'missing_package'}]
    try:
        with zipfile.ZipFile(package) as archive:
            names = set(archive.namelist())
            normalized_names = {
                name[2:] if name.startswith('./') else name: name
                for name in names
            }
            for source_name, archive_name in source_files.items():
                source = root_path(source_name, root)
                packaged_name = normalized_names.get(archive_name)
                source_digest = None
                packaged_digest = None
                if source.is_file():
                    with source.open('rb') as stream:
                        source_digest = sha256_stream(stream)
                if packaged_name:
                    with archive.open(packaged_name) as stream:
                        packaged_digest = sha256_stream(stream)
                checks.append({
                    'source': source_name,
                    'archive': archive_name,
                    'sourceSha256': source_digest,
                    'packageSha256': packaged_digest,
                    'passed': bool(source_digest) and source_digest == packaged_digest,
                })
            for source_tree_name, archive_tree_name in (source_trees or {}).items():
                source_tree = root_path(source_tree_name, root)
                archive_prefix = archive_tree_name.rstrip('/') + '/'
                expected = {}
                if source_tree.is_dir():
                    for source in sorted(path for path in source_tree.rglob('*') if path.is_file()):
                        relative = source.relative_to(source_tree).as_posix()
                        expected[archive_prefix + relative] = source
                packaged = {
                    name for name in normalized_names
                    if name.startswith(archive_prefix) and not name.endswith('/')
                }
                mismatches = []
                for archive_name, source in expected.items():
                    packaged_name = normalized_names.get(archive_name)
                    if not packaged_name:
                        mismatches.append(f'missing:{archive_name}')
                        continue
                    with source.open('rb') as source_stream, archive.open(packaged_name) as package_stream:
                        if sha256_stream(source_stream) != sha256_stream(package_stream):
                            mismatches.append(f'hash:{archive_name}')
                mismatches.extend(f'extra:{name}' for name in sorted(packaged - set(expected)))
                checks.append({
                    'sourceTree': source_tree_name,
                    'archiveTree': archive_tree_name,
                    'files': len(expected),
                    'mismatches': mismatches,
                    'passed': source_tree.is_dir() and not mismatches,
                })
    except (OSError, zipfile.BadZipFile):
        return [{'package': package.name, 'passed': False, 'error': 'invalid_zip'}]
    return checks


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
        except (urllib.error.URLError, TimeoutError, http.client.HTTPException, ConnectionError):
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
            digest = sha256_stream(stream)
    checks.append({'package': package.name, 'sha256': digest, 'passed': digest == manifest['package']['sha256']})
    source_checks = check_package_sources(
        package,
        manifest['package']['sourceFiles'],
        source_trees=manifest['package']['sourceTrees'],
    )
    checks.append({
        'packageSources': source_checks,
        'passed': bool(source_checks) and all(item['passed'] for item in source_checks),
    })
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
