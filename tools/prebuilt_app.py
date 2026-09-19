#!/usr/bin/env python3
"""Reuse the image application only when its complete build inputs match."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs(root):
    paths = set()
    source_suffixes = {'.C', '.c', '.cc', '.cpp', '.h', '.hh', '.hpp', '.tcc', '.inc'}
    for pattern in ('moose_app/src/**/*', 'moose_app/include/**/*',
                    'moose_app/test/src/**/*', 'moose_app/test/include/**/*'):
        paths.update(p for p in root.glob(pattern)
                     if p.is_file() and p.suffix in source_suffixes)
    paths.update(p for p in root.glob('moose_app/patches/**/*') if p.is_file())
    paths.update(root/p for p in (
        'moose_app/Makefile', 'tools/setup_reproduction.sh', '.devcontainer/Dockerfile',
        '.agent/shared/skills/setup-moose-conda/scripts/moose_conda_env.sh'))
    return {str(p.relative_to(root)): digest(p) for p in sorted(paths)}


def reusable(root, image):
    manifest = image/'.agent-runtime/prebuilt-app.json'
    if not manifest.is_file():
        return False
    record = json.loads(manifest.read_text())
    executable = image/'moose_app/nonlinear_biot_ad-opt'
    return (record['inputs'] == inputs(root) and executable.is_file()
            and digest(executable) == record['executable_sha256']
            and (root/'.agent-runtime/moose').resolve() ==
                (image/'.agent-runtime/moose').resolve())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('record', 'use'))
    args = parser.parse_args()
    executable = ROOT/'moose_app/nonlinear_biot_ad-opt'
    if args.action == 'record':
        record = dict(inputs=inputs(ROOT), executable_sha256=digest(executable))
        (ROOT/'.agent-runtime/prebuilt-app.json').write_text(json.dumps(record, indent=2)+'\n')
        return 0
    image_path = os.environ.get('BIOT_IMAGE_ROOT')
    if not image_path:
        return 1
    image = Path(image_path)
    compatible = (os.environ.get('MOOSE_CONDA_ENV', 'moose') == 'moose'
                  and os.environ.get('MOOSE_FRAMEWORK_PATH', '.agent-runtime/moose') == '.agent-runtime/moose')
    if compatible and reusable(ROOT, image):
        if ROOT != image:
            if executable.exists() and digest(executable) != digest(image/'moose_app/nonlinear_biot_ad-opt'):
                return 1  # Preserve a locally built executable for its normal build.
            executable.unlink(missing_ok=True)
            # Keep a local executable path for run provenance. Its library paths
            # continue to refer to the fixed, precompiled image installation.
            shutil.copy2(image/'moose_app/nonlinear_biot_ad-opt', executable)
        print('Using source-matched application from the tested container image')
        return 0
    if executable.is_symlink() and executable.resolve() == image/'moose_app/nonlinear_biot_ad-opt':
        executable.unlink()
    print('Application inputs differ from the image; building the current checkout')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
