"""The masculine singular subject nu preserves independent possessive forms."""
import re
import unittest
from test_vocabulary import ROOT, build


class NuPronounTests(unittest.TestCase):
    def test_personal_paradigm_and_lexicon(self):
        nouns = (ROOT / 'chapters/nouns.tex').read_text()
        self.assertIn("Third person, masc., sg. & `he' & \\nk{nu} & \\nk{navn} & \\nk{navn}", nouns)
        entries = {r['lemma']: r for r in build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')}
        self.assertEqual((entries['nu']['partofspeech'], entries['nu']['definition']), ('pron', 'he'))
        self.assertNotIn('nar', entries)

    def test_possessive_homograph_and_syllabification_preserved(self):
        modifiers = (ROOT / 'chapters/modifiers.tex').read_text()
        self.assertIn(r'\nikp{nu}{he} & \nk{næ} & \nk{nar} & \nk{næ} & \nk{na}', modifiers)
        phonology = (ROOT / 'chapters/phonology.tex').read_text()
        self.assertIn(r'\nkstress{magasín.nar}', phonology)

    def test_no_obsolete_subject_in_running_examples(self):
        for folder in ('chapters', 'texts'):
            for path in (ROOT / folder).rglob('*'):
                if path.suffix not in {'.tex', '.csv'}:
                    continue
                text = path.read_text()
                text = text.replace(r'\nk{nar}', '') if path.name == 'modifiers.tex' else text
                text = text.replace('magasín.nar', '') if path.name == 'phonology.tex' else text
                self.assertIsNone(re.search(r'\bnar\b', text, re.I), str(path))
