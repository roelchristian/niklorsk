"""Source-only checks for the dictionary; no TeX installation is required."""
import csv
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'makefile').read_text().split('define _NIKLORSK_BUILD_SOURCE\n', 1)[1].split('\nendef', 1)[0]
build = types.ModuleType('niklorsk_build')
build.__file__ = str(ROOT / 'codex' / 'build.py')
exec(compile(source, str(ROOT / 'makefile'), 'exec'), build.__dict__)


class VocabularyTests(unittest.TestCase):
    def setUp(self):
        self.rows = build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
        self.verbs = {r['lemma']: r for r in self.rows if r['partofspeech'] == 'v'}

    def test_citation_forms(self):
        self.assertEqual(len(self.rows), 488)
        self.assertEqual(len(self.verbs), 115)
        special = {'ö': 'ös', 'går': 'gårs', 'vor': 'vors', 'lod': 'lods',
                   'igom': 'igoms', 'tage': 'tages', 'baus': 'bauses',
                   'mårs': 'mårses', 'skers': 'skerses', 'bra': 'brags',
                   'helbra': 'helbrags', 'få': 'fågs', 'kunda': 'kundags',
                   'sollna': 'sollnags', 'kanseler': 'kanselers'}
        for stem, infinitive in special.items():
            self.assertEqual(build.citation_form(self.verbs[stem]), infinitive)
        for row in self.rows:
            if row['partofspeech'] != 'v':
                self.assertEqual(build.citation_form(row), row['lemma'])
        keys = [build.dictionary_key(build.citation_form(r)) for r in self.rows]
        self.assertEqual(keys, sorted(keys))

    def test_rendered_headwords_and_irregular_links(self):
        with tempfile.TemporaryDirectory() as directory:
            stage = Path(directory)
            (stage / 'vocabulary').mkdir()
            (stage / 'vocabulary/vocabulary.csv').write_bytes((ROOT / 'vocabulary/vocabulary.csv').read_bytes())
            self.assertEqual(build.vocabulary(stage), 488)
            text = (stage / 'vocabulary/vocabulary.tex').read_text()
            for stem, row in self.verbs.items():
                head = r'\dictionaryentry{' + row['infinitive'] + '}'
                self.assertIn(head, text)
            for infinitive, target in [('ös', 'tab:verb-to-be'), ('gårs', 'tab:verb-to-be'), ('vors', 'tab:verb-there-is')]:
                entry = next(line for line in text.splitlines() if line.startswith(r'\dictionaryentry{' + infinitive + '}'))
                self.assertIn(r'See Table~\ref{' + target + '}', entry)

    def test_missing_infinitive_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'vocabulary.csv'
            row = dict(self.verbs['bra'], infinitive='')
            with path.open('w') as stream:
                writer = csv.DictWriter(stream, fieldnames=build.VOCABULARY_FIELDS, delimiter=';')
                writer.writeheader()
                writer.writerow(row)
            with self.assertRaisesRegex(build.BuildError, 'Missing infinitive'):
                build.read_vocabulary(path)


if __name__ == '__main__':
    unittest.main()
