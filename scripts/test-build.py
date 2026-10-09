#!/usr/bin/env python3
"""Regression checks for article recency, Markdown and asset cache invalidation."""
import datetime as dt
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import build


class BuildChecks(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.entries = self.root / 'content/game/features'
        self.entries.mkdir(parents=True)
        self.project = {'slug': 'game', 'name': 'Game'}
        self.root_patch = patch.object(build, 'ROOT', self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def write_entry(self, name, date, updated=None, draft=False):
        metadata = f'title = "{name}"\ndate = "{date}"\nsummary = "Summary"\ndraft = {str(draft).lower()}\n'
        if updated is not None:
            metadata += f'updated = "{updated}"\n'
        (self.entries / f'{name}.md').write_text('+++\n' + metadata + '+++\nBody', encoding='utf-8')

    def test_local_midnight_precedes_same_day_update(self):
        self.write_entry('new', '2026-10-10')
        self.write_entry('revised', '2026-10-09', '2026-10-10T01:32:04+09:00')
        self.write_entry('draft', '2026-10-11', draft=True)
        entries = build.load_entries(self.project, 'features')
        self.assertEqual([entry['title'] for entry in entries], ['revised', 'new'])
        row = build.entry_row(entries[0], True)
        self.assertIn('2026.10.10', row)
        self.assertIn('更新', row)

    def test_timezones_are_compared_by_instant(self):
        self.write_entry('earlier', '2026-10-09', '2026-10-10T02:00:00+09:00')
        self.write_entry('later', '2026-10-09', '2026-10-09T18:00:00+00:00')
        entries = build.load_entries(self.project, 'features')
        self.assertEqual(entries[0]['title'], 'later')

    def test_date_only_update_uses_site_timezone(self):
        self.write_entry('revised', '2026-10-09', '2026-10-10')
        entry = build.load_entries(self.project, 'features')[0]
        expected = dt.datetime(2026, 10, 10, tzinfo=build.SITE_ZONE).astimezone(dt.timezone.utc)
        self.assertEqual(entry['sort_date'], expected)

    def test_update_before_publication_is_rejected(self):
        self.write_entry('invalid', '2026-10-10', '2026-10-09')
        with self.assertRaisesRegex(ValueError, 'updated cannot precede date'):
            build.load_entries(self.project, 'features')

    def test_replaced_asset_has_new_url(self):
        asset = self.root / 'public/assets/example.png'
        asset.parent.mkdir(parents=True)
        asset.write_bytes(b'first')
        match = build.re.search(r'(src=")(/assets/[^"?]+)(")', 'src="/assets/example.png"')
        first = build.asset_url(match)
        asset.write_bytes(b'second')
        second = build.asset_url(match)
        self.assertNotEqual(first, second)
        self.assertIn(hashlib.sha256(b'second').hexdigest()[:12], second)

    def test_ffa_label_is_strong(self):
        path = Path(__file__).resolve().parents[1] / 'content/project-cdx/features/rules.md'
        body = path.read_text(encoding='utf-8').split('+++', 2)[2]
        self.assertIn('<strong>Free For All（FFA）</strong>', build.MD.render(body))


if __name__ == '__main__':
    unittest.main()
