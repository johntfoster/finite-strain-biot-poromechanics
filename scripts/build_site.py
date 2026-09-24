#!/usr/bin/env python3
"""Build and check a self-contained Pages site with the matching source files."""
from __future__ import annotations

import html
import os
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import parse_qs, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.agent-runtime/site'


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.ids = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.ids.update([attrs['id']] if 'id' in attrs else [])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])


def source_path(value, root=ROOT):
    """Resolve a viewer path without allowing URLs or repository escape."""
    if value.startswith('../'):
        value = value[3:]
    relative = Path(value)
    if urlsplit(value).scheme or relative.is_absolute() or '..' in relative.parts:
        raise ValueError(f'Unsafe source path: {value}')
    path = root / relative
    if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Missing or external source: {value}')
    return path


def source_link(path, label=None):
    relative = path.relative_to(ROOT).as_posix()
    return f'<a href="source.html?f={relative}">{html.escape(label or relative)}</a>'


def registered_objects(root=ROOT):
    """Map registered class names to source, including shared source files."""
    return {name: path for path in (root/'moose_app/src').rglob('*.C')
            for name in re.findall(r'registerMooseObject\s*\(\s*"[^"]+"\s*,\s*(\w+)\s*\)',
                                   path.read_text())}


def check_production_balances(root=ROOT):
    """Keep the coupled publication inputs on the conservative balance kernels."""
    required = {'ReferenceMomentum', 'ReferenceFluidMass'}
    retired = {'ADReferenceSolidMomentum', 'ADReferenceMaterialStorageRateTerm',
                'ADReferenceComponentFluxTerm'}
    for name in ('mandel_implicit_biot/mandel_water_q2_q1.i',
                 'poroplastic_mandel/compression.i'):
        deck = root/'moose_app/test/tests'/name
        selected = set(re.findall(r'^\s*type\s*=\s*(\w+)', deck.read_text(), re.M))
        if not required <= selected or retired & selected:
            raise ValueError(f'{name}: production inputs must use the conservative balance kernels')


def examples_catalog():
    sections = ['<section class="section"><h2>Headers and shared utility</h2><ul>']
    sections += [f'<li>{source_link(p)}</li>' for p in sorted((ROOT/'moose_app/include').rglob('*.h'))]
    sections.append('</ul></section><section class="section" id="examples"><h2>All example and test inputs</h2>')
    sections.append('<p>Each input links to the local implementations it selects. Framework objects are supplied by the pinned MOOSE checkout. Inputs using <code>!include</code> also link to their base input. Run the test groups with <code>make test</code>; full publication calculations use the targets on the reproduction page.</p><ul>')
    objects = registered_objects()
    for deck in sorted((ROOT/'moose_app/test/tests').rglob('*.i')):
        content = deck.read_text()
        selected = sorted(set(re.findall(r'^\s*type\s*=\s*[\'\"]?(\w+)', content, re.M)))
        links = [source_link(objects[name], name) for name in selected if name in objects]
        for include in re.findall(r'^\s*!include\s+(\S+)', content, re.M):
            path = (deck.parent/include).resolve()
            if not path.is_file() or not path.is_relative_to(ROOT):
                raise ValueError(f'Invalid include in {deck}: {include}')
            links.append(source_link(path, 'included '+path.name))
        test = deck.parent/'tests'
        if test.is_file():
            links.append(source_link(test, 'test specification'))
        sections.append(f'<li>{source_link(deck)}<br>'+ ' · '.join(links)+'</li>')
    sections.append('</ul></section><section class="section"><h2>Verification and figure scripts</h2><ul>')
    for folder in ('scripts', 'validation/scripts'):
        sections += [f'<li>{source_link(p)}</li>' for p in sorted((ROOT/folder).glob('*.py'))]
    sections.append('</ul></section>')
    return '\n'.join(sections)


