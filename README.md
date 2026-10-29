# Serbian Anki decks: frequency vocabulary and verb patterns (with audio)

Two Anki decks for learners of Serbian, with Serbian audio on every headword and example sentence. Each deck comes in two versions: **English** and **Russian** (the Serbian text and audio are the same in both).

**[Русская версия README →](README.ru.md)**

| Deck | Language | Release file | Notes | Audio clips | What it is |
|---|---|---|---|---|---|
| Vocabulary | English | `Serbian_Frequency.apkg` | 2,293 | 6,879 | Latin word → Cyrillic, part of speech, meaning, two example sentences with English translations; ordered by frequency |
| Vocabulary | Russian | `Serbian_Frequency_RU.apkg` | 2,293 | 6,879 | The same deck with Russian meanings, part-of-speech labels and example translations |
| Verb patterns | English | `Serbian_Verbs.apkg` | 150 | 300 | 50 common verbs × 3 gap-sentence cards each, with the present paradigm, past forms and aspect partner |
| Verb patterns | Russian | `Serbian_Verbs_RU.apkg` | 150 | 300 | The same cards with Russian glosses, translations and notes |

> **Status.** Every meaning, example sentence, translation and verb paradigm was written by an AI assistant (Claude). The English text was written first; the Russian was translated from the English by an AI assistant. All audio is machine-generated. A **random sample** of the English text and audio was proofread by a native Serbian speaker; the rest of the deck has not been reviewed. **The Russian translations have not been reviewed by a native Russian speaker.** Expect occasional unnatural phrasing or pronunciation errors. Corrections are welcome.

## Download and import

