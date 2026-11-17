"""The canonical verb 'do, make' is mycks, without a myks variant."""
import re
import unittest
from test_vocabulary import ROOT, build


class MycksTests(unittest.TestCase):
    def test_single_canonical_entry(self):
        rows = build.read_vocabulary(ROOT / 'vocabulary/vocabulary.csv')
        entries = [row for row in rows if row['partofspeech'] == 'v'
                   and row['definition'] == 'to do, to make']
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['lemma'], 'myck')
        self.assertEqual(entries[0]['infinitive'], 'mycks')
        self.assertEqual(entries[0]['inflection'], 'V-I')

    def test_examples_and_synthetic_passive(self):
        verbs = (ROOT / 'chapters/verbs.tex').read_text()
        nouns = (ROOT / 'chapters/nouns.tex').read_text()
        self.assertIn('Matti dægn med mycks smed læb.', verbs)
        self.assertIn('i mycks bram imed.', nouns)
        self.assertIn('mycken enmer', (ROOT / 'texts/middlemarch.tex').read_text())
        # Consonant-final Class I stems retain ck before their inflection.
        obsolete = re.compile(r'(?<!\w)myk(?:s|ar|æs|års|er|e|ade|ur|uren|sk|en|aren)?(?!\w)')
        for path in [*ROOT.glob('chapters/*.tex'), *ROOT.glob('texts/*.tex'),
                     ROOT / 'texts/corpus.csv', ROOT / 'README.md']:
            with self.subTest(path=path.name):
                self.assertIsNone(obsolete.search(path.read_text()))


if __name__ == '__main__':
    unittest.main()
