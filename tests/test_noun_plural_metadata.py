"""Recorded noun paradigms remain available in the generated dictionary."""
from collections import defaultdict
import re
import unittest

from test_vocabulary import ROOT, build


class NounPluralMetadataTests(unittest.TestCase):
    def test_unique_attested_table_plurals_are_recorded(self):
        tables = {
            'chapters/nouns.tex': {
                'tab:plural-ar', 'tab:plural-or', 'tab:plural-a',
                'tab:plural-n', 'tab:plural-er-umlaut',
                'tab:plural-umlaut-only', 'tab:plural-zero',
            },
            'chapters/derivations.tex': {'tab:action-nouns-ande'},
        }
        attested = defaultdict(set)
        for filename, labels in tables.items():
            source = (ROOT / filename).read_text()
            seen = set()
            for table in re.findall(r'\\begin\{table\}.*?\\end\{table\}', source, re.S):
                match = re.search(r'\\label\{([^}]+)\}', table)
                if not match or match[1] not in labels:
                    continue
                seen.add(match[1])
                pairs = re.findall(
                    r'^\s*\\nk\{([^}]+)\}\s*&\s*\\nk\{([^}]+)\}',
                    table, re.M)
                self.assertTrue(pairs, (filename, match[1]))
                for lemma, plural in pairs:
                    attested[lemma].add(plural)
            self.assertEqual(seen, labels, filename)

        nouns = {row['lemma']: row for row in
                 build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
                 if row['partofspeech'] == 'n'}
        for lemma, plurals in attested.items():
            with self.subTest(lemma=lemma):
                self.assertIn(lemma, nouns)
                # A single-form field must not suppress recorded alternatives.
                # Multi-paradigm entries retain their links to the source tables.
                if len(plurals) == 1:
                    self.assertEqual(nouns[lemma]['plural'], next(iter(plurals)))
                else:
                    self.assertEqual(nouns[lemma]['plural'], '')

    def test_attested_slag_gender(self):
        rows = build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
        slag = next(row for row in rows if row['lemma'] == 'slåg')
        self.assertEqual(slag['gender'], 'm')
        # The singular definite article is explicit, not inferred from spelling.
        source = (ROOT / 'texts/middlemarch.tex').read_text()
        self.assertIn('en slåg sla brickhæd', source)
        self.assertIn('the type of beauty', source)
