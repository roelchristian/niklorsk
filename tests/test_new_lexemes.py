"""Preserve the explicitly supplied botanical vocabulary and plural forms."""
import csv
import tempfile
import unittest
from pathlib import Path
from test_vocabulary import ROOT, build

class NewLexemeTests(unittest.TestCase):
    def test_exact_forms_and_unrecorded_metadata(self):
        rows = build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
        entries = {build.citation_form(r): r for r in rows}
        plurals = {'stöb':'stöbar', 'vadd':'vädder', 'sälv':'sälver',
                   'kalm':'kälmer', 'vacks':'väckser', 'torg':'torgen'}
        genders = {'stöb':'f', 'vadd':'f', 'sälv':'n',
                   'kalm':'m', 'vacks':'m', 'torg':'n'}
        for word, plural in plurals.items():
            self.assertEqual(entries[word]['plural'], plural)
            self.assertEqual(entries[word]['gender'], genders[word])
        for word in [*plurals, 'hjärs', 'fålg']:
            self.assertEqual(entries[word]['stress'], '')
            self.assertEqual(entries[word]['accent'], '')
        self.assertEqual(entries['hjärs']['inflection'], 'V?')
        self.assertEqual(entries['fålg']['inflection'], 'A?')
        self.assertEqual(entries['sälv']['inflection'], 'N-exp')
        with tempfile.TemporaryDirectory() as directory:
            stage = Path(directory)
            (stage/'vocabulary').mkdir()
            (stage/'vocabulary/vocabulary.csv').write_bytes((ROOT/'vocabulary/vocabulary.csv').read_bytes())
            build.vocabulary(stage)
            text = (stage/'vocabulary/vocabulary.tex').read_text()
            for plural in plurals.values():
                self.assertIn('Pl. \\nk{' + plural + '}.', text)

    def test_explicit_plural_validation(self):
        row = next(r for r in build.read_vocabulary(ROOT/'vocabulary/vocabulary.csv') if r['lemma']=='sälv')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'test.csv'
            def read(**changes):
                record = dict(row, **changes)
                with path.open('w') as f:
                    w=csv.DictWriter(f,fieldnames=build.VOCABULARY_FIELDS,delimiter=';')
                    w.writeheader();w.writerow(record)
                return build.read_vocabulary(path)
            for changes in ({'plural':''}, {'plural':'sälver|sälvar'}, {'partofspeech':'adj','inflection':'A?','gender':''}):
                with self.assertRaises(build.BuildError): read(**changes)
