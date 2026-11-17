"""Source-only regression checks for analytic finite aspect."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AspectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verbs = (ROOT / 'chapters/verbs.tex').read_text()
        cls.sources = [ROOT / 'README.md', *sorted((ROOT / 'chapters').glob('*.tex')),
                       *sorted((ROOT / 'texts').glob('*.tex')), ROOT / 'texts/corpus.csv']

    def test_obsolete_finite_aspect_absent(self):
        obsolete = ('hjaltatt', 'hjaltet', 'bratt', 'sollnatt', 'kanselatt',
                    'kanselert', 'tagett', 'bördutt', 'bängdutt', 'slämatt',
                    'stettatt', 'svoratt', 'pöljatt', 'hjeckatt', 'mykatt',
                    'bördet', 'vædatten', 'naurtet', 'enrammet', 'anslötet',
                    'anslötatt', 'voratt', 'vorst', 'normaˈlisatt')
        pattern = r'(?<!\w)(?:' + '|'.join(map(re.escape, obsolete)) + r')(?!\w)'
        for path in self.sources:
            text = path.read_text()
            with self.subTest(path=path.name):
                self.assertIsNone(re.search(pattern, text))
                self.assertNotIn(r'\Prog', text)
                # Perfect glossing remains only on retained perfect infinitives.
                self.assertIsNone(re.search(r'\\Perf(?:\{\})?\.(?!\\Inf)', text))
        self.assertIsNone(re.search(r'^\s*(?:Perfect|Progressive)\s*&', self.verbs, re.M))

    def test_perfect_auxiliary_and_invariable_participle(self):
        for form in ('får hjaltur', 'fårar hjaltur', 'fåräs hjaltur',
                     'Ag får så när hjaltur', 'får vorur i hjalts'):
            self.assertIn(form, self.verbs)
        self.assertIn('invariable', self.verbs)
        self.assertIn('fårar nortur Joann', (ROOT / 'chapters/texts.tex').read_text())

    def test_progressive_remains_infinitival(self):
        for form in ('ö i hjalts', 'vor i hjalts', 'vörs i hjalts',
                     'Ag ö så i hjalts', 'Ag ö så i mursts med op'):
            self.assertIn(form, self.verbs)

    def test_retained_nonfinite_and_mood_forms(self):
        for form in ('hjaltsk', 'bragsk', 'fjerdsk', 'hjaltade', 'brade',
                     'hjaltur', 'bragur', 'vorur', 'hjaltårs', 'brars',
                     'hjalter', 'brager', 'hjalte', 'brage'):
            self.assertIn(form, self.verbs)
        self.assertNotIn('braur', self.verbs)
        self.assertIn(r'\nikp{vorur}{been}', self.verbs)
        self.assertIn(r'\nikp{ur}{become}', self.verbs)

    def test_passive_is_preserved(self):
        self.assertIn(r'\nk{-(e)n}', self.verbs)
        self.assertIn('past participle agreeing with the subject in gender and number', self.verbs)
        self.assertIn('braren hel', self.verbs)
        self.assertIn(r'\label{sec:passive-voice}', self.verbs)


if __name__ == '__main__':
    unittest.main()
