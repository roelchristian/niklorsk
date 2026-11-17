"""Nominal possession uses sla without a genitive ending."""
import tempfile
import unittest
from pathlib import Path
from test_vocabulary import ROOT, build


class SlaPossessionTests(unittest.TestCase):
    def test_no_genitive_construction_or_gloss(self):
        paths = list((ROOT / 'chapters').glob('*.tex')) + list((ROOT / 'texts').glob('*.tex'))
        for path in paths:
            text = path.read_text()
            self.assertNotIn(r'\Gen', text, path.name)
            self.assertNotIn('genitive', text.lower(), path.name)
            for form in ('Martint', 'Andærst', 'Jesust', 'Filipt', 'blivtes', 'skælltes', 'vætøt'):
                self.assertNotIn(form, text, path.name)
        self.assertNotIn('Genitives follow', (ROOT / 'makefile').read_text())

    def test_retained_case_and_pronominal_possession(self):
        nouns = (ROOT / 'chapters/nouns.tex').read_text()
        self.assertIn(r'\label{sec:nominal-case}', nouns)
        for form in ('om', 'der', 'egn', 'dæ', 'hamde', 'hamdær', 'hamda'):
            self.assertIn(form, nouns)
        self.assertIn('sla Martin', nouns)
        self.assertIn('sla Andærs', nouns)

    def test_vaerg_entry_and_rendered_plural(self):
        rows = build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
        matches = [r for r in rows if r['lemma'] == 'værg']
        self.assertEqual(len(matches), 1)
        near = [r for r in rows if r['lemma'] == 'hålla']
        self.assertEqual(len(near), 1)
        self.assertEqual((near[0]['partofspeech'], near[0]['definition']), ('adv', 'near'))
        row = matches[0]
        self.assertEqual((row['partofspeech'], row['gender'], row['plural']), ('n', 'm', 'værgen'))
        self.assertEqual(row['definition'], 'lord, master')
        self.assertEqual(row['stress'], '')
        self.assertEqual(row['accent'], '')
        with tempfile.TemporaryDirectory() as directory:
            stage = Path(directory)
            (stage / 'vocabulary').mkdir()
            (stage / 'vocabulary/vocabulary.csv').write_bytes((ROOT / 'vocabulary/vocabulary.csv').read_bytes())
            build.vocabulary(stage)
            text = (stage / 'vocabulary/vocabulary.tex').read_text()
            self.assertIn('værg', text)
            self.assertIn(r'Pl. \nk{værgen}.', text)
