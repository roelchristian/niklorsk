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

The phonology chapter treats vowel and consonant length, diphthongs, variable
lexical stress, and the relationship between spelling and pronunciation.
Stress normally falls on the initial syllable of a native root and remains
stable through inflection. Compounds and some derivational suffixes introduce
secondary stress, while a small class of suffixes attracts primary stress.

## What the grammar covers

- [Phonology and orthography](chapters/phonology.tex): vowel and consonant
  inventories, quantity, stress and reduction, sound realization, and spelling
  conventions.
- [Verbs](chapters/verbs.tex): conjugation, tense and aspect, negation,
  conditional and modal constructions, infinitives and participles, separable
  verbs, copular and existential constructions, and the passive voice.
- [Nouns and pronouns](chapters/nouns.tex): gender, articles, number, case,
  personal and demonstrative pronouns, and noun phrases.
- [Other word classes](chapters/modifiers.tex): adjective agreement and
  comparison, possessive forms, adverbs, prepositions, and conjunctions.
- [Clause structure](chapters/syntax.tex): basic word order, ditransitive verbs
  and the dative alternation, constituent fronting, questions, relative clauses,
  and complement clauses.
- [Derivational morphology](chapters/derivations.tex): word-forming affixes and
  their stress classes, and noun-noun compounds with primary and secondary
  stress.
- [Sample texts](chapters/texts.tex): passages in Niklorsk with interlinear
  glosses and English translations.

## Vocabulary and texts

The [vocabulary](vocabulary/vocabulary.csv) records Niklorsk words, their parts
of speech, English meanings, and specified primary-stress positions. Noun
entries include plural forms where given. The same word list supplies the
manuscript's vocabulary appendix.

Additional material in [texts/](texts/) includes a translation draft from
*Middlemarch* and a small Niklorsk–English corpus. These are separate from the
sample-text chapter included in the manuscript.

## Manuscript status

This is a working grammar. Some sections are outlines or partial descriptions,
and forms and analyses may be revised as the manuscript develops.

The manuscript entry point is [grammar.tex](grammar.tex). Run `make` to compile
and validate it; a successful build produces `grammar.pdf` in the root.
