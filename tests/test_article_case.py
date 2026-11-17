"""Definite articles preserve case without inventing accusative allomorphs."""
import unittest
from test_vocabulary import ROOT


class ArticleCaseTests(unittest.TestCase):
    def test_syncretic_paradigm(self):
        text = (ROOT / 'chapters/nouns.tex').read_text()
        common = r' & \nk{en} & \nk{de} & \nk{eg} & \nk{der}'
        self.assertIn('Nominative' + common, text)
        self.assertIn('Accusative' + common, text)
        self.assertIn(r'Dative & \nk{om} & \nk{der} & \nk{egn} & \nk{dæ}', text)

    def test_recipient_and_theme_case(self):
        text = (ROOT / 'chapters/syntax.tex').read_text()
        self.assertIn('Matti brar om hond en afte', text)
        self.assertIn('Fronting either argument preserves its case', text)
        for form in ('der mama', 'egn hond', 'dæ hynd'):
            self.assertIn(form, text)
        self.assertIn(r'\gla Matti brar om hond men skæmd.//', text)
        self.assertIn(r'\gla Om hond brar Matti men skæmd.//', text)

    def test_possessor_articles_agree_with_possessor(self):
        text = (ROOT / 'chapters/nouns.tex').read_text()
        for phrase in ('de brug sla en bliv', 'de brug sla en svorade bliv',
                       'de banger brug sla Martin', 'eg roghjalt sla Andærs'):
            self.assertIn(phrase, text)
        for obsolete in ('blivt', 'blivtes', 'skællt', 'skælltes'):
            self.assertNotIn(obsolete, text)


if __name__ == '__main__':
    unittest.main()
