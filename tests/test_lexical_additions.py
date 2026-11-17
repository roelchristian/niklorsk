"""Preserve supplied lexical forms without inferring pronunciation or valency."""
import tempfile
import unittest
from pathlib import Path
from test_vocabulary import ROOT, build


class LexicalAdditionTests(unittest.TestCase):
    def test_supplied_nouns_and_explicit_plurals(self):
        rows = build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
        expected = {
            'bli': ('m', 'N-zero', 'mountain', 'bli'),
            'ænsel': ('n', 'N-exp', 'donkey', 'ænsler'),
            'profet': ('m', 'N-ar', 'prophet', 'profetar'),
            'blind': ('n', 'N-ar', 'word', 'blindar'),
        }
        for lemma, values in expected.items():
            matches = [row for row in rows if row['lemma'] == lemma]
            self.assertEqual(len(matches), 1)
            row = matches[0]
            self.assertEqual(row['partofspeech'], 'n')
            self.assertEqual(tuple(row[key] for key in ('gender', 'inflection', 'definition', 'plural')), values)
            for key in ('stress', 'accent', 'stress_anchor'):
                self.assertEqual(row[key], '')
        with tempfile.TemporaryDirectory() as directory:
            stage = Path(directory)
            (stage / 'vocabulary').mkdir()
            (stage / 'vocabulary/vocabulary.csv').write_bytes((ROOT / 'vocabulary/vocabulary.csv').read_bytes())
            build.vocabulary(stage)
            rendered = (stage / 'vocabulary/vocabulary.tex').read_text()
            for lemma, (_, _, _, plural) in expected.items():
                entry = next(line for line in rendered.splitlines()
                             if line.startswith(r'\dictionaryentry{' + lemma + '}'))
                self.assertIn(r'Pl. \nk{' + plural + '}.', entry)

    def test_before_and_existing_synonyms(self):
        rows = build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
        matches = [row for row in rows if row['lemma'] == 'nærer']
        self.assertEqual(len(matches), 1)
        row = matches[0]
        self.assertEqual((row['partofspeech'], row['inflection'], row['definition']), ('adv', 'Adv0', 'before'))
        for key in ('gender', 'plural', 'stress', 'accent', 'stress_anchor'):
            self.assertEqual(row[key], '')
        self.assertTrue(any(row['lemma'] == 'smed' and row['definition'] == 'before' for row in rows))
        self.assertTrue(any(row['lemma'] == 'verb' and row['definition'] == 'word' for row in rows))
