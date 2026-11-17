"""Lexical illustrations use documented forms and preserve recovered glosses."""
import unittest
from test_vocabulary import ROOT, build


class LexicalExampleAuditTests(unittest.TestCase):
    def test_cover_infinitive_keeps_its_documented_meaning(self):
        phonology = (ROOT / 'chapters/phonology.tex').read_text()
        self.assertIn(r'The infinitive \nikp{bængds}{cover}', phonology)
        self.assertIn(r'[\ipa{bæŋːs}]', phonology)
        self.assertIn('consonant-bearing stem [bænð]', phonology)
        row = next(row for row in build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
                   if row['infinitive'] == 'bængds')
        self.assertEqual(row['definition'], 'to cover')
        self.assertEqual(row['lemma'], 'bængds')
        self.assertEqual(row['inflection'], 'V?|V-stem')
        self.assertEqual(row['stress'], '')
        self.assertEqual(row['accent'], '')

    def test_coordination_uses_recorded_verbs(self):
        text = (ROOT / 'chapters/modifiers.tex').read_text()
        self.assertIn(r'\gla Ag bram vin exam dåg Matti svor.//', text)
        self.assertIn(r'\glb I study.\Pres{} for exam but Matti sleep.\Pres{}//', text)
        self.assertNotIn('Matti pølj', text)
        verbs = {row['lemma']: row for row in
                 build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
                 if row['partofspeech'] == 'v'}
        for stem, meaning in [('bram', 'to study'), ('svor', 'to sleep')]:
            self.assertEqual(verbs[stem]['definition'], meaning)
            self.assertEqual(verbs[stem]['infinitive'], stem + 's')


if __name__ == '__main__':
    unittest.main()
