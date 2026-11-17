"""Recorded verb classes and citation forms remain mutually consistent."""
import unittest

from test_vocabulary import ROOT, build


class VerbLexiconAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verbs = {
            row['lemma']: row for row in
            build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
            if row['partofspeech'] == 'v'
        }

    def test_recorded_classes_have_matching_infinitives(self):
        # Validate recorded classes only: an unknown paradigm is not evidence
        # for assigning a class from the spelling of its citation form.
        for stem, row in self.verbs.items():
            codes = set(row['inflection'].split('|'))
            with self.subTest(stem=stem):
                if 'V-I' in codes or 'V-modal' in codes:
                    expected = stem + ('es' if stem.endswith('s') else 's')
                elif 'V-II' in codes:
                    expected = stem + 'gs'
                elif 'V-L' in codes:
                    expected = stem + 's'
                elif 'V-be' in codes:
                    expected = {'ø': 'vors', 'går': 'gårs'}[stem]
                else:
                    continue
                self.assertEqual(row['infinitive'], expected)

    def test_attested_particle_derivatives_retain_base_class(self):
        # Compare lexical pairs explicitly documented in the grammar, rather
        # than treating every initial particle-like string as a mobile prefix.
        pairs = {
            'anhveng': 'hveng', 'ansløt': 'sløt', 'atsløt': 'sløt',
            'helsløt': 'sløt', 'hætsløt': 'sløt', 'ånsløt': 'sløt',
            'helbra': 'bra', 'helmod': 'mod', 'opmurst': 'murst',
            'ånhjalt': 'hjalt', 'ånvand': 'vand',
        }
        for compound, base in pairs.items():
            with self.subTest(compound=compound):
                row = self.verbs[compound]
                base_row = self.verbs[base]
                self.assertIn('Sep', row['inflection'].split('|'))
                self.assertEqual(row['inflection'].split('|')[0],
                                 base_row['inflection'].split('|')[0])
                prefix = compound[:-len(base)]
                self.assertEqual(row['infinitive'], prefix + base_row['infinitive'])


if __name__ == '__main__':
    unittest.main()
