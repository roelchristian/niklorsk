# A Grammar of Niklorsk

*A Grammar of Niklorsk*, by Roel Christian Yambao, describes the sound system,
word forms, and clause structure of Niklorsk. The manuscript combines
grammatical descriptions with paradigms, interlinear examples, sample texts,
and a Niklorsk–English vocabulary.

## The language

Niklorsk has basic subject–verb–object order, with prepositions and generally
prenominal adjectives. Constituent fronting can alter the order of the subject
and verb.

Nouns have masculine, feminine, and neuter gender, with several lexical plural
patterns. Nominal possession is expressed with postnominal *sla* phrases,
while personal pronouns retain accusative and dative forms and a separate
possessive paradigm. Adjectives agree with
the nouns they modify in gender and number. The verbal system includes finite
and non-finite forms, tense and aspect distinctions, conditional constructions,
and passive forms.

The copula *vors* covers identity, state, existence and location, with present
*ø* and past *vor*. The present, past and future are inflected synthetically. Perfect aspect normally uses
finite *fårs* ‘have’ with an invariable past participle. Directed intransitive
motion selects *vors* with a lexical participle agreeing in number, not gender; *læts*
‘walk’ permits this auxiliary in a licensed bounded-motion construction. The progressive
uses finite forms of *vors* followed by *i* and an infinitive; these constructions can
also combine in the perfect progressive. A synthetic perfect infinitive
expresses anterior events in non-finite complements.

Particle verbs separate the particle from a finite lexical verb in both main
and subordinate clauses, including synthetic passives and imperatives.
Infinitives and participles incorporate the particle, including under negation
and with pronominal objects. Mobile particles contrast with inseparable
prefixes in both placement and stress.

The phonology chapter treats vowel and consonant length, the diphthong /œʏ̯/, syllable
structure, variable lexical stress, two lexical pitch accents, and phrasal
intonation. Accent 1 has an early high target followed by a fall; Accent 2
rises to a late high target, with variable early laryngealisation. Their
opposition is licensed within the primary-stressed rhyme by a long vowel, a
diphthong, or a short vowel followed by a moraic sonorant. Metrical weight
alone does not license the contrast.

Stress normally falls on the initial syllable of a native root and remains
stable through inflection. Compounds and some derivational suffixes introduce
secondary stress, while a small class of suffixes attracts primary stress.
Unstressed syllables undergo extensive vowel reduction, schwa assimilation,
syncope, apocope, and contraction. Articles, pronouns, and prepositions have
weak forms and clitic pronunciations in connected speech. The spelling
preserves distinctions that merge in ordinary pronunciation.

## What the grammar covers

- [Phonology and orthography](chapters/phonology.tex): vowel and consonant
  inventories, syllable structure and phonotactics, quantity, lexical and
  phrasal stress, lexical pitch accent and its history, selected nominal,
  verbal, and particle accent paradigms, intonation, vowel erosion, sound
  realization, and spelling conventions.
- [Verbs](chapters/verbs.tex): conjugation, inherited lexical accent
  alternations, tense and aspect, negation, conditional and modal constructions,
  infinitives and participles, separable verbs and particle placement with
  direct objects, copular and existential constructions, and the passive voice.
- [Nouns and pronouns](chapters/nouns.tex): gender, definite and indefinite
  articles, number, case, personal and demonstrative pronouns, and noun phrases.
- [Other word classes](chapters/modifiers.tex): adjective agreement and
  comparison, possessive forms, cardinal numerals, counting in twenties,
  long-scale numerals, adverbs, prepositions, and conjunctions.
- [Clause structure](chapters/syntax.tex): basic word order, ditransitive verbs
  and the dative alternation, constituent fronting, questions, relative clauses,
  and complement clauses.
- [Derivational morphology](chapters/derivations.tex): word-forming affixes and
  their stress classes, the inseparable lexical derivational prefixes *gæ-*, *før-* and *en-*, and noun-noun compounds
  with primary and secondary stress.
- [Sample texts](chapters/texts.tex): passages in Niklorsk with interlinear
  glosses and English translations.

## Vocabulary and texts

The [vocabulary](vocabulary/vocabulary.csv) supplies the manuscript’s
Niklorsk–English dictionary, whose inflection labels link to the relevant
paradigms. Entries record parts of speech, noun gender, inflection groups,
English meanings, primary stress and lexical accent where specified. Verbs use
the infinitive as their citation form, with particles and prefixes incorporated,
and derived words have separate entries. A question mark identifies an
unrecorded class or incomplete paradigm; noun plurals are described in the noun
and derivation chapters. An optional `plural` field preserves an explicitly
recorded noun plural and prints it in the entry; `N-exp` records such a form
without assigning a productive inflection class.

In displayed headwords, an acute marks primary stress and superscript 1 or 2
records lexical A1 or A2, independently of its surface realisation. An omitted
superscript leaves the lexical category unspecified.

In the CSV, `infinitive` holds each verb’s citation form and `lemma` its present
stem for morphological lookup. Older word lists containing verbs must supply
the `infinitive` column explicitly, since the generator does not infer missing
forms. The separate optional `perfect_auxiliary` field records `BE` for directed
motion verbs and `ALTERNATING` for predicates with a licensed activity/transition
alternation. These values describe lexical selection independently of conjugation class:
verbal entries default to `HAVE`, which may also be recorded explicitly, while
non-verbal entries leave the field blank. The generated dictionary identifies
non-default selection and links to the perfect section.

`stress` is a one-based syllable index, and `accent` is `A1`, `A2` or
blank. `stress_anchor`, when required, identifies the stressed vowel by its
one-based Unicode grapheme position in the citation form; it resolves an
exception rather than supplying missing stress data. The generator groups
`øy` as one nucleus and treats other adjacent vowel graphemes as hiatus.
It emits `notation_warnings.json` alongside the generated vocabulary for
missing or unresolved metadata. Display accents do not change stored spelling,
lookup or sorting. Run `python3 -m unittest discover -s tests -v` for source-only checks.

Additional material in [texts/](texts/) includes a translation draft from
*Middlemarch* and a small Niklorsk–English corpus. These are separate from the
sample-text chapter included in the manuscript.

## Manuscript status

Some sections remain outlines or partial descriptions.

The manuscript entry point is [grammar.tex](grammar.tex). Run `make` to compile
and validate it; a successful build produces `grammar.pdf` in the root.
