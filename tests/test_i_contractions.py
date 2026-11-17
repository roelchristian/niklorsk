"""Definite article contractions preserve their dative gender/number distinctions."""
import unittest
from test_vocabulary import build, ROOT


class IContractionTests(unittest.TestCase):
    def test_contraction_paradigm(self):
        nouns = (ROOT / 'chapters/nouns.tex').read_text()
        for article, form, category in (
            ('om', 'im', 'Masculine singular'),
            ('der', 'ir', 'Feminine singular'),
            ('egn', 'ing', 'Neuter singular'),
            ('dæ', 'idæ', 'Plural, all genders'),
        ):
            self.assertIn(r'\nk{i} + \nk{' + article + r'} & \nk{' + form + '} & ' + category, nouns)
        self.assertIn(r'\label{tab:i-article-contractions}', nouns)
        self.assertIn(r'\label{sec:article-contraction}', nouns)
        self.assertIn(r'\nikp{atta fjeltt}{to the party}', nouns)

    def test_examples_match_lexical_gender_and_number(self):
        rows = build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
        nouns = {r['lemma']: r for r in rows if r['partofspeech'] == 'n'}
        for lemma, gender in [('kung', 'm'), ('brug', 'f'), ('magasin', 'n')]:
            self.assertEqual(nouns[lemma]['gender'], gender)
        self.assertEqual(nouns['afte']['inflection'], 'N-n')
        text = (ROOT / 'chapters/nouns.tex').read_text()
        for form in ('im kung', 'ir brug', 'ing magasin', 'idæ aften',
                     'ir banger brug', 'idæ banga aften'):
            self.assertIn(form, text)

    def test_bare_and_infinitival_i_preserved(self):
        modifiers = (ROOT / 'chapters/modifiers.tex').read_text()
        verbs = (ROOT / 'chapters/verbs.tex').read_text()
        for phrase in ('i brug', 'i kung', 'i Malmö'):
            self.assertIn(phrase, modifiers)
        self.assertIn('Ag ö i hjalts en afte', verbs)
        rows = build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
        preposition = next(r for r in rows if r['lemma'] == 'i' and r['partofspeech'] == 'prep')
        self.assertIn('im, ir, ing, idæ', preposition['definition'])


if __name__ == '__main__':
    unittest.main()
