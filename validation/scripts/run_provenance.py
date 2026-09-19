"""Observe the environment at execution time without recording machine paths."""
from datetime import datetime, timezone
from importlib import metadata
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import os

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            result.update(block)
    return result.hexdigest()


def observe(executable, command):
    """Call before a simulation; never infer the environment of an earlier run."""
    executable = Path(executable).resolve()
    packages = {}
    for name in ('numpy', 'scipy', 'sympy', 'pandas', 'matplotlib', 'pyyaml'):
        try:
            packages[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            packages[name] = None
    conda = {}
    for path in sorted((Path(sys.prefix)/'conda-meta').glob('*.json')):
        value = json.loads(path.read_text())
        if value['name'] in ('moose-dev', 'moose-libmesh', 'moose-tools', 'petsc', 'libmesh', 'openmpi'):
            conda[value['name']] = dict(version=value['version'], build=value.get('build'))
    framework = ROOT/os.environ.get('MOOSE_FRAMEWORK_PATH', '.agent-runtime/moose')
    result = subprocess.run(['git', '-C', str(framework), 'rev-parse', 'HEAD'],
                            capture_output=True, text=True)
    return dict(schema_version=1, captured_at_utc=datetime.now(timezone.utc).isoformat(),
                python=platform.python_version(), packages=packages, conda_packages=conda,
                framework_commit=result.stdout.strip() if result.returncode == 0 else None,
                executable=dict(path=executable.relative_to(ROOT).as_posix(), sha256=digest(executable)),
                command=[(Path(arg).name if Path(str(arg)).is_absolute()
                          and not str(arg).startswith(str(ROOT)+'/') else
                          str(arg).replace(str(ROOT)+'/', '')) for arg in command])


def complete(observed, outputs):
    """Attach output identities only after successful execution and checks."""
    if digest(ROOT/observed['executable']['path']) != observed['executable']['sha256']:
        raise RuntimeError('Application changed during simulation')
    return dict(observed, outputs={Path(p).resolve().relative_to(ROOT).as_posix(): digest(p)
                                   for p in outputs})
