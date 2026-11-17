"""Source regressions for finite separation and non-finite incorporation."""
import csv
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ParticleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verbs = (ROOT / 'chapters/verbs.tex').read_text()
        cls.syntax = (ROOT / 'chapters/syntax.tex').read_text()
        cls.sources = [ROOT / 'README.md', *sorted((ROOT / 'chapters').glob('*.tex')),
                       *sorted((ROOT / 'texts').glob('*.tex')), ROOT / 'texts/corpus.csv']

    def test_finite_paradigm_separates(self):
        table = self.verbs.split(r'\label{tab:anslot-inflection}', 1)[1].split(r'\end{table}', 1)[0]
        for form in ('sløt an', 'sløtar an', 'sløtæs an', 'sløtårs an',
                     'sløter an', 'sløte an', 'ansløts', 'ansløtsk',
                     'ansløtade', 'ansløtur'):
            with self.subTest(form=form):
                self.assertIn(r'\nk{' + form + '}', table)

    def test_clause_order_survives_separation(self):
        for example in ('Ag sædar, og sløtar Matti an.',
                        'Ag sædar, og sløtar Matti så an.'):
            self.assertIn(r'\gla ' + example + '//', self.syntax)
        self.assertIn('I kvett sløtar Matti an', self.verbs + self.syntax)
        self.assertIn('Ag inte sløtar an?', self.verbs)
        self.assertIn('Ag hvæd, efte Matti sløtar an', self.syntax)

    def test_nonfinite_particles_survive_negation_and_light_objects(self):
        for example in ('Ag igom ånvands en dyr', 'Ag igom nær ånvands',
                        'Ag igom så ånvands en dyr', 'Ag igom så nær ånvands',
                        'Ag får opmurstur eg hjålt', 'Ag får så opmurstur eg hjålt',
                        'Ag får så med opmurstur', 'Matti ø så ansløtur',
                        'Ag ø i opmursts eg hjålt', 'Ag ø så i opmursts med'):
            with self.subTest(example=example):
                self.assertIn(example, self.verbs)

    def test_passive_finite_and_infinitive_contrast(self):
        self.assertIn('En samm braren hel par brevet.', self.verbs)
        self.assertIn('Eg hjålt dægn opmurstsen', self.verbs)

    def test_old_positive_example_patterns_absent(self):
        # Stored lexical stems are not finite sentence forms and are deliberately
        # outside this source audit. Infinitive citation forms remain incorporated.
        obsolete = re.compile(r'(?<!\w)(?:(?:an|at|hel|hæt|ån)sløt(?:ar|æs|års|er)|opmurstar)(?!\w)')
        for path in self.sources:
            with self.subTest(path=path.name):
                text = path.read_text()
                self.assertIsNone(obsolete.search(text))
                for example in ('Matti ø så sløtur an', 'Ag får så murstur op',
                                'Ag får så med murstur op', 'Ag igom nær vands ån',
                                'Ag ø så i mursts med op'):
                    self.assertNotIn(example, text)

    def test_inseparable_prefixes_remain_attached(self):
        for form in ('enrammar', 'får enrammur', 'enramms', 'enrammen',
                     'Ag enramm så med', 'Enramme med!'):
            self.assertIn(form, self.verbs)

    def test_incorporated_lexical_citations_preserved(self):
        with (ROOT / 'vocabulary/vocabulary.csv').open() as stream:
            rows = {r['lemma']: r for r in csv.DictReader(stream, delimiter=';')}
        for lemma, infinitive in [('ansløt', 'ansløts'), ('opmurst', 'opmursts'),
                                  ('ånvand', 'ånvands'), ('helbra', 'helbrags')]:
            self.assertEqual(rows[lemma]['infinitive'], infinitive)
            self.assertIn('Sep', rows[lemma]['inflection'])


if __name__ == '__main__':
    unittest.main()
