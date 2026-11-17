"""Counted noun phrases use lexical plural forms and plural agreement."""
import re
import unittest
from test_vocabulary import build, ROOT


class NumeralAgreementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nouns = (ROOT / 'chapters/nouns.tex').read_text()
        cls.modifiers = (ROOT / 'chapters/modifiers.tex').read_text()

    def test_counted_noun_forms(self):
        for text in (self.nouns, self.modifiers):
            self.assertIn(r'\nikp{som aften}{two books}', text)
            self.assertIn(r'\nikp{som dyr}{two bears}', text)
        self.assertIn(r'\nikp{men afte}{one book}', self.nouns)
        self.assertIn(r'\nikp{menårød aften}{twenty-one books}', self.modifiers)
        self.assertIn(r'\nikp{somsmøler aften}{two hundred books}', self.modifiers)
        rows = build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
        nouns = {r['lemma']: r for r in rows if r['partofspeech'] == 'n'}
        self.assertEqual(nouns['afte']['inflection'], 'N-n')
        self.assertEqual(nouns['dyr']['inflection'], 'N-zero')
        # Cardinal one and quantifiers are not silently changed by this rule.
        self.assertIn(r'\nikp{dritte bliv}{a few men}', self.nouns)

    def test_agreement_examples(self):
        for example in ('som banga aften', 'Som aften ø banga',
                        'som hjalturen aften'):
            self.assertIn(example, self.modifiers)
        numeral_section = self.modifiers.split(r'\label{sec:numerals}', 1)[1]
        self.assertIn(r'\nk{nø}', numeral_section)
        self.assertIn(r'\ref{tab:personal-pronouns}', numeral_section)
        self.assertIn(r'\nk{banga}', self.modifiers)
        self.assertIn(r'\nk{hjalturen}', self.modifiers)
        # Agreement on counted phrases does not spread to the have-perfect.
        self.assertIn('the participle in the have-perfect is invariable', self.modifiers)

    def test_obsolete_numeral_singular_rule_absent(self):
        for path in [*sorted((ROOT / 'chapters').glob('*.tex')),
                     *sorted((ROOT / 'texts').glob('*.tex')),
                     ROOT / 'texts/corpus.csv']:
            text = path.read_text()
            with self.subTest(path=path.name):
                self.assertIsNone(re.search(r'\bsom afte\b', text, re.I))
                self.assertNotIn('counted noun remains singular', text)
                self.assertNotIn('Cardinal numerals precede a counted noun in its singular form', text)
                self.assertNotIn('After a numeral or quantifier, the noun has its singular form', text)


if __name__ == '__main__':
    unittest.main()
