"""The øy spelling retains its diphthong and lexical identities."""
import re
import unittest
from pathlib import Path
from test_vocabulary import build, ROOT

class OrthographyOyTests(unittest.TestCase):
    def test_lexical_spellings_and_citation_forms(self):
        rows = build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
        by_lemma = {r['lemma']: r for r in rows}
        expected = {'øygig': 'often', 'øyto': 'car', 'bøys': 'to kill',
                    'gøyps': 'right now', 'møyg': 'friend', 'møyrs': 'fame',
                    'møys': 'happy', 'møyshæd': 'happiness', 'møysegs': 'happily',
                    'nøyp': 'to snow', 'nøyrt': 'to seize', 'røyk': 'to smoke', 'søygna': 'our'}
        for lemma, definition in expected.items():
            self.assertEqual(by_lemma[lemma]['definition'], definition)
        for lemma, infinitive in [('bøys','bøyses'), ('nøyp','nøyps'), ('nøyrt','nøyrts'), ('røyk','røyks')]:
            self.assertEqual(by_lemma[lemma]['infinitive'], infinitive)
        self.assertFalse(any('au' in r['lemma'] or 'au' in r.get('infinitive','') for r in rows))

    def test_phonetic_value_and_diphthong_nucleus(self):
        phonology = (ROOT / 'chapters/phonology.tex').read_text()
        self.assertRegex(phonology, r'øy\s*&?\s*/œʏ̯/')
        self.assertNotIn('au /œʏ̯/', phonology)
        for word, index, expected in [('bøyses','1','bǿyses'),('bøyses','2','bøysés'),('Øyto','1','Ǿyto')]:
            self.assertEqual(build.stress_display(dict(lemma=word, infinitive='',stress=index,stress_anchor='')), (expected,''))
        # An explicitly distinct hiatus sequence is not the old diphthong spelling.
        self.assertEqual(build.stress_display(dict(lemma='au',infinitive='',stress='2',stress_anchor='')), ('aú',''))

    def test_orthographic_example_consistency(self):
        sources = '\n'.join(p.read_text() for p in (ROOT / 'chapters').glob('*.tex'))
        self.assertIsNone(re.search(r'\b(?:auto|bauses|maug|maugen|maus|saugna|rauks|daussur)\b', sources, re.I))
        self.assertIn(r'\nk{øy} $\rightarrow$ \nk{o}', sources)

class MergedVowelInventoryTests(unittest.TestCase):
    def test_merged_vowel_and_remaining_diphthong(self):
        source = (ROOT / 'chapters/phonology.tex').read_text()
        self.assertIn('æ & /æ/', source)
        self.assertIn('ø & /œ/', source)
        self.assertIn('øy & /œʏ̯/', source)
        self.assertNotIn('aɛ̯', source)
        self.assertNotIn('two phonemic diphthongs', source)

    def test_lexically_conditioned_participial_classes_preserved(self):
        source = (ROOT / 'chapters/verbs.tex').read_text()
        for form in ('væds', 'vødur', 'læts', 'lotur'):
            self.assertIn(form, source)
        self.assertIn('distinct lexical classes', source)
