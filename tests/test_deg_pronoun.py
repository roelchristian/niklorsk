"""Source-only coverage for deg and the coordinator dåg."""
import csv
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DegPronounTests(unittest.TestCase):
    def test_lexical_identity_and_other_words(self):
        with (ROOT / 'vocabulary/vocabulary.csv').open() as f:
            rows = list(csv.DictReader(f, delimiter=';'))
        entries = [r for r in rows if r['lemma'] == 'deg']
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['partofspeech'], 'pron')
        self.assertEqual(entries[0]['inflection'], 'Q')
        self.assertEqual(entries[0]['definition'], 'who; also used as a relative pronoun')
        self.assertTrue(any(r['lemma'] == 'skæll' and r['definition'] == 'fish' for r in rows))

    def test_paradigm_and_syntax(self):
        nouns = (ROOT / 'chapters/nouns.tex').read_text()
        syntax = (ROOT / 'chapters/syntax.tex').read_text()
        self.assertIn(r'\nikp{deg}{who}', nouns)
        self.assertIn(r'\nikp{deger}{who (pl.)}', nouns)
        self.assertIn(r'\gla Deg vædar ægn?//', syntax)
        self.assertIn(r'\gla Deger vædar ægn?', syntax)
        self.assertIn(r'\gla Ag sattar, deg sløtar.//', syntax)
        self.assertIn(r'\gla Ag sattar, deg vædar Matti.//', syntax)
        self.assertIn(r'\gla En bliv, deg vædar ag i magasin, ø en dur sla Martin.//', syntax)

    def test_coordinator_dag(self):
        with (ROOT / 'vocabulary/vocabulary.csv').open() as f:
            rows = list(csv.DictReader(f, delimiter=';'))
        entries = [r for r in rows if r['lemma'] == 'dåg']
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['partofspeech'], 'conj')
        self.assertEqual(entries[0]['definition'], 'but')
        self.assertTrue(any(r['lemma'] == 'fjerdåge' for r in rows))
        self.assertTrue(any(r['lemma'] == 'fjerdåghæd' for r in rows))
        modifiers = (ROOT / 'chapters/modifiers.tex').read_text()
        self.assertIn(r'\nk{dåg sig}', modifiers)
        self.assertIn('Ag malm at Trøndhem dåg Matti malm at Rikke.', modifiers)
        self.assertIn('Ag bram vin exam dåg Matti svor', modifiers)
        paths = [ROOT / 'vocabulary/vocabulary.csv']
        for folder in ('chapters', 'texts'):
            paths.extend((ROOT / folder).glob('*.tex'))
            paths.extend((ROOT / folder).glob('*.csv'))
        for path in paths:
            self.assertIsNone(re.search(r'\bdårg\b', path.read_text()), path)

    def test_old_pronoun_absent_from_descriptive_sources(self):
        paths = [ROOT / 'vocabulary/vocabulary.csv']
        for folder in ('chapters', 'texts'):
            paths.extend((ROOT / folder).glob('*.tex'))
            paths.extend((ROOT / folder).glob('*.csv'))
        for path in paths:
            self.assertIsNone(re.search(r'\b(?:käll|kæll)(?:er)?\b', path.read_text(), re.IGNORECASE), path)


if __name__ == '__main__':
    unittest.main()
