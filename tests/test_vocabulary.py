"""Source-only checks for the dictionary; no TeX installation is required."""
import csv
import re
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
        self.assertEqual(len(self.rows), 508)
        self.assertEqual(len(self.verbs), 116)
        special = {'ø': 'vors', 'går': 'gårs', 'får': 'fårs',
                   'igom': 'igoms', 'tage': 'tages', 'bøys': 'bøyses',
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
            self.assertEqual(build.vocabulary(stage), 508)
            text = (stage / 'vocabulary/vocabulary.tex').read_text()
            for stem, row in self.verbs.items():
                head = r'\dictionaryentry{' + build.stress_display(row)[0] + '}'
                self.assertIn(head, text)
            self.assertEqual(text.count(r'\dictionaryentry{vors}'), 1)
            self.assertNotIn(r'\dictionaryentry{øs}', text)
            self.assertNotIn(r'\dictionaryentry{vor}', text)
            entry = next(line for line in text.splitlines() if line.startswith(r'\dictionaryentry{slǿts}'))
            self.assertIn(r'Perfect with \nk{vors}', entry)
            entry = next(line for line in text.splitlines() if line.startswith(r'\dictionaryentry{læts}'))
            self.assertIn('bounded-motion construction', entry)
            for infinitive, target in [('vors', 'tab:verb-to-be'), ('gårs', 'tab:verb-to-be')]:
                entry = next(line for line in text.splitlines() if line.startswith(r'\dictionaryentry{' + infinitive + '}'))
                self.assertIn(r'See Table~\ref{' + target + '}', entry)

    def test_unified_copula(self):
        copulas = [row for row in self.verbs.values() if row['infinitive'] == 'vors']
        self.assertEqual(len(copulas), 1)
        self.assertEqual(copulas[0]['lemma'], 'ø')
        self.assertEqual(copulas[0]['inflection'], 'V-be')
        self.assertNotIn('vor', self.verbs)
        self.assertNotIn('øs', [row['infinitive'] for row in self.verbs.values()])
        self.assertNotIn('V-ex', build.INFLECTION_GROUPS)
        self.assertEqual(self.verbs['går']['infinitive'], 'gårs')

    def test_have_lexeme(self):
        have = [row for row in self.rows if row['definition'].split(';')[0] == 'to have']
        self.assertEqual(len(have), 1)
        self.assertEqual(have[0]['lemma'], 'får')
        self.assertEqual(have[0]['infinitive'], 'fårs')
        self.assertEqual(have[0]['inflection'], 'V-I')
        self.assertIn('perfect auxiliary', have[0]['definition'])
        self.assertNotIn('bærg', self.verbs)
        self.assertNotIn('lod', self.verbs)
        self.assertEqual(self.verbs['få']['infinitive'], 'fågs')
        self.assertEqual(self.verbs['få']['definition'], 'to drive')
        for folder in ('chapters', 'texts'):
            for path in (ROOT / folder).glob('*.tex'):
                self.assertIsNone(re.search(r'\b(?:bärgs?|lods?|lodar)\b', path.read_text()), path)
        nouns = (ROOT / 'chapters/nouns.tex').read_text()
        self.assertIn('Nu får øyto?', nouns)
        self.assertIn(r'\nk{fårs leder}', nouns)
        self.assertIn(r'\nk{fågs øyto}', nouns)
        self.assertIn('Læse får de ngell', nouns)
        self.assertIn('i fårs så 18 spis', (ROOT / 'chapters/verbs.tex').read_text())
        self.assertIn('Konta Brok fårar', (ROOT / 'texts/middlemarch.tex').read_text())

    def test_perfect_auxiliary_metadata(self):
        be = {'sløts', 'mosts', 'malms', 'ansløts', 'atsløts',
              'helsløts', 'hætsløts', 'ånsløts'}
        self.assertEqual({r['infinitive'] for r in self.rows
                          if build.perfect_auxiliary(r) == 'BE'}, be)
        self.assertEqual(build.perfect_auxiliary(self.verbs['læt']), 'ALTERNATING')
        for lemma in ('får', 'ø', 'går', 'kom', 'sollna', 'bra', 'hjalt', 'kvint', 'få'):
            self.assertEqual(build.perfect_auxiliary(self.verbs[lemma]), 'HAVE')
        for row in self.rows:
            if row['partofspeech'] != 'v':
                self.assertEqual(build.perfect_auxiliary(row), '')
        self.assertEqual(self.verbs['læt']['inflection'], 'V-I|V-alt')
        self.assertEqual(self.verbs['ansløt']['inflection'], 'V-I|Sep')

    def test_auxiliary_validation_and_old_header(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'vocabulary.csv'
            def write(row, fields=build.VOCABULARY_FIELDS):
                with path.open('w') as stream:
                    writer = csv.DictWriter(stream, fieldnames=fields, delimiter=';', extrasaction='ignore')
                    writer.writeheader()
                    writer.writerow(row)
            for row in (dict(self.verbs['sløt'], perfect_auxiliary='MOTION'),
                        dict(next(r for r in self.rows if r['partofspeech'] == 'n'), perfect_auxiliary='BE')):
                write(row)
                with self.assertRaisesRegex(build.BuildError, 'Invalid perfect auxiliary'):
                    build.read_vocabulary(path)
            write(dict(self.verbs['hjalt'], perfect_auxiliary='HAVE'))
            self.assertEqual(build.perfect_auxiliary(build.read_vocabulary(path)[0]), 'HAVE')
            write(self.verbs['hjalt'], build.CITATION_VOCABULARY_FIELDS)
            self.assertEqual(build.perfect_auxiliary(build.read_vocabulary(path)[0]), 'HAVE')

    def test_conflicting_duplicate_auxiliary_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'vocabulary.csv'
            with path.open('w') as stream:
                writer = csv.DictWriter(stream, fieldnames=build.VOCABULARY_FIELDS, delimiter=';')
                writer.writeheader()
                writer.writerow(self.verbs['sløt'])
                writer.writerow(dict(self.verbs['sløt'], perfect_auxiliary='HAVE'))
            with self.assertRaisesRegex(build.BuildError, 'Conflicting perfect auxiliary'):
                build.read_vocabulary(path)

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

    def test_auxiliary_and_accent_metadata_coexist(self):
        motion = self.verbs['sløt']
        self.assertEqual(build.perfect_auxiliary(motion), 'BE')
        self.assertEqual(motion['stress'], '1')
        self.assertEqual(build.stress_display(motion)[0], 'slǿts')
        self.assertEqual(motion['accent'], 'A1')
        self.assertEqual(build.perfect_auxiliary(self.verbs['hjalt']), 'HAVE')
        self.assertEqual(self.verbs['hjalt']['accent'], 'A1')
        self.assertEqual(build.stress_display(self.verbs['hjalt'])[0], 'hjálts')


if __name__ == '__main__':
    unittest.main()
