"""Grapheme-safe editorial notation; no lexical phonology is inferred."""
import csv
import json
import tempfile
import unittest
import unicodedata
from pathlib import Path
from test_vocabulary import build, ROOT


def record(word, stress='', accent='', anchor=''):
    return dict(lemma=word, infinitive='', stress=stress, accent=accent, stress_anchor=anchor)


class AccentNotationTests(unittest.TestCase):
    def test_all_vowel_graphemes(self):
        for vowel, expected in zip('aeiouyæøå', ['á','é','í','ó','ú','ý','ǽ','ǿ','ǻ']):
            with self.subTest(vowel=vowel):
                actual, warning = build.stress_display(record(vowel, '1'))
                self.assertEqual(unicodedata.normalize('NFC', actual), unicodedata.normalize('NFC', expected))
                self.assertFalse(warning)
                self.assertEqual(build.stress_display(record(unicodedata.normalize('NFD', vowel), '1'))[0], actual)

    def test_nuclei_compounds_and_prefixes(self):
        for word, stress, expected in [('magasin','3','magasín'),('hjalts','1','hjálts'),
                                       ('tages','1','táges'),('afte','1','áfte'),
                                       ('bøyses','1','bǿyses'),('bøyses','2','bøysés'),
                                       ('situasion','3','situásion'),('enhjalts','2','enhjálts'),
                                       ('gætugs','2','gætúgs'),('ansløts','1','ánsløts')]:
            self.assertEqual(build.stress_display(record(word, stress)), (expected, ''))

    def test_unknown_not_invented_and_anchor_override(self):
        self.assertEqual(build.stress_display(record('afte'))[0], 'afte')
        self.assertIn('unrecorded', build.stress_display(record('afte'))[1])
        self.assertIn('stress_anchor', build.stress_display(record('afte', '3'))[1])
        self.assertEqual(build.stress_display(record('øy', '2', anchor='2'))[0], 'øý')
        self.assertIn('overrides', build.stress_display(record('øy', '2', anchor='2'))[1])
        with self.assertRaises(build.BuildError):
            build.stress_display(record('afte', '1', anchor='2'))

    def test_rendered_categories_and_data_independence(self):
        with tempfile.TemporaryDirectory() as directory:
            stage=Path(directory); (stage/'vocabulary').mkdir()
            source=ROOT/'vocabulary/vocabulary.csv'
            (stage/'vocabulary/vocabulary.csv').write_bytes(source.read_bytes())
            build.vocabulary(stage)
            rendered=(stage/'vocabulary/vocabulary.tex').read_text()
            for word, accent in [('magasín','A1'),('hjálts','A1'),('táges','A2'),('áfte','')]:
                self.assertIn('\\dictionaryentry{'+word+'}{'+accent+'}', rendered)
            self.assertNotIn('Superscripts number', rendered)
            rows=build.read_vocabulary(source)
            self.assertEqual([build.dictionary_key(build.citation_form(r)) for r in rows], sorted(build.dictionary_key(build.citation_form(r)) for r in rows))
            warnings=json.loads((stage/'vocabulary/notation_warnings.json').read_text())
            self.assertTrue(any('lexical accent unrecorded' in r['issues'] for r in warnings))
            self.assertTrue(all(c not in '¹²' for r in rows for c in build.citation_form(r)))
            # The inherited loan café retains its lexical spelling.
            by_word = {build.citation_form(r): r for r in rows}
            self.assertIn('magasin', by_word)
            self.assertIn('hjalts', by_word)
            self.assertIn('tages', by_word)
            self.assertIn('café', by_word)

    def test_surface_a0_is_not_a_lexical_category(self):
        rows=build.read_vocabulary(ROOT/'vocabulary/vocabulary.csv')
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'test.csv'
            with path.open('w') as stream:
                writer=csv.DictWriter(stream, fieldnames=build.VOCABULARY_FIELDS, delimiter=';')
                writer.writeheader(); writer.writerow(dict(rows[0], accent='A0'))
            with self.assertRaisesRegex(build.BuildError, 'surface category'):
                build.read_vocabulary(path)

    def test_accent_and_stress_metadata_validate_independently(self):
        rows = build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
        base = next(row for row in rows if row['lemma'] == 'afte')
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'vocabulary.csv'

            def read_variant(**changes):
                with source.open('w', encoding='utf-8', newline='') as stream:
                    writer = csv.DictWriter(stream, fieldnames=build.VOCABULARY_FIELDS, delimiter=';')
                    writer.writeheader()
                    writer.writerow(dict(base, **changes))
                return build.read_vocabulary(source)[0]

            # A documented category need not imply a recorded stress location.
            row = read_variant(stress='', accent='A2', stress_anchor='')
            self.assertEqual(row['accent'], 'A2')
            self.assertEqual(build.stress_display(row)[0], 'afte')
            self.assertIn('unrecorded', build.stress_display(row)[1])
            for changes in ({'stress': '0'}, {'stress': '１'},
                            {'stress': '', 'stress_anchor': '1'},
                            {'stress': '1', 'stress_anchor': '0'},
                            {'stress': '1', 'stress_anchor': '2'},
                            {'stress': '1', 'stress_anchor': '99'}):
                with self.subTest(changes=changes), self.assertRaises(build.BuildError):
                    read_variant(**changes)

    def test_editorial_macros_and_morphological_contrast(self):
        cls=(ROOT/'grammarstyle.cls').read_text()
        chapter=(ROOT/'chapters/phonology.tex').read_text()
        self.assertIn(r"\newcommand{\nkstress}", cls)
        self.assertIn(r"\newcommand{\nkaccent}", cls)
        for form in [r"\nkaccent{hjált}{A1}", r"\nkaccent{hjálte}{A2}", r"\nkstress{áfte}"]:
            self.assertIn(form, chapter)
        self.assertIn(r"\def\nkaccent#1#2{#1}", cls)
        self.assertIn(r"\accentcategory{#2}", cls)
        self.assertNotIn('Superscripts number the primary-stressed', (ROOT/'makefile').read_text())

    def test_particle_paradigm_records_lexical_accent(self):
        chapter = (ROOT/'chapters/phonology.tex').read_text()
        table = chapter.split(r'\label{tab:particle-lexical-accent}', 1)[1].split(r'\end{table}', 1)[0]
        for form in [r'\nkaccent{án}{A1}', r'\nkaccent{ǻn}{A1}',
                     r'\nkaccent{slǿt}{A1}', r'\nkaccent{ánˌsløt}{A1}',
                     r'\nkaccent{slǿtar}{A1}', r'\nkaccent{Slǿte}{A1}']:
            self.assertIn(form, table)


class RevisedVowelSpellingTests(unittest.TestCase):
    def test_current_vowels_and_diphthong_resolution(self):
        self.assertEqual(build.VOWEL_GRAPHEMES, set('aeiouyæøå'))
        for word, stress, expected in [('æ', '1', 'ǽ'), ('ø', '1', 'ǿ'),
                                      ('ae', '1', 'áe'), ('ae', '2', 'aé'),
                                      ('øys', '1', 'ǿys')]:
            self.assertEqual(build.stress_display(record(word, stress)), (expected, ''))
        self.assertIn('no written nucleus', build.stress_display(record('øys', '2'))[1])

    def test_current_letter_collation(self):
        self.assertEqual(sorted(['å', 'ø', 'æ', 'z'], key=build.dictionary_key),
                         ['z', 'æ', 'ø', 'å'])
        self.assertEqual(build.dictionary_heading('øys'), 'Ø')
        self.assertEqual(build.dictionary_heading('ærs'), 'Æ')

    def test_lexical_spelling_has_no_retired_letters(self):
        for row in build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv'):
            for field in ('lemma', 'infinitive', 'plural'):
                self.assertFalse(set(row.get(field, '')) & set('äöÄÖ'), (row['lemma'], field))
