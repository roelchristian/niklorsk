"""The recorded proper name preserves its spelling and unrecorded morphology."""
import tempfile
import unittest
from pathlib import Path
from test_vocabulary import ROOT, build


class JesuTests(unittest.TestCase):
    def test_lexical_entry_and_display(self):
        rows = build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
        matches = [row for row in rows if row['lemma'] == 'Jesu']
        self.assertEqual(len(matches), 1)
        row = matches[0]
        self.assertEqual((row['partofspeech'], row['inflection'], row['definition']),
                         ('n', 'N?', 'Jesus (proper name)'))
        for field in ('gender', 'plural', 'stress', 'accent', 'stress_anchor', 'infinitive'):
            self.assertEqual(row[field], '')
        with tempfile.TemporaryDirectory() as directory:
            stage = Path(directory)
            (stage / 'vocabulary').mkdir()
            (stage / 'vocabulary/vocabulary.csv').write_bytes(
                (ROOT / 'vocabulary/vocabulary.csv').read_bytes())
            build.vocabulary(stage)
            rendered = (stage / 'vocabulary/vocabulary.tex').read_text()
            self.assertIn(r'\dictionaryentry{Jesu}{}{noun}', rendered)
            self.assertNotIn('personal and place names are omitted', rendered)

    def test_source_name_and_english_translation(self):
        text = (ROOT / 'chapters/texts.tex').read_text()
        self.assertIn(r'\gla I man forst, Herodes en arnum sædar det møyrs sla Jesu,//', text)
        self.assertIn(r'\glb in that time Herod the ruler hear.\Pst{} about fame of Jesus//', text)
        self.assertIn('the fame of Jesus', text)