The decks are not stored in this repository. Download them from the **[Releases page](https://github.com/haruhiistjp/serbian-deck/releases)**:

- Import: `Serbian_Frequency.apkg`, `Serbian_Verbs.apkg` (English) or `Serbian_Frequency_RU.apkg`, `Serbian_Verbs_RU.apkg` (Russian).
- Pipeline inputs: `Serbian_Frequency_complete.apkg` and `Serbian_Verb_Patterns.apkg`, the unvoiced English versions of the decks (no audio), used as input to the audio pipeline.

In Anki: **File → Import** and choose the `.apkg` file. The decks are created as:

- English: `Serbian::Frequency (Audio)` and `Serbian::Verbs (Audio)`
- Russian: `Serbian-Russian::Frequency (Audio)` and `Serbian-Russian::Verbs (Audio)`

Each deck uses its own note type, and the English and Russian decks have different IDs, so you can import both into one collection. Test on a backup profile first if you are unsure.

## Card design

**Script.** The cards are written in Latin script. The vocabulary deck also has a Cyrillic form of each word, shown only on the back of the card. The verb deck has no Cyrillic. Audio was generated from the Latin text, not from the Cyrillic.

**Vocabulary** (note type `Serbian Frequency (word→meaning, audio)` in English, `… audio, RU` in Russian; one card per note)

- Fields: `Rank`, `Word`, `Cyrillic`, `POS`, `Meaning`, `Example1`, `Example1_EN` (or `Example1_RU`), `Example2`, `Example2_EN` (or `Example2_RU`), `Word_Audio`, `Example1_Audio`, `Example2_Audio`.
- Front: the Latin-script word and its audio. Back: Cyrillic, part of speech, meaning, and both examples with translations and audio.
- New-card order follows frequency rank.

**Verb patterns** (note type `Serbian Verb Pattern (gap, audio)` in English, `… audio, RU` in Russian; one card per note)

- Front: a sentence with a blank and a cue (verb · person), for example *Hoću da _____ sutra.* → *doći · ja*.
- Back: the completed form and its audio, the full sentence with audio, the translation, the six present-tense forms, past forms, the aspect partner (perfective ↔ imperfective), and a short note on irregularities.

## Audio

- Generated with Google Gemini text-to-speech (model `gemini-3.8-flash-tts`, language `sr-RS`). Text is sent in Latin script exactly as displayed.
- Five prebuilt voices are used: male *Charon*, *Fenrir*; female *Kore*, *Autonoe*, *Vindemiatrix*. They were chosen after an audition of all 30 voices on Serbian sentences containing *đ*, which most voices rendered incorrectly.
- Voice assignment is fixed by a seed, so rebuilding reproduces it.
- In the vocabulary deck, example 1 is read by a male voice, example 2 by a female voice, and the headword alternates by rank parity. In the verb deck, the completed form is male and the full sentence is female.
- Serbian verbs in the first person change with the speaker's gender ("Napravila sam kolač" is said by a woman). Where a sentence was spoken by a different gender than its slot's voice, the two examples of that note are swapped, so the voice matches the speaker. In 6 notes both sentences are spoken by a man, so example 2 uses a male voice in those notes. The speakers are listed in `speaker_gender.tsv`.
- Clips are silence-trimmed, level-matched (about −20 dBFS RMS) and encoded as MP3 mono 24 kHz, 64 kbps.
- The Russian decks use the same clips as the English decks.
- Google's terms state that Google does not claim ownership of content generated through its services.

## Russian translations

The Russian decks translate the English text: meanings, part-of-speech labels, example translations, verb glosses, translations and notes. The Serbian words, sentences and paradigms are unchanged. The translations are in `translations/ru/` (`freq.tsv` and `verbs.tsv`), one row per note, so they can be reviewed and corrected directly in git.

Russian was generated by an AI assistant (Claude) and has **not been reviewed by a native Russian speaker**.

## Omitted words

Some words were left out on purpose. The list is in [`skipped_entries.txt`](skipped_entries.txt) (260 entries), so you can see what was omitted and add back any you want.

> **Warning:** `skipped_entries.txt` contains profanity, slurs, sexual and violent vocabulary, and drug and suicide-related terms. Its glosses were carried over from the source frequency list and may be wrong.

Omitted categories: profanity and slurs, sexual-violence vocabulary, drug words, suicide-related vocabulary, Croatian-only variants, and single-letter or obscure noise entries. A first pass was too strict and removed some neutral words; those were restored in the final deck.

## Sources and credits

Deck references (the original authors are not shown inside Anki; use the AnkiWeb pages to find them):

| Deck (AnkiWeb) | Link | Role in this project |
|---|---|---|
| Serbian Frequency Word List | [558656370](https://ankiweb.net/shared/info/558656370) | **Used.** Headword list and frequency order for the vocabulary deck. |
| Serbian Sentences | [163129316](https://ankiweb.net/shared/info/163129316) | Consulted; not used in the published decks. |
| Serbian – English (Audio + Text) Male Voice SmartXP | [120206932](https://ankiweb.net/shared/info/120206932) | Consulted; not used in the published decks. |
| English-Serbian Vocabulary | [1612667773](https://ankiweb.net/shared/info/1612667773) | Consulted; not used in the published decks. |
| Serbian most frequent words | [1398663823](https://ankiweb.net/shared/info/1398663823) | Consulted; not used in the published decks. |
| Serbian language learning | [1072723263](https://ankiweb.net/shared/info/1072723263) | Consulted; not used in the published decks. |
| Serbian A1 Phrases | [1281188335](https://ankiweb.net/shared/info/1281188335) | Consulted; not used in the published decks. |

Definitions in the community decks derive from [Wiktionary](https://en.wiktionary.org/), which is available under CC BY-SA 4.0. Wiktionary contributors are credited accordingly.

Meanings, example sentences, translations, verb paradigms, card templates and build scripts were written with the AI assistant Claude (Anthropic) under the direction of the project maintainer. The Russian translations were produced by the same assistant from the English text. The audio was generated with Google Gemini.

## Known limitations

- Only a random sample of the English text and audio was checked by a native speaker. The rest of the deck is unreviewed.
- The Russian translations have not been reviewed by a native speaker.
- The check that matched voices to speakers covers the gendered first-person forms it could identify. Other gendered forms may remain; a native speaker should listen to a sample.
- Frequency order is inherited from the source list. Its corpus is not documented, and the list leans toward conversational and film-style vocabulary (for example crime and police words rank fairly high).
- Some multi-sense words are compressed into one card, and a few grammatical particles have loose glosses. Each card lists its senses in the meaning field.
- Cyrillic is generated automatically by a Latin→Cyrillic transliteration script and has not been proof-read.

## Repository contents

```
LICENSE                       CC BY-SA 4.0 (content)
LICENSE-MIT                   MIT (code)
README.md                     this file (English)
README.ru.md                  Русская версия этого файла
PROJECT_NOTES.md              detailed handover notes: voices, costs, repairs, gotchas
skipped_entries.txt           omitted words, with a profanity warning
speaker_gender.tsv            speaker gender of the example sentences that were checked by hand
translations/ru/              Russian translations: freq.tsv (by rank), verbs.tsv (by guid)
docs/history/                 earlier documentation, kept for reference
source/                       (not in git) unvoiced English input decks, from the Releases page
*.apkg                        (not in git) the four decks, from the Releases page
plan_audio.py                 1. reads the source decks, assigns voices, writes the clip plan
tts_batch.py                  2. synthesizes clips with the Gemini Batch API
postprocess_audio.py          3. trims, levels and encodes the clips to MP3
build_audio_decks.py          4. packages the English and Russian decks (genanki)
verify_decks.py               5. checks media references, note/card counts and clip durations
requirements.txt              Python dependencies
```

## Rebuilding

Requirements: Python 3.13, `ffmpeg` and `ffprobe` on the PATH, and a Google AI Studio API key stored in `~/.config/gcloud/gemini.key` (the path the script reads). The audio step is only needed when the Serbian text changes.

```bash
# 1. Put the unvoiced source decks from the Releases page into source/
mkdir -p source   # then copy Serbian_Frequency_complete.apkg and Serbian_Verb_Patterns.apkg here

# 2. Build
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python plan_audio.py                # writes _work_audio/ (deterministic)
.venv/bin/python tts_batch.py --chunk 2000    # costs money; resumable, skips clips already on disk
.venv/bin/python postprocess_audio.py
.venv/bin/python build_audio_decks.py         # writes the four .apkg files (English and Russian)
.venv/bin/python verify_decks.py
```

`build_audio_decks.py --lang ru` rebuilds only the Russian decks from the existing audio and `translations/ru/`.

`_work_audio/` (clip plans, raw audio, MP3s) is not tracked in git. Generated audio is cached in `_work_audio/raw/` and `_work_audio/audio/`.

## License

The project uses two licenses:

- **Content** (the decks and their audio, `README.md`, `README.ru.md`, `PROJECT_NOTES.md`, `skipped_entries.txt`, `translations/`): [CC BY-SA 4.0](LICENSE).
- **Code** (the Python scripts, `requirements.txt`, `.gitignore`): [MIT](LICENSE-MIT).