def check_links(site, sources=False):
    count = 0
    for page in sorted(site.glob('*.html')):
        for link in Links(page.read_text()).links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                continue
            target = (page.parent/unquote(parsed.path)).resolve() if parsed.path else page.resolve()
            if not target.is_relative_to(site.resolve()) or not target.is_file():
                raise ValueError(f'{page.name}: broken link {link}')
            if parsed.fragment and target.suffix == '.html':
                if unquote(parsed.fragment) not in Links(target.read_text()).ids:
                    raise ValueError(f'{page.name}: missing anchor {link}')
            if parsed.path == 'source.html':
                values = parse_qs(parsed.query).get('f', [])
                if values:
                    original = source_path(values[0])
                    if sources:
                        copied = site/'sources'/original.relative_to(ROOT)
                        if not copied.is_file() or copied.read_bytes() != original.read_bytes():
                            raise ValueError(f'{page.name}: missing or stale packaged source {link}')
            count += 1
    return count


def check_markdown_links(root=ROOT):
    if (root/'.git').exists():
        paths = subprocess.check_output(
            ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z', '*.md'],
            cwd=root, text=True).split('\0')
    else:
        # Publication archives contain source but no Git administrative files.
        paths = []
        excluded = {'.git', '.agent-runtime', 'build', '__pycache__', '.agent',
                    '.codex', '.claude', '.opencode'}
        for directory, folders, files in os.walk(root, followlinks=False):
            folders[:] = [name for name in folders if name not in excluded]
            paths.extend(str((Path(directory)/name).relative_to(root))
                         for name in files if name.endswith('.md'))
    count = 0
    for name in set(paths) - {''}:
        page = root/name
        if not page.is_file():
            continue
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', page.read_text()):
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (page.parent/unquote(parsed.path)).resolve()
            if not target.is_relative_to(root.resolve()) or not target.exists():
                raise ValueError(f'{name}: broken Markdown link {link}')
            count += 1
    return count


def build():
    markdown_count = check_markdown_links()
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    shutil.copytree(ROOT/'docs', OUTPUT)
    catalog = OUTPUT/'moose-catalog.html'
    catalog.write_text(catalog.read_text().replace('<!-- GENERATED EXAMPLE CATALOG -->', examples_catalog()))
    for page in OUTPUT.glob('*.html'):
        for link in Links(page.read_text()).links:
            parsed = urlsplit(link)
            if parsed.path != 'source.html':
                continue
            values = parse_qs(parsed.query).get('f', [])
            if not values:
                continue
            original = source_path(values[0])
            destination = OUTPUT/'sources'/original.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original, destination)
    # The viewer's default must work even without a query string.
    default = OUTPUT/'sources/moose_app/src/main.C'
    default.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT/'moose_app/src/main.C', default)
    (OUTPUT/'.nojekyll').touch()
    count = check_links(OUTPUT, sources=True)
    objects = registered_objects()
    local_objects = set(objects)
    check_production_balances()
    all_selected = set()
    for deck in (ROOT/'moose_app/test/tests').rglob('*.i'):
        all_selected.update(re.findall(r'^\s*type\s*=\s*(\w+)', deck.read_text(), re.M))
    unused = local_objects - all_selected
    if unused:
        raise ValueError(f'Application objects lack a retained input: {sorted(unused)}')
    selected = set()
    for deck in (ROOT/'moose_app/test/tests/mandel_implicit_biot').glob('*.i'):
        selected.update(re.findall(r'^\s*type\s*=\s*(\w+)', deck.read_text(), re.M))
    documented = set(re.findall(r'(moose_app/src/[^"?]+/\w+\.C)',
                                (OUTPUT/'mandel.html').read_text()))
    expected = {objects[name].relative_to(ROOT).as_posix()
                for name in selected & local_objects}
    expected.add('moose_app/src/base/NonlinearBiotADApp.C')
    if documented != expected:
        raise ValueError(f'Mandel object links disagree with inputs: {documented ^ expected}')
    catalog_text = catalog.read_text()
    for source in (ROOT/'moose_app/src').rglob('*.C'):
        if source.relative_to(ROOT).as_posix() not in catalog_text:
            raise ValueError(f'Uncatalogued implementation: {source.relative_to(ROOT)}')
    print(f'PASS {count} local site links; every implementation and example catalogued')
    print(f'PASS {markdown_count} repository Markdown links')
    print('Site: .agent-runtime/site')


if __name__ == '__main__':
    build()
