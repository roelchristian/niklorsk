"""Source-only regression checks for analytic finite aspect."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AspectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verbs = (ROOT / 'chapters/verbs.tex').read_text()
        cls.sources = [ROOT / 'README.md', *sorted((ROOT / 'chapters').glob('*.tex')),
                       *sorted((ROOT / 'texts').glob('*.tex')), ROOT / 'texts/corpus.csv']

    def test_obsolete_finite_aspect_absent(self):
        obsolete = ('hjaltatt', 'hjaltet', 'bratt', 'sollnatt', 'kanselatt',
                    'kanselert', 'tagett', 'bördutt', 'bängdutt', 'slämatt',
                    'stettatt', 'svoratt', 'pöljatt', 'hjeckatt', 'mykatt',
                    'bördet', 'vædatten', 'naurtet', 'nöyrtet', 'enrammet', 'anslötet',
                    'anslötatt', 'voratt', 'vorst', 'normaˈlisatt')
        pattern = r'(?<!\w)(?:' + '|'.join(map(re.escape, obsolete)) + r')(?!\w)'
        for path in self.sources:
            text = path.read_text()
            with self.subTest(path=path.name):
                self.assertIsNone(re.search(pattern, text))
                self.assertNotIn(r'\Prog', text)
                # Perfect glossing remains only on retained perfect infinitives.
                self.assertIsNone(re.search(r'\\Perf(?:\{\})?\.(?!\\Inf)', text))
        self.assertIsNone(re.search(r'^\s*(?:Perfect|Progressive)\s*&', self.verbs, re.M))

    def test_perfect_auxiliary_and_invariable_participle(self):
        for form in ('får hjaltur', 'fårar hjaltur', 'fåräs hjaltur',
                     'Ag får så när hjaltur', 'får vorur i hjalts'):
            self.assertIn(form, self.verbs)
        self.assertIn('invariable', self.verbs)
        self.assertIn('fårar nortur Joann', (ROOT / 'chapters/texts.tex').read_text())

    def test_be_perfect_examples(self):
        for form in ('Ag får hjaltur en afte', 'Matti får lotur',
                     'Matti ö slötur', 'Matti ö malmur at Norge',
                     'Matti ö anslötur', 'Matti ö atslötur',
                     'Matti vor slötur', 'Matti vörs slötur',
                     'Matti års slötur', 'Matti voren slötur',
                     'Matti ö så slötur', 'Matti ö så slötur an',
                     'Gå ö slöturen', 'Matti tind slötsk'):
            self.assertIn(form, self.verbs)
        for form in ('mustur', 'lotur', '-uren', '-guren'):
            self.assertIn(form, self.verbs)
        self.assertNotIn('Matti ö så anslötur', self.verbs)

    def test_number_only_past_participles(self):
        for path in self.sources:
            with self.subTest(path=path.name):
                self.assertNotIn('urär', path.read_text())
        modifiers = (ROOT / 'chapters/modifiers.tex').read_text()
        self.assertIn('hjalturen', modifiers)
        # Present participle agreement remains distinct.
        self.assertIn('hjaltade', modifiers)

    def test_interlinear_participial_agreement(self):
        pairs = re.findall(r'\\gla\s+(.*?)//\s*\\glb\s+(.*?)//',
                           self.verbs, re.S)
        examples = {source: gloss for source, gloss in pairs}
        be_perfect = 'Matti ö slötur. Gå ö slöturen.'
        passive = 'Der hjölter får vorur kvinturen på Matti.'
        self.assertIn(be_perfect, examples)
        self.assertIn(passive, examples)
        for source in (be_perfect, passive):
            self.assertEqual(len(source.split()), len(examples[source].split()))
        self.assertIn(r'come.\PstP{}.\Sg{}', examples[be_perfect])
        self.assertIn(r'come.\PstP{}.\Pl{}', examples[be_perfect])
        self.assertIn(r'be.\PstP{} bake.\PstP{}.\Pl{}', examples[passive])

    def test_interlinear_token_alignment(self):
        for path in [*sorted((ROOT / 'chapters').glob('*.tex')),
                     *sorted((ROOT / 'texts').glob('*.tex'))]:
            for source, gloss in re.findall(
                    r'\\gla\s+(.*?)//\s*\\glb\s+(.*?)//', path.read_text(), re.S):
                with self.subTest(path=path.name, example=source):
                    self.assertEqual(len(source.split()), len(gloss.split()))

    def test_auxiliary_scope_and_selection_limits(self):
        self.assertIn('Neither the subject nor an object controls agreement on its participle', self.verbs)
        self.assertIn('retains \\nk{fårs} even with an embedded motion verb', self.verbs)
        self.assertIn('finite \\nk{fårs}, invariable \\nk{vorur}, and an agreeing lexical past participle', self.verbs)
        self.assertIn('Eg hjålt får vorur kvintur på Matti', self.verbs)
        self.assertIn('not merely a direction of movement', self.verbs)
        self.assertIn('not a promoted object', self.verbs)
        self.assertIn('without necessarily implying that Matti remains at the destination', self.verbs)
        self.assertIn('is independent of finite auxiliary selection', self.verbs)

    def test_progressive_remains_infinitival(self):
        for form in ('ö i hjalts', 'vor i hjalts', 'vörs i hjalts',
                     'Ag ö så i hjalts', 'Ag ö så i mursts med op'):
            self.assertIn(form, self.verbs)

    def test_retained_nonfinite_and_mood_forms(self):
        for form in ('hjaltsk', 'bragsk', 'fjerdsk', 'hjaltade', 'brade',
                     'hjaltur', 'bragur', 'vorur', 'hjaltårs', 'brars',
                     'hjalter', 'brager', 'hjalte', 'brage'):
            self.assertIn(form, self.verbs)
        self.assertNotIn('braur', self.verbs)
        self.assertIn(r'\nikp{vorur}{been}', self.verbs)
        self.assertIn(r'\nikp{ur}{become}', self.verbs)

    def test_passive_is_preserved(self):
        self.assertIn(r'\nk{-(e)n}', self.verbs)
        self.assertIn('past participle agreeing with the subject in number only', self.verbs)
        self.assertNotIn('past participle agreeing with the subject in gender and number', self.verbs)
        self.assertIn('braren hel', self.verbs)
        self.assertIn(r'\label{sec:passive-voice}', self.verbs)


if __name__ == '__main__':
    unittest.main()
