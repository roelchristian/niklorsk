"""Source-only regression checks for the unified copula."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CopulaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verbs = (ROOT / 'chapters/verbs.tex').read_text()

    def test_unified_paradigm(self):
        forms = {
            'Present': ('ö', 'I am'),
            'Past': ('vor', 'I was'),
            'Future': ('vörs', 'I will be'),
            'Conditional': ('års', 'I would be'),
            'Negative Conditional': ('voren', 'I would not be'),
            'Infinitive': ('vors', 'to be'),
            'Present participle': ('edde', 'being'),
            'Past participle': ('vorur', 'been'),
        }
        for category, (form, gloss) in forms.items():
            with self.subTest(category=category):
                self.assertIn(category + r' & \nikp{' + form + '}{' + gloss + '}', self.verbs)
        self.assertIn(r'\nikp{ur}{become}', self.verbs)
        self.assertIn(r'\nikp{är}{I became}', self.verbs)

    def test_obsolete_copula_forms_and_table_absent(self):
        sources = [ROOT / 'README.md', ROOT / 'makefile',
                   *sorted((ROOT / 'chapters').glob('*.tex')),
                   *sorted((ROOT / 'texts').glob('*.tex')),
                   ROOT / 'texts/corpus.csv', ROOT / 'vocabulary/vocabulary.csv']
        # av, är and ur remain independently valid as a preposition or forms of gårs.
        obsolete = re.compile(r'(?<![\w-])(?:ös|isk|voräs|vorems|vorade)(?!\w)', re.I)
        for path in sources:
            with self.subTest(path=path.name):
                text = path.read_text()
                self.assertIsNone(obsolete.search(text))
                self.assertNotIn('tab:verb-there-is', text)


if __name__ == '__main__':
    unittest.main()
