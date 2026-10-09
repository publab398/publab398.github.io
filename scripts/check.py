#!/usr/bin/env python3
"""Check generated routes, local assets, fragments and basic page metadata."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1] / '_site'


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.refs = []
        self.ids = set()
        self.h1 = 0
        self.title = False
        self.lang = False
        self.description = False
        self.errors = []
        self.feed(source)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.errors.append(f'duplicate id: {attrs["id"]}')
            self.ids.add(attrs['id'])
        self.h1 += tag == 'h1'
        self.title |= tag == 'title'
        self.lang |= tag == 'html' and attrs.get('lang') == 'ja'
        self.description |= bool(tag == 'meta' and attrs.get('name') == 'description' and attrs.get('content'))
        if tag == 'img' and not attrs.get('alt'):
            self.errors.append('image missing alt text')
        for key in ('href', 'src'):
            if key in attrs:
                self.refs.append(attrs[key])


def main():
    pages = {path: Document(path.read_text(encoding='utf-8')) for path in ROOT.rglob('*.html')}
    if not pages:
        raise SystemExit('No pages found. Run scripts/build.py first.')
    errors = []
    references = 0
    for path, doc in pages.items():
        label = path.relative_to(ROOT).as_posix()
        errors.extend(f'{label}: {error}' for error in doc.errors)
        if doc.h1 != 1 or not doc.title or not doc.lang or not doc.description:
            errors.append(f'{label}: expected one h1, title, lang=ja and description')
        route = '/' + label.removesuffix('index.html') if path.name == 'index.html' else '/' + label
        for ref in doc.refs:
            resolved = urlsplit(urljoin('https://publab398.github.io' + route, ref))
            if resolved.scheme not in ('http', 'https') or resolved.netloc != 'publab398.github.io':
                continue
            references += 1
            target = ROOT / unquote(resolved.path).lstrip('/')
            if target.is_dir():
                target /= 'index.html'
            if not target.is_file():
                errors.append(f'{label}: missing target {ref}')
            elif resolved.fragment and target in pages and unquote(resolved.fragment) not in pages[target].ids:
                errors.append(f'{label}: missing fragment {ref}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Checked {len(pages)} pages, {references} local references: OK')


if __name__ == '__main__':
    main()
