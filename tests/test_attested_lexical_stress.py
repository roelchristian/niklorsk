"""Lexical metadata follows explicitly annotated forms, not inferred defaults."""
import unittest
from test_vocabulary import ROOT, build


class AttestedLexicalStressTests(unittest.TestCase):
    def test_attested_stress_is_recorded_without_inventing_accent(self):
        entries = {build.citation_form(r): r for r in
                   build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')}
        derivations = (ROOT / 'chapters/derivations.tex').read_text()
        # Citation, recorded syllable, display, independently annotated source form.
        forms = [
            ('hond', '1', 'hónd', 'hónd'),
            ('honding', '1', 'hónding', 'hónding'),
            ('grom', '1', 'gróm', 'gróm'),
            ('gromhæd', '1', 'grómhæd', 'grómˌhæd'),
            ('vædfør', '1', 'vǽdfør', 'vǽdˌfør'),
            ('hjaltygde', '1', 'hjáltygde', 'hjáltygde'),
            ('plastrum', '1', 'plástrum', 'plástˌrum'),
            ('snørbrug', '1', 'snǿrbrug', 'snǿrˌbrug'),
            ('rørdygg', '1', 'rǿrdygg', 'rǿrˌdygg'),
            ('brutal', '2', 'brutál', 'brutál'),
            ('normalisers', '3', 'normalísers', 'normalíser'),
            ('normaliserats', '3', 'normalíserats', 'normalíserats'),
            ('dramatisers', '3', 'dramatísers', 'dramatíser'),
            ('brutalitet', '4', 'brutalitét', 'brutalitét'),
            ('objektivitet', '5', 'objektivitét', 'objektivitét'),
        ]
        for citation, stress, display, source in forms:
            with self.subTest(citation=citation):
                row = entries[citation]
                self.assertEqual(row['stress'], stress)
                self.assertEqual(build.stress_display(row), (display, ''))
                self.assertEqual(row['accent'], '')
                self.assertIn(r'\nkstress{' + source + '}', derivations)

    def test_explicit_compound_accent_is_recorded(self):
        entries = {build.citation_form(r): r for r in
                   build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')}
        phonology = (ROOT / 'chapters/phonology.tex').read_text()
        for citation, marked in [('ansløts', 'ánˌsløts'), ('ånvands', 'ǻnˌvands')]:
            self.assertEqual(entries[citation]['accent'], 'A1')
            self.assertIn(r'\nkaccent{' + marked + '}{A1}', phonology)
        prep = next(row for row in build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
                    if row['lemma'] == 'ån' and row['partofspeech'] == 'prep')
        self.assertEqual(prep['accent'], '')
