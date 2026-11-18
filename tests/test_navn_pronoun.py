"""Masculine singular object navn is distinct from lexical nær and nærer."""
import re
import unittest
from test_vocabulary import ROOT, build


class NavnPronounTests(unittest.TestCase):
    def test_accusative_and_dative_paradigm(self):
        nouns = (ROOT / 'chapters/nouns.tex').read_text()
        self.assertIn("Third person, masc., sg. & `he' & \\nk{nu} & \\nk{navn} & \\nk{navn}", nouns)
        weak = nouns.split(r'\label{tab:weak-pronouns}', 1)[1].split(r'\end{table}', 1)[0]
        # The earlier object's exceptional weak vowel is not assigned to navn.
        self.assertNotIn(r'\nk{navn}', weak)
        self.assertNotIn(r'\ipa{nɛ}', weak)
        self.assertNotIn(r'\ipa{nɐ}', weak)

    def test_object_examples_and_binding(self):
        syntax = (ROOT / 'chapters/syntax.tex').read_text()
        verbs = (ROOT / 'chapters/verbs.tex').read_text()
        texts = (ROOT / 'chapters/texts.tex').read_text()
        for form in ('Ag vandar navn ån', 'Ag modar så navn hel',
                     'Matti brar navn men skæmd', 'Matti brar navn ja',
                     'Martin vædar navn i kung', 'og vædar Matti navn i kung'):
            self.assertIn(form, syntax)
        for form in ('Ag får så navn hjaltur', 'Andærs fall navn væds',
                     'Meg dægn navn dag begns', 'Ag igom navn ånvands',
                     'Ag igom så navn ånvands'):
            self.assertIn(form, verbs)
        self.assertIn('å løgtar navn, å klassar navn', texts)
        for source in (syntax, verbs, texts, (ROOT / 'chapters/nouns.tex').read_text()):
            self.assertIsNone(re.search(r'\bnær\b', source, re.IGNORECASE))

    def test_unrelated_lexemes_and_nominative_dictionary_entry(self):
        rows = build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
        entries = {row['lemma']: row for row in rows}
        self.assertEqual((entries['nær']['partofspeech'], entries['nær']['definition']),
                         ('adv', 'for a long time'))
        self.assertEqual((entries['nærer']['partofspeech'], entries['nærer']['definition']),
                         ('prep', 'before, in front of'))
        self.assertEqual((entries['nu']['partofspeech'], entries['nu']['inflection']), ('pron', 'P'))
        # Personal pronouns are cited under their nominative, not each case form.
        self.assertNotIn('navn', entries)
        modifiers = (ROOT / 'chapters/modifiers.tex').read_text()
        self.assertIn(r'\nikp{nær}{for a long time}', modifiers)
        self.assertIn(r'\nikp{nærann}{longer}', modifiers)
