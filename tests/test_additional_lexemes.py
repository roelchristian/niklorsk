"""Explicit lexical additions retain supplied inflection and unknown prosody."""
import tempfile
import unittest
from pathlib import Path
from test_vocabulary import ROOT, build


class AdditionalLexemeTests(unittest.TestCase):
    def test_supplied_lexical_data(self):
        rows = build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
        entries = {build.citation_form(row): row for row in rows}
        expected = {
            'øsks': ('øsk', 'v', '', 'V?', 'to open', ''),
            'røygs': ('røy', 'v', '', 'V-II', 'to be like, to resemble', ''),
            'båd': ('båd', 'n', 'f', 'N-exp', 'night', 'bøder'),
            'hons': ('hons', 'n', 'm', 'N-exp', 'oil', 'honsar'),
            'gøyld': ('gøyld', 'n', 'm', 'N-exp', 'door', 'gøyldar'),
        }
        for citation, values in expected.items():
            with self.subTest(citation=citation):
                row = entries[citation]
                self.assertEqual(tuple(row[k] for k in
                    ('lemma', 'partofspeech', 'gender', 'inflection', 'definition', 'plural')), values)
                for key in ('stress', 'accent', 'stress_anchor', 'perfect_auxiliary'):
                    self.assertEqual(row[key], '')
                self.assertEqual(sum(build.citation_form(r) == citation for r in rows), 1)
        self.assertEqual(entries['røygs']['inflection'], entries['brags']['inflection'])
        self.assertIn('røyks', entries)  # The distinct verb 'smoke' is unchanged.

    def test_dictionary_rendering(self):
        with tempfile.TemporaryDirectory() as directory:
            stage = Path(directory)
            (stage / 'vocabulary').mkdir()
            (stage / 'vocabulary/vocabulary.csv').write_bytes(
                (ROOT / 'vocabulary/vocabulary.csv').read_bytes())
            build.vocabulary(stage)
            rendered = (stage / 'vocabulary/vocabulary.tex').read_text()
            for word in ('øsks', 'røygs', 'båd', 'hons', 'gøyld'):
                self.assertIn(r'\dictionaryentry{' + word + '}{}', rendered)
            for plural in ('bøder', 'honsar', 'gøyldar'):
                self.assertIn(r'Pl. \nk{' + plural + '}.', rendered)
            self.assertNotIn('böder', rendered)
