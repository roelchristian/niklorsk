"""Source-only checks for direct, embedded and quoted interrogatives."""
import csv
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EmbeddedQuestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.syntax = (ROOT / 'chapters/syntax.tex').read_text()
        cls.verbs = (ROOT / 'chapters/verbs.tex').read_text()
        cls.phonology = (ROOT / 'chapters/phonology.tex').read_text()
        cls.embedded = cls.syntax.split(r'\label{sec:embedded-interrogatives}', 1)[1].split(r'\subsection{Direct quotation}', 1)[0]
        cls.quoted = cls.syntax.split(r'\label{sec:quoted-questions}', 1)[1].split(r'\section{Reflexive binding}', 1)[0]

    def test_polar_complements_and_matrix_force(self):
        for example in (
            'Ag hvæd, efte Matti får børdur någ.',
            'Meg inte hvæd, efte Matti får børdur någ?',
            'Meg hvæd, efte Matti får børdur någ?',
            'Ag hvæd, og får Matti børdur någ',
        ):
            self.assertIn(example, self.embedded)
        self.assertNotIn('Quoted questions require', self.syntax)
        self.assertIn('does not occur inside the interrogative complement', self.embedded)
        self.assertIn('Declarative complement clauses', self.syntax)
        # The rejected particle placement is discussion, never a positive example.
        self.assertNotIn(r'\gla Meg hvæd, efte Matti inte får', self.syntax)

    def test_negation_scope_pair(self):
        for example in (
            'Meg inte hvæd så, efte Matti får børdur någ?',
            'Meg inte hvæd, efte Matti får så børdur någ?',
        ):
            self.assertIn(r'\gla ' + example + '//', self.embedded)

    def test_content_question_order_and_quotation(self):
        self.assertIn(r'\gla Ag sattar, kæll sløtar.//', self.embedded)
        self.assertIn(r'\gla Ag sattar, kæll vædar Matti.//', self.embedded)
        self.assertIn('relative clause modifies a nominal antecedent', self.embedded)
        self.assertIn("\\gla Ag sattar: `Matti inte får børdur någ?'//", self.quoted)
        self.assertIn('reporting clause may remain declarative', self.quoted)

    def test_efte_senses_and_mood_are_distinct(self):
        with (ROOT / 'vocabulary/vocabulary.csv').open() as f:
            rows = list(csv.DictReader(f, delimiter=';'))
        entries = [row for row in rows if row['lemma'] == 'efte']
        self.assertEqual(len(entries), 1)
        self.assertEqual({s.strip() for s in entries[0]['definition'].split(';')}, {'if', 'whether'})
        self.assertIn('In conditional constructions it is required in the protasis', self.verbs)
        self.assertIn('takes the indicative by default', self.verbs)
        self.assertIn('independently licensed by the meaning of the embedded clause', self.verbs)
        self.assertIn(r'\gla Ag sortæs hamdær nyst, efte sortårs Matti de hamdær.//', self.verbs)

    def test_intonation_is_not_clause_scope(self):
        self.assertIn('without giving that complement an independent question contour', self.phonology)
        self.assertIn('its phonetic location does not determine the syntactic scope of interrogation', self.phonology)
        self.assertIn('Directly quoted questions retain the contours of independent questions', self.phonology)

    def test_new_interlinear_examples_align(self):
        pairs = re.findall(r'\\gla\s+(.*?)//\s*\\glb\s+(.*?)//', self.embedded + self.quoted, re.S)
        self.assertEqual(len(pairs), 7)
        for source, gloss in pairs:
            with self.subTest(example=source):
                self.assertEqual(len(source.split()), len(gloss.split()))
                self.assertNotIn(' if ', ' ' + gloss + ' ')


if __name__ == '__main__':
    unittest.main()
