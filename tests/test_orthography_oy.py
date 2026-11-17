"""The öy spelling retains its diphthong and lexical identities."""
import re
import unittest
from pathlib import Path
from test_vocabulary import build, ROOT

class OrthographyOyTests(unittest.TestCase):
    def test_lexical_spellings_and_citation_forms(self):
        rows = build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
        by_lemma = {r['lemma']: r for r in rows}
        expected = {'öygig': 'often', 'öyto': 'car', 'böys': 'to kill',
                    'göyps': 'right now', 'möyg': 'friend', 'möyrs': 'fame',
                    'möys': 'happy', 'möyshæd': 'happiness', 'möysegs': 'happily',
                    'nöyp': 'to snow', 'nöyrt': 'to seize', 'röyk': 'to smoke', 'söygna': 'our'}
        for lemma, definition in expected.items():
            self.assertEqual(by_lemma[lemma]['definition'], definition)
        for lemma, infinitive in [('böys','böyses'), ('nöyp','nöyps'), ('nöyrt','nöyrts'), ('röyk','röyks')]:
            self.assertEqual(by_lemma[lemma]['infinitive'], infinitive)
        self.assertFalse(any('au' in r['lemma'] or 'au' in r.get('infinitive','') for r in rows))

    def test_phonetic_value_and_diphthong_nucleus(self):
        phonology = (ROOT / 'chapters/phonology.tex').read_text()
        self.assertIn('öy /œʏ̯/', phonology)
        self.assertNotIn('au /œʏ̯/', phonology)
        for word, index, expected in [('böyses','1','bö́yses'),('böyses','2','böysés'),('Öyto','1','Ö́yto')]:
            self.assertEqual(build.stress_display(dict(lemma=word, infinitive='',stress=index,stress_anchor='')), (expected,''))
        # An explicitly distinct hiatus sequence is not the old diphthong spelling.
        self.assertEqual(build.stress_display(dict(lemma='au',infinitive='',stress='2',stress_anchor='')), ('aú',''))

    def test_orthographic_example_consistency(self):
        sources = '\n'.join(p.read_text() for p in (ROOT / 'chapters').glob('*.tex'))
        self.assertIsNone(re.search(r'\b(?:auto|bauses|maug|maugen|maus|saugna|rauks|daussur)\b', sources, re.I))
        self.assertIn(r'\nk{öy} $\rightarrow$ \nk{o}', sources)
