#!/usr/bin/env python3
"""Check both directions of the manuscript/application equation inventory."""
from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]


def manuscript_labels(root):
    """Follow the canonical root; ignore comments and unrelated TeX files."""
    labels = {}
    visited = set()

    def visit(path):
        if path in visited:
            return
        visited.add(path)
        text = re.sub(r"(?<!\\)%[^\n]*", "", path.read_text())
        for environment, body in re.findall(
                r'\\begin\{(equation|align|gather)\}(.*?)\\end\{\1\}', text, re.S):
            if not re.search(r'\\label\{eq:[^}]+\}', body):
                raise ValueError(f"Unlabelled numbered display in {path.relative_to(root)}: {environment}")
        for number, line in enumerate(text.splitlines(), 1):
            for label in re.findall(r"\\label\{([^}]+)\}", line):
                if label in labels:
                    raise ValueError(f"Duplicate manuscript label: {label}")
                labels[label] = (path.relative_to(root).as_posix(), number)
        for command, target in re.findall(r"\\(paperinput|input|include)\{([^}#]+)\}", text):
            if not target.endswith('.tex'):
                target += '.tex'
            child = (root/'paper' if command == 'paperinput' else path.parent)/target
            visit(child)

    visit(root/'paper/main.tex')
    return labels


def audit(root=ROOT):
    labels = manuscript_labels(root)
    inventory = yaml.safe_load((root/'validation/equation_to_moose_map.yml').read_text())
    mappings = inventory['mappings'] + inventory['supporting_mappings']
    ids = [entry['id'] for entry in mappings]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate equation mapping ID')
    objects = {p.stem: p for folder in ('materials', 'kernels', 'postprocessors')
               for p in (root/'moose_app/src'/folder).glob('*.C')}
    tests = {name for path in (root/'moose_app/test/tests').rglob('tests')
             for name in re.findall(r'^\s*\[([^]/]+)\]', path.read_text(), re.M)}
    covered = set()
    mapped_objects = set()
    for entry in mappings:
        equations = entry['paper_equations']
        if not equations:
            raise ValueError(f"No equations in {entry['id']}")
        for label in equations:
            if label not in labels:
                raise ValueError(f"Stale manuscript label in {entry['id']}: {label}")
            covered.add(label)
        for name in entry.get('moose_objects', []) + entry.get('consumers', []):
            if name not in objects:
                raise ValueError(f"Unknown MOOSE object: {name}")
            mapped_objects.add(name)
        for name in entry.get('tests', []):
            if name not in tests:
                raise ValueError(f"Unknown regression in {entry['id']}: {name}")
        paths = list(entry.get('sources', []))
        paths += [entry[key] for key in ('source', 'verifier', 'independent_diagnostic',
                                        'refinement_diagnostic') if key in entry]
        for path in paths:
            if Path(path).is_absolute() or '..' in Path(path).parts or not (root/path).is_file():
                raise ValueError(f"Missing or nonportable traceability source: {path}")
    reference_sources = (list(objects.values())
                         + list((root/'moose_app/include').rglob('*.h'))
                         + list((root/'validation/scripts').glob('*.py')))
    for path in reference_sources:
        for label in re.findall(r'\beq:[a-zA-Z0-9_-]+', path.read_text()):
            if label not in labels:
                raise ValueError(f"Stale source equation reference in {path.relative_to(root)}: {label}")
    missing = {label for label in labels if label.startswith('eq:')} - covered
    if missing:
        raise ValueError(f"Unmapped manuscript equations: {sorted(missing)}")
    if set(objects) - mapped_objects:
        raise ValueError(f"Unmapped MOOSE objects: {sorted(set(objects) - mapped_objects)}")
    return labels, mappings, objects


if __name__ == '__main__':
    labels, mappings, objects = audit()
    print(f"PASS {sum(x.startswith('eq:') for x in labels)} equation labels, "
          f"{len(objects)} MOOSE objects, {len(mappings)} traceability groups")
