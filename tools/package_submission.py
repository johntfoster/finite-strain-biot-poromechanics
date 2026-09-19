#!/usr/bin/env python3
"""Freeze a clean submission revision with source, evidence, and checksums."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', *args], cwd=cwd)


def archive_entries(root, prefix=''):
    with tarfile.open(fileobj=io.BytesIO(git('archive', 'HEAD', cwd=root))) as archive:
        for member in archive:
            if member.isfile():
                yield prefix+member.name, archive.extractfile(member).read()
            elif member.issym():
                # Preserve tracked symlinks as usable source files in ZIP readers.
                path = root/member.name
                if path.is_file():
                    yield prefix+member.name, path.read_bytes()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag', required=True)
    args = parser.parse_args()
    if not args.tag or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._' for c in args.tag):
        raise SystemExit('Use a simple release tag without path separators')
    if git('status', '--porcelain').strip():
        raise SystemExit('Commit all intended changes before packaging')
    subprocess.run(['make', 'paper', 'validate'], cwd=ROOT, check=True)
    output = ROOT/'.agent-runtime/submission'/args.tag
    output.mkdir(parents=True, exist_ok=False)
    entries = list(archive_entries(ROOT))
    entries += list(archive_entries(ROOT/'.agent/shared', '.agent/shared/'))
    with zipfile.ZipFile(output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries:
            archive.writestr(name, data)
    with zipfile.ZipFile(output/'manuscript-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries:
            if name.startswith(('paper/', 'figures/', 'submission/')) or name in (
                    'all.bib', '.latexmkrc', 'provenance/ai_use_statement.tex'):
                archive.writestr(name, data)
        archive.write(ROOT/'paper/build/main.bbl', 'paper/main.bbl')
    with zipfile.ZipFile(output/'supplement.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries:
            if name.startswith(('validation/', 'provenance/')):
                archive.writestr(name, data)
        for path in sorted((ROOT/'.agent-runtime/site').rglob('*')):
            if path.is_file():
                archive.write(path, 'website/'+str(path.relative_to(ROOT/'.agent-runtime/site')))
    # Keep the manuscript preview at its canonical path; package it directly.
    with zipfile.ZipFile(output/'manuscript-pdf.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.write(ROOT/'paper/build/main.pdf', 'main.pdf')
    subprocess.run(['git', 'bundle', 'create', str(output/'repository.bundle'), 'HEAD', 'main'], cwd=ROOT, check=True)
    metadata = dict(revision=git('rev-parse', 'HEAD').decode().strip(), tag=args.tag,
                    workflow_revision=git('rev-parse', 'HEAD', cwd=ROOT/'.agent/shared').decode().strip(),
                    container='ghcr.io/johntfoster/finite-strain-biot-poromechanics:sha-'+git('rev-parse', 'HEAD').decode().strip(),
                    evidence='Curated results and historical execution records; heavy studies are not rerun by ordinary CI.')
    (output/'release.json').write_text(json.dumps(metadata, indent=2)+'\n')
    checksums = ''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n'
                        for p in sorted(output.iterdir()) if p.is_file())
    (output/'SHA256SUMS').write_text(checksums)
    print(output.relative_to(ROOT))


if __name__ == '__main__':
    main()
