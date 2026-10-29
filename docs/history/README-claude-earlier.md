> **Historical document.** An earlier, unvoiced version of the project written before the audio was added. Its file names, deck counts and source list are out of date. The current documentation is [`../../README.md`](../../README.md).

# Serbian–English Anki Decks (frequency-ordered vocabulary + verb patterns)

Two Anki decks for learners of Serbian, built in October 2026:

| Deck | File | Cards | What it is |
|---|---|---|---|
| **Vocabulary** | `Serbian_Frequency_Deck_v7_complete.apkg` | 2,293 | Word → meaning + two simple example sentences, sorted by frequency |
| **Verb patterns** | `Serbian_Verb_Patterns_top50.apkg` | 150 | 50 common verbs × 3 gap-sentence cards each, with full present paradigm |

Supporting files: `skipped_entries.txt` (words deliberately left out of the vocabulary deck) and `serbian_deck_buildkit.tar.gz` (the scripts and data needed to rebuild both decks).

> **Status / honesty notes**
> - The decks have been integrity-checked as SQLite/Anki packages, but **were not opened in Anki by the author of the build scripts (an AI assistant)**. Please test the import on a backup profile first.
> - All glosses and example sentences were **written by an AI (Claude) and have not been reviewed by a native Serbian speaker**. Expect occasional unnatural phrasing. Corrections are welcome.

---

## Card design

Minimal "Japanese-style" cards with very little styling, so that Anki add-ons and themes can restyle them freely.

**Vocabulary deck** — note type `Serbian Frequency (word→meaning)`, one card per note:

`Rank · Word · Cyrillic · POS · Meaning · Example1 · Example1_EN · Example2 · Example2_EN`

- Front: the Latin-script word. Back: Cyrillic, part of speech, meaning, two examples with translations.
- Cards are ordered by frequency rank (new-card order follows rank). Tags like `freq_0001-0100` allow filtered decks by band.
- Cyrillic is generated automatically by a Latin→Cyrillic transliteration script (including `lj`, `nj`, `dž`), not hand-written; rare words may need a second look.

**Verb deck** — note type `Serbian Verb Pattern (gap)`, one card per note:

`Rank · Verb · Gloss · Person · Prompt · Answer · Sentence · English · Paradigm · Past · Pair · Note`

- Front: a sentence with a blank and a cue (verb · person), e.g. *Hoću da _____ sutra.* → *doći · ja*.
- Back: the full sentence with the answer highlighted, English translation, the six present-tense forms, masculine/feminine past forms, the aspect partner (perfective ↔ imperfective), and a one-line note on irregularities.
- 16 perfective and 34 imperfective verbs; 18 verbs are tagged `irregular`. Perfective verbs are shown in the contexts where their present forms actually occur (after *da / kad / ako*).

## Updating an already-imported deck

Every note has a stable GUID, so importing a newer version of the same deck updates existing cards instead of duplicating them:

- Vocabulary: GUID = first 10 hex characters of `SHA-1("srfreq:" + lemma key)`; note type ID `1700000000001`.
- Verbs: GUID = first 10 hex characters of `SHA-1("srverb:" + verb + ":" + card index)`; note type ID `1700000000011`.

Rank numbers on cards can shift slightly between versions when words are added or merged; Anki will update the field, but it does not reorder cards you have already studied.

---

## Sources and credits

### Input data: community Anki decks

Seven community decks were provided as `.apkg` files. **The original authors, URLs, and licences of these decks were not recorded in the files I received. Please fill in the attribution below from the original AnkiWeb pages before publishing.**

| Deck (file name as received) | Notes | How it was used | Original author / URL / licence |
|---|---|---|---|
| `Serbian_Frequency_Word_List.apkg` | 3,833 | **Primary source.** Provided the headword list and the frequency order. Its definition fields look like English-Wiktionary-style entries (part-of-speech sections, IPA, Cyrillic forms); they were parsed only to identify lemmas, inflected forms and homographs. | TODO |
| `Serbian_Sentences.apkg` | 3,001 | Examined as a possible source of example sentences. **Not used in the final cards**: sentences were very short fragments (median 3 words) and covered only about 470 of ~3,500 headwords. | TODO |
| `Serbian_A1_Phrases.apkg` | 198 | Examined together with the sentence deck for the same purpose. Not used in the final cards. | TODO |
| `English-Serbian_Vocabulary.apkg` | 1,150 | Inspected; not used in the final cards. | TODO |
| `Serbian_language_learning.apkg` | 193 | Inspected; not used in the final cards. | TODO |
| `Serbian_most_frequent_words_.apkg` | 293 | Inspected; not used (this deck is Greek–Serbian, with Greek field names). | TODO |
| `Serbian_-_English_Audio__Text_Male_Voice_SmartXP.apkg` | 109 | Inspected; not used. Audio coverage (109 cards) was too small to cover the vocabulary list, so the final decks have **no audio**. | TODO |

### What is original to this project

- All **meanings** and **example sentences** (≈4,600 vocabulary examples and 150 verb sentences) and their English translations — written by the AI assistant, not copied from the source decks.
- The lemma-merging rules, the manual lemma table for ambiguous inflected forms, the ekavian standardization, the verb paradigm data, the card templates, and the build scripts.

### Tools and libraries

