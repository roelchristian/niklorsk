"""Nominative plural nø remains distinct from oblique and possessive forms."""
import tempfile
import unittest
from pathlib import Path

from test_vocabulary import ROOT, build


class NoPronounTests(unittest.TestCase):
    def test_subject_and_unchanged_oblique_paradigm(self):
        nouns = (ROOT / 'chapters/nouns.tex').read_text()
        self.assertIn("Third person, pl. & `they' & \\nk{nø} & \\nk{nørn} & \\nk{nørne}", nouns)
        self.assertIn(r'The plural \nk{nø} is common to all genders.', nouns)
        self.assertIn(r'Weak \nk{nø}', nouns)
        self.assertNotIn(r'\nk{nør}', nouns)
        modifiers = (ROOT / 'chapters/modifiers.tex').read_text()
        self.assertIn(r'\nikp{nø}{they} & \nk{nør} & \nk{nører} & \nk{nøre} & \nk{nøra}', modifiers)
        self.assertIn(r'a subsequent reference uses plural \nk{nø}', modifiers)
        self.assertNotIn(r'\nikp{nør}{they}', modifiers)

    def test_dictionary_distinguishes_they_and_their(self):
        rows = build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
        entries = {row['lemma']: row for row in rows}
        self.assertEqual(entries['nø']['definition'], 'they')
        self.assertEqual(entries['nø']['inflection'], 'P')
        self.assertEqual(entries['nør']['definition'], 'their')
        self.assertEqual(entries['nør']['inflection'], 'Poss')
        for lemma in ('nø', 'nør'):
            self.assertEqual(entries[lemma]['partofspeech'], 'pron')
            self.assertEqual(entries[lemma]['stress'], '')
            self.assertEqual(entries[lemma]['accent'], '')
        # These unrelated lexical items must not lose their final r.
        for lemma, definition in [('nørs', 'never'), ('snør', 'beach'), ('snørbrug', 'beach house')]:
            self.assertEqual(entries[lemma]['definition'], definition)
        with tempfile.TemporaryDirectory() as directory:
            stage = Path(directory)
            (stage / 'vocabulary').mkdir()
            (stage / 'vocabulary/vocabulary.csv').write_bytes((ROOT / 'vocabulary/vocabulary.csv').read_bytes())
            build.vocabulary(stage)
            rendered = (stage / 'vocabulary/vocabulary.tex').read_text()
            self.assertIn(r'\dictionaryentry{nø}', rendered)
            self.assertIn(r'\dictionaryentry{nør}', rendered)
