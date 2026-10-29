> **Historical document.** Describes the old 104-note Edge deck (`Serbian_Frequency_Deck_v2_audio.apkg`), which is no longer published. The current decks are described in [`../../README.md`](../../README.md).

# Serbian Frequency Deck — Audio Edition

> **Looking for the current decks?** This README covers only the old 104-note
> Edge deck. The active project — the 2,293-note frequency deck and the 150-note
> verb deck, both with Gemini audio — is documented in
> [`PROJECT_NOTES.md`](PROJECT_NOTES.md).

`Serbian_Frequency_Deck_v2_audio.apkg` is a new Anki deck based on
`Serbian_Frequency_Deck_v1_top100.apkg`, with Serbian audio added to every word
and every example sentence.

## What is in the deck

- 104 notes (the source deck is labelled “top 100” but contains 104 notes).
- 312 audio clips: one for the headword and one for each of the two examples.
- Voice: **Microsoft `sr-RS-SophieNeural`** (female, neural Serbian voice,
  generated with `edge-tts`).
- Existing fields (word, Cyrillic, part of speech, meaning, examples,
  translations) are unchanged. Three audio fields were added:
  `Word_Audio`, `Example1_Audio`, `Example2_Audio`.
- Audio autoplays with the card; each clip also has a replay button.

## Why the examples were transliterated

The `sr-RS` neural voice mispronounces Serbian Latin text. For example, Latin
`kući` is read incorrectly, while Cyrillic `кући` is read correctly. The audio
for the examples is therefore generated from a Cyrillic transliteration of the
Latin sentences. The text displayed in the deck is unchanged.

## Import

Open Anki → **File → Import** → choose
`Serbian_Frequency_Deck_v2_audio.apkg`. It imports as a separate deck named
`Serbian::Frequency (Audio)`, so the original deck is left untouched.

## Regenerate

```bash
python3 -m venv .venv
.venv/bin/pip install edge-tts genanki
.venv/bin/python build_audio.py --voice sophie   # or --voice nicholas
.venv/bin/python build_deck.py
```

`build_audio.py` writes the audio plan and clips to `_work/`. `build_deck.py`
packages them into the `.apkg`. To use the male voice without overwriting this
deck:

```bash
.venv/bin/python build_audio.py --voice nicholas
.venv/bin/python build_deck.py --output Serbian_Frequency_Deck_v2_audio_nicholas.apkg
```

## Files

- `Serbian_Frequency_Deck_v2_audio.apkg` — the deck to import.
- `build_audio.py` — TTS generation, silence trimming, and loudness handling.
- `build_deck.py` — builds the Anki package from `_work/notes.json`.
- `_work/notes.json` — extracted notes plus audio metadata.
- `_work/audio/` — the final MP3 clips.