- Python 3 standard library (`sqlite3`, `zipfile`, `json`, `hashlib`) for reading and writing `.apkg` files. The `.apkg` writer was implemented directly (legacy collection schema v11) because `genanki` was not available in the offline build environment.
- `BeautifulSoup` (bs4) for parsing the HTML definition fields of the frequency deck.
- Built with **Claude** (Anthropic) — model reported by the app as Claude Sonnet 5.5 — working interactively with the requester, who set the scope, card format and editorial rules.

---

## Method (what was done, in order)

1. **Extraction.** `.apkg` files are zip archives containing an SQLite collection; notes and field names were read directly.
2. **Parsing the frequency list.** Definition HTML was parsed into headword, part of speech, senses, IPA and Cyrillic form.
3. **De-duplication.**
   - 304 entries were Cyrillic headwords; 301 of them had a Latin-script twin and were dropped.
   - Single-letter entries were dropped (except *i, u, a, o*).
4. **Lemma consolidation.** About a thousand entries were inflected forms ("inflection of …", participles, case forms). They were merged into their lemma, and the lemma took the **best (lowest) frequency rank** of its forms. About 170 forms whose lemma was missing or mis-parsed (homographs such as *šuma*, *mali*, *kažem*) were resolved with a hand-written lookup table.
5. **Ekavian standardization.** The source mixes ekavian and ijekavian/Croatian forms. The deck standardizes on ekavian (*vreme, videti, mleko*); ijekavian doublets (*vrijeme, vidjeti*) were merged into the ekavian card, and Croatian-only variants (*tisuća, liječnik, točka, računalo*) were merged into the Serbian equivalent or left out.
6. **Result of steps 2–5:** 3,833 source entries → **2,682 lemma entries**.
7. **Hand authoring.** The automatic glosses were unreliable for top-frequency words because homographs hijack them (e.g. *biti* → "to beat", *kada* → "bathtub", *sad* → "plant nursery"), so every card was authored by hand in 19 batch files (≈2,300 cards plus 114 merge directives).
8. **Quality checks run on every batch:** exact-duplicate example sentences across the whole deck (all removed), malformed rows, empty fields, SQLite integrity, and GUID stability against the previous release.
9. **Verb deck.** 50 high-frequency verbs were selected; present paradigms, past forms and aspect partners were written out and each card's answer was validated programmatically against its paradigm.

## Editorial decisions

- **Standard variety:** ekavian Serbian, Latin script on the front, Cyrillic on the back.
- **Omitted on purpose:** profanity and slurs, sexual-violence vocabulary, drug words, suicide-related vocabulary, Croatian-only variants, and single-letter or obscure noise entries. A first pass was too strict and also removed some neutral words (*gej, ortak, stara, seks, gđica* …); those were restored in v7. The remaining 260 omitted entries are listed in `skipped_entries.txt` so anyone can add back words they want.
- **Examples are short and simple** and were **not** vocabulary-controlled: an example may contain words ranked later in the deck.
- **Same-lemma cards:** each lemma has one card, even where several senses exist (senses are listed in the meaning field).

## Known limitations

- No native-speaker review; no audio.
- Frequency order is inherited from the source list. Its underlying corpus is not documented in the deck, and the ordering shows a lean toward conversational/film-style vocabulary (e.g. crime and police words rank fairly high).
- The Cyrillic field is automatic and has not been proof-read.
- Some multi-sense words are compressed into a single card; a few grammatical particles are glossed loosely.

## Rebuilding

`serbian_deck_buildkit.tar.gz` contains:

```
work/
├── base.json          # merged lemma table (derived from the frequency deck; see licence note)
├── batches/b01–b19    # hand-authored cards and merge directives (pipe-separated)
├── make_deck.py       # builds the vocabulary .apkg
└── verbs/
    ├── verbs_data.py  # 50 verbs, paradigms and sentences
    └── make_verbs.py  # builds the verb .apkg
```

```bash
python3 work/make_deck.py   out/Serbian_Frequency_Deck.apkg
python3 work/verbs/make_verbs.py out/Serbian_Verb_Patterns.apkg
```

Batch line format: `key|display|pos|meaning|example1|translation1|example2|translation2`; lines starting with `=` merge a variant into another entry (`=sretan>srećan`).

---

## Licence note (please verify before publishing)

I cannot determine the licences of the source decks, and this is not legal advice. Things to check:

- **Source decks:** confirm each deck's licence and author on its AnkiWeb page, and credit them in the table above.
- **Wiktionary-derived data:** the frequency deck appears to carry English-Wiktionary-style definitions. Wiktionary text is generally available under CC BY-SA 4.0. `base.json` in the build kit contains glosses carried over from that deck for reference; if you publish it, you may need to attribute Wiktionary and keep that file under a compatible share-alike licence. The released decks' meanings and examples were hand-written, but the **headword list and ordering come from the source deck**.
- A cautious choice for the generated content is **CC BY-SA 4.0**, with credits to the source decks and Wiktionary; choose what suits your situation after checking the points above.

## Suggested credits block for your repository

> Vocabulary headwords and frequency order derived from the community deck "Serbian Frequency Word List" (author/URL: *add here*). Definitions in that deck appear to derive from Wiktionary (CC BY-SA 4.0). Meanings, example sentences, verb patterns, card templates and build scripts were written with the AI assistant Claude (Anthropic) under the direction of *your name*. Other community decks were reviewed during preparation but not incorporated.
