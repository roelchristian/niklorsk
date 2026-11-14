# A Grammar of Niklorsk

*A Grammar of Niklorsk*, by Roel Christian Yambao, describes the sound system,
word forms, and clause structure of Niklorsk. The manuscript combines
grammatical descriptions with paradigms, interlinear examples, sample texts,
and a Niklorsk–English vocabulary.

## The language

Niklorsk has a basic subject–verb–object word order. It uses prepositions, and
adjectives generally precede the nouns they modify. The grammar also describes
constituent fronting and the changes in word order associated with it.

Nouns have masculine, feminine, and neuter gender, with several lexical plural
patterns and a distinction between nominative and genitive case. Personal
pronouns retain additional accusative and dative forms. Adjectives agree with
the nouns they modify in gender and number. The verbal system includes finite
and non-finite forms, tense and aspect distinctions, conditional constructions,
and passive forms.

Modern speech normally expresses the progressive with *vor i* followed by an
infinitive. The synthetic progressive in *-att* or *-tt* remains preferred in
writing, especially in literary prose. The two forms have essentially the same
meaning; their usual difference is register.

The synthetic passive in *-(e)n* is especially common in general statements,
instructions and formal prose, but also permits particular events. The
periphrastic *vor* passive is preferred for ordinary spoken event reports.
Resultant-state predicates share the latter form but have a distinct adjectival
analysis. Ordinary erosion can neutralise synthetic active–passive contrasts.

Particle verbs ordinarily combine a preverbal particle with the verbal stem
as one word. The grammar describes their separation with negation, pronominal
or demonstrative objects, imperatives, and synthetic passives. It also treats
particle placement with modals, in questions, and in inverted clauses. Mobile
particles contrast with inseparable prefixes in both placement and stress.

The phonology chapter treats vowel and consonant length, diphthongs, syllable
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
- [Nouns and pronouns](chapters/nouns.tex): gender, articles, number, case,
  personal and demonstrative pronouns, and noun phrases.
- [Other word classes](chapters/modifiers.tex): adjective agreement and
  comparison, possessive forms, adverbs, prepositions, and conjunctions.
- [Clause structure](chapters/syntax.tex): basic word order, ditransitive verbs
  and the dative alternation, constituent fronting, questions, relative clauses,
  and complement clauses.
- [Derivational morphology](chapters/derivations.tex): word-forming affixes and
  their stress classes, the inseparable lexical derivational prefixes *gæ-*, *för-* and *en-*, and noun-noun compounds
  with primary and secondary stress.
- [Sample texts](chapters/texts.tex): passages in Niklorsk with interlinear
  glosses and English translations.

## Vocabulary and texts

The [vocabulary](vocabulary/vocabulary.csv) records Niklorsk lemmas, parts of
speech, noun gender, plural forms where given, English meanings, and specified
primary-stress positions. Alternate plurals appear together; unchanged plurals
are explicitly recorded. The same word list supplies the manuscript's
vocabulary appendix. It does not yet record lexical accent categories.

Additional material in [texts/](texts/) includes a translation draft from
*Middlemarch* and a small Niklorsk–English corpus. These are separate from the
sample-text chapter included in the manuscript.

## Manuscript status

Some sections remain outlines or partial descriptions.

The manuscript entry point is [grammar.tex](grammar.tex). Run `make` to compile
and validate it; a successful build produces `grammar.pdf` in the root.
