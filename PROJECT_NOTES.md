# Serbian deck project — handover notes

Last updated: 2026-10-28

Everything needed to rebuild, repair or extend the two voiced decks without
reconstructing the reasoning from scratch. Read the **TL;DR** first; the rest
is reference.

---

## TL;DR

Two importable Anki decks exist, built from the user's unvoiced source decks:

| Output | Size | Notes | Clips | Audio |
|---|---|---|---|---|
| `Serbian_Frequency.apkg` | 75.7 MB | 2,293 | 6,879 | 143.8 min |
| `Serbian_Verbs.apkg` | 3.3 MB | 150 | 300 | 6.1 min |
| `Serbian_Frequency_RU.apkg` | 72.3 MB | 2,293 | 6,879 (same clips) | 143.8 min |
| `Serbian_Verbs_RU.apkg` | 3.2 MB | 150 | 300 (same clips) | 6.1 min |

The Russian decks are the same cards with English glosses and translations
replaced by Russian (see "Russian decks" below). They reuse the English decks'
audio files, byte for byte, so no clips were synthesized for them.

Voices are Google **Gemini TTS** (`gemini-3.8-flash-tts`, `sr-RS`), five of the
30 prebuilt voices, drawn at random per clip with a fixed seed.

The unvoiced source decks are **never modified** — the audio decks are separate
note types with new IDs and derived GUIDs.

---

## Source decks (inputs, untouched)

| File | Notes | Note type | Role |
|---|---|---|---|
| `source/Serbian_Frequency_complete.apkg` | 2,293 | `Serbian Frequency (word→meaning)` | unvoiced frequency deck (input to `plan_audio.py`) |
| `source/Serbian_Verb_Patterns.apkg` | 150 | `Serbian Verb Pattern (gap)` | unvoiced verb deck, 50 verbs × 3 persons (input to `plan_audio.py`) |

2500-ish words are actually 2,293 notes. The verb deck is 50 verbs × 3 persons
= 150 notes (only 3 of the persons are drilled per verb).

### Older lineage — archived outside the repo

The 104- and 1,629-note Edge-era decks and their scripts were moved out of the
repository to `../Serbian_archive/` (not published). They are superseded by the
audio decks above.

---

## Voice decisions

### Provider

**Google Gemini TTS via AI Studio API key.** Chosen after ruling out:

- **Edge TTS** — `sr-RS` has only Sophie/Nicholas, robotic, and needs Cyrillic
  transliteration.
- **Azure** — same two voices as Edge.
- **Groq / Orpheus** — English + Arabic only.
- **ElevenLabs / Soniox** — not needed once Gemini billing worked.

Key file: `~/.config/gcloud/gemini.key` (40 bytes, `AIza` prefix, mode 600).
Never print it.

### The 30 voices

Complete prebuilt roster for the model. Gender is **not** in the AI Studio docs;
the authoritative table is the Google Cloud Gemini-TTS voice table:
<https://docs.cloud.google.com/text-to-speech/docs/gemini-tts>

- female (14): Achernar, Aoede, Autonoe, Callirrhoe, Despina, Erinome, Gacrux,
  Kore, Laomedeia, Leda, Pulcherrima, Sulafat, Vindemiatrix, Zephyr
- male (16): Achird, Algenib, Algieba, Alnilam, Charon, Enceladus, Fenrir,
  Iapetus, Orus, Puck, Rasalgethi, Sadachbia, Sadaltager, Schedar, Umbriel,
  Zubenelgenubi

**Do not infer gender from pitch.** Gacrux (~147 Hz) and Pulcherrima (~144 Hz)
are female contralto voices and land in male range. An earlier pipeline
classified by an F0 threshold and got both wrong.

### The 0.99 group (used for the decks)

All 30 voices were auditioned on three Serbian samples and machine-transcribed.
Only five produced a recognisably voiced **đ** in `Đaci će čitati…` and scored
0.99:

```
male    Charon, Fenrir
female  Kore, Autonoe, Vindemiatrix
```

The other 25 rendered đ as ć / dj / dž / gi / gj. The deck has many `đ` words,
so only these five are used.

### Assignment rule (implemented in `plan_audio.py`)

- frequency deck: `Example1` **male**, `Example2` **female**,
  headword alternates by rank parity (odd → male, even → female)
- verb deck: the missing form (`Answer`) **male**, the full sentence **female**
- verb lemma is *not* voiced — it is already shown on the front as a cue
- random per clip, `random.Random(20261027)`

Re-running with the same seed reproduces the exact same voice assignment.

### Speaker gender (fixed 2026-10-29)

Serbian first-person forms carry the speaker's gender ("Napravila sam kolač",
"Nisam uveren"). Voices were first assigned by slot only, so 79 sentences were
spoken by a gender that did not match their voice (77 male speakers read by a
female voice, 2 female speakers read by a male voice).

- `speaker_gender.tsv`: for each affected note, the speaker of `Example1` and
  `Example2` (`M`, `F`, or `N` = neutral). Checked by hand; the sentences
  were found by pattern (sam/nisam + participle or adjective) and then read.
- `plan_audio.py` applies, per note:
  1. keep the slots if both examples fit (`Example1` male, `Example2` female;
     neutral fits anywhere);
  2. otherwise swap the two examples (text, English translation and Russian
     translation move together) if that fits — 73 notes;
  3. otherwise keep the order and give the slot that does not fit a voice of the
     right gender — 6 notes where both sentences are spoken by a man, so
     `Example2` uses a male voice (`f…_m_ex2`). These draws use their own seeded
     generator (`SEED + 1`), so the main draws, and every other clip, are unchanged.
- Result: 146 clips changed text (73 notes × 2), 6 clips changed voice. All
  other clips and all verb clips are byte-identical to the previous plan.
- The archived audio from before the fix is in `../Serbian_archive/faulty_audio/2026-10-29/`
  (152 raw WAVs and MP3s, plus the old plan). The old decks are in
  `../Serbian_archive/previous_decks/2026-10-29/`.

The gender check covers the first-person forms it could identify. It does not
cover every gendered form in the deck; a native speaker should listen to a sample.

---

## Pipeline

Five scripts, run in this order. Each stage is resumable and skips work already
on disk.

### 1. `plan_audio.py`

Reads both `.apkg` files, strips HTML from the `Sentence` field, assigns voices,
writes the work plan.

```
.venv/bin/python plan_audio.py
```

Outputs:

- `_work_audio/clips.json` — the 7,179 clips to synthesize
  (`key`, `file`, `text`, `voice`, `deck`)
- `_work_audio/freq/notes.json` — notes + audio filenames + voices + guid/tags
- `_work_audio/verb/notes.json` — same

Clip key / filename scheme:

```
f{rank:04d}_{m|f}_{word|ex1|ex2}.mp3     frequency deck, e.g. f0001_m_word.mp3
v{index:03d}_{m_answer|f_sent}.mp3       verb deck,      e.g. v001_f_sent.mp3
```

### 2. `tts_batch.py`

Submits clips to the **Batch API** (`google-genai` SDK), polls, downloads the
result JSONL, decodes base64 WAVs into `_work_audio/raw/<key>.wav`.

```
.venv/bin/python tts_batch.py --chunk 2000      # full run
.venv/bin/python tts_batch.py --limit 8 --chunk 8   # pilot
```

- resumable: only clips without a raw WAV are submitted
- chunked so a failure costs one chunk, not the run
- job metadata is not persisted; job ids appear in the log only
- results land in `_work_audio/batch/<tag>.result.jsonl` (~200 MB per 2,000)

### 3. `postprocess_audio.py`

Raw WAV → deck MP3 with silence trim, level matching, lead-in and tail pad.

```
.venv/bin/python postprocess_audio.py
```

Writes `_work_audio/audio/*.mp3`, then ffprobes every clip and fails if any is
missing or outside 0.15–25 s.

### 4. `build_audio_decks.py`

Packages the decks with genanki: English and Russian by default.

```
.venv/bin/python build_audio_decks.py
# or: --deck freq|verb   --lang en|ru   --outdir DIR   --workdir DIR
```

Writes `Serbian_Frequency.apkg`, `Serbian_Verbs.apkg`, `Serbian_Frequency_RU.apkg`
and `Serbian_Verbs_RU.apkg` in the repository root. `--lang ru` rebuilds only the
Russian decks from `translations/ru/`.

### 5. `verify_decks.py`

Structural check of the packaged files: sound references resolve, no
unreferenced media, note/card counts match, no clips under 0.25 s.

```
.venv/bin/python verify_decks.py
```

---

## Russian decks

### Files

- `translations/ru/freq.tsv`: `rank`, `meaning_ru`, `example1_ru`, `example2_ru`.
  One row per vocabulary note, keyed by rank (ranks are unique).
- `translations/ru/verbs.tsv`: `guid`, `gloss_ru`, `english_ru`, `note_ru`, `pair_ru`.
  One row per verb note, keyed by the note GUID (verb ranks repeat across a verb's
  three cards, so rank is not a key).

Part-of-speech labels are not in the TSV: `build_audio_decks.py` maps the English
POS to Russian with the `POS_RU` table (`сущ.`, `гл.`, `нар.`, `прил.`, …).
Serbian forms (the verb in `pair_ru`, the forms in `note_ru`, the pronoun cues in
`Person`) are kept as written.

### How they were made

The English text was translated in nine parallel batches (eight of 288 and one
of 277 vocabulary rows, plus one batch of 150 verb rows). Each batch read its
input and wrote its output file directly; the batches shared a glossary
(*yes* = да, *I* = я, *to be* = быть, *pf* = сов. вид, *impf* = несов. вид) and
were told to use the Serbian sentences only to resolve ambiguity.

Checks run before the decks were built:

- row count and column count per file; ranks 1–2293 present once each;
- no empty translation where the English is non-empty;
- every translated field contains Cyrillic (the only Latin left was *Golf*, a car
  model name; it is now *Гольф*);
- a manual read of the first 20 vocabulary rows and a random sample of others.

The translations have **not** been reviewed by a native Russian speaker.

### Building and checking

```
.venv/bin/python build_audio_decks.py --lang ru
.venv/bin/python verify_decks.py Serbian_Frequency_RU.apkg Serbian_Verbs_RU.apkg
```

The Russian note types have their own IDs and GUID prefixes, so they can be
imported next to the English decks. Their media filenames and contents are
identical to the English decks, so shared filenames always refer to the same file.

### Changes of 2026-10-29

- Translation fixes: duplicate senses (ranks 7, 20, 23, 264, 393, 585), the
  car model *Golf* (1131), and POS labels inside meanings (1448, 1554, 1665,
  1703) were corrected. Rank 393 is now `ни … ни; и не`.
- Speaker-gender voice fix (see "Speaker gender" above).
- Tags: the 23 frequency band tags (`freq_0001-0100` …) and the `audio` tag
  were removed. The vocabulary deck has no tags. The verb deck keeps its source
  tags (`verbs`, `irregular`, `impf`, `pf`).
- The four published decks were rebuilt; the previous versions are archived.

## Fixed constants

Change these only deliberately.

| Thing | Value |
|---|---|
| Model | `gemini-3.8-flash-tts` |
| Language code | `sr-RS` |
| Script sent to TTS | **Latin**, exactly as displayed (no transliteration) |
| Prompt | bare target text only — any instruction text gets read aloud |
| Voice seed | `20261027` |
| Frequency model ID / deck ID | `1700000000021` / `1700000000022` |
| Verb model ID / deck ID | `1700000000031` / `1700000000032` |
| Deck names | `Serbian::Frequency (Audio)`, `Serbian::Verbs (Audio)` |
| GUID prefixes | `sr_freq_audio`, `sr_verb_audio` |
| Russian frequency model ID / deck ID | `1700000000041` / `1700000000042` |
| Russian verb model ID / deck ID | `1700000000051` / `1700000000052` |
| Russian deck names | `Serbian-Russian::Frequency (Audio)`, `Serbian-Russian::Verbs (Audio)` |
| Russian GUID prefixes | `sr_freq_audio_ru`, `sr_verb_audio_ru` |

GUIDs are `genanki.guid_for(prefix, original_note_guid)`, so re-importing a
rebuilt deck updates its own notes rather than duplicating, and can never
collide with the unvoiced originals.

### Audio spec

```
filter: silenceremove(-60dB, both ends via areverse)
        volume=<per-clip gain>dB
        adelay=80|80
        apad=pad_dur=0.15
codec:  MP3, mono, 24 kHz, 64 kbps
```

Level matching (`postprocess_audio.py`) targets **−20 dBFS RMS** over voiced
frames, caps the peak at **−1.5 dBFS**, clamps gain to ±15 dB. Raw peaks across
the five voices spanned 5.7 dB; the output spans 0.5 dB.

---

## Cost and API behaviour

Exact usage from the batch result files:

```
278,236 audio output tokens + 35,841 prompt tokens
batch price  ≈ $1.26      live price ≈ $2.51
total incl. one wasted duplicate job ≈ $1.46
```

Facts learned the hard way:

- **Free tier is 10 requests per day** per model (not 3/min — the 3/min 429 is
  a different quota). Unusable. Billing via AI Studio prepay moves the project
  to Tier 1 with ~10 requests/minute live and no daily cap.
- **Batch API is 50% price** and the right tool above a few hundred clips.
  Live would have been ~12 hours at 10 req/min.
- **Batch queue time is wildly variable.** Observed chunk durations for the same
  2,000-clip size: 3.8 min, 64.5 min, 3.1 min. One 1,171-clip job sat 65 minutes
  without starting; a duplicate submitted alongside finished **in 1.7 minutes**.
  If a job shows no `update_time` change for ~30 min, submit a duplicate and
  cancel the stuck one.
- **Location gating is real.** With a VPN active the API returns
  `400 FAILED_PRECONDITION: User location is not supported for the API use.`
  on *every* endpoint including `models.list`. Turning the VPN off fixed it.
- Batch jobs bill on completion; Google's billing/credit display lags by up to a
  day, so a zero balance display does not mean nothing is happening.

---

## Verification results (2026-10-28)

```
Serbian_Frequency.apkg   2,293 notes / 2,293 cards / 6,879 media
Serbian_Verbs.apkg         150 notes /   150 cards /   300 media
text fields differing from source:       0 (all 9 and 12 fields)
example1 male / example2 female:         all notes
headword alternation violations:         0   (3,440 / 3,439)
verb answer male / sentence female:      all 150
clips under 0.25 s:                      0
```

Voice usage, frequency deck: Charon 1,798 · Fenrir 1,642 · Kore 1,162 ·
Autonoe 1,195 · Vindemiatrix 1,082.

---

## Gotchas

- **Do not add instruction or style text to the TTS prompt.** Gemini reads it
  aloud verbatim. Send only the bare Serbian text.
- **Latin works.** Unlike Edge/Azure, Gemini reads `Đaci će čitati…` correctly;
  no Cyrillic transliteration step is needed (unlike the old 104-note deck).
- **Whisper is unreliable on isolated words** (`da` → "Na", `tokom` → "talvez").
  Judge ASR only on full sentences, and use it as a signal, not a verdict.
- **Whisper sometimes answers in Cyrillic** for Serbian, which produces a fake
  0.00 similarity score against Latin text. Transliterate before scoring.
- **Single-letter headwords** (`i`, `u`, `a`, `o`, ranks 5/6/19/22) are correct
  as-is; they are pronounced as their letter sounds.
- **`ffprobe` under-reports the duration of Gemini's raw WAVs** by ~1.6%
  (header vs data chunk). Use trimmed MP3 durations for reporting.
- **The 0.99 group was measured on one sentence.** If a new batch of text comes
  in with heavy `đ`/`ć`, spot-check again rather than assuming.

---

## Common repairs

### Re-render a single clip

Delete its raw WAV and the postprocessed MP3, then re-run stages 2–4. The batch
script only submits what is missing.

```bash
rm _work_audio/raw/f1956_f_word.wav _work_audio/audio/f1956_f_word.mp3
.venv/bin/python tts_batch.py --chunk 50
.venv/bin/python postprocess_audio.py
.venv/bin/python build_audio_decks.py
```

Note: re-submitting changes the audio for that clip but keeps the same voice,
because the plan (and its seed) is unchanged.

### Change a voice for the whole deck

Edit `MALE` / `FEMALE` in `plan_audio.py`, then delete the affected raws and
MP3s and re-run 1–4. Changing the seed reshuffles every assignment.

### Add notes to the source deck

Re-export the source `.apkg`, drop it in this folder, then run 1–5. Existing
clips are cached by key, so only new notes cost money.

### Rebuild the decks without touching audio

```bash
.venv/bin/python build_audio_decks.py && .venv/bin/python verify_decks.py
```

---

## The voice audition site (Go)

`voiceserver/` serves all 30 voices × 3 samples as a listening page with
male/female filters and sequential audition.

```bash
cd voiceserver && go run . -addr :8080 -data ../_work1629/bakeoff
```

Prints LAN URLs at startup; re-reads `manifest.json` on every request.
Assets come from `render_all_voices.py` (90 clips) and are **not** needed for
the decks.

---

## Disk usage and cleanup

| Path | Size | Safe to delete? |
|---|---|---|
| `_work_audio/raw/` | ~700 MB | yes, re-synthesizes (costs money) |
| `_work_audio/batch/` | ~1.5 GB | moved to `../Serbian_archive/scratch/`; regenerable from `raw/`, not needed |
| `_work_audio/audio/` | 70 MB | yes, regenerated from raw |
| `_work_audio/clips.json`, `_work_audio/*/notes.json` | small | regenerated by `plan_audio.py` (byte-identical on rerun); needed by the packager |
| `../Serbian_archive/` | — | old Edge deck, early probes, audition assets (outside the repo) |

Deleting `_work_audio/audio/` forces a full ffmpeg re-encode (~2 min, free).
Deleting `raw/` forces re-billing every clip.

---

## Environment

- macOS, Python 3.13 at `.venv` with `genanki`, `numpy`, `google-genai`, `edge-tts`
- Go 1.27 for `voiceserver`
- ffmpeg / ffprobe on PATH
- Whisper for QA:

  ```
  /Library/Frameworks/Python.framework/Versions/3.11/bin/whisper \
      --model small --language sr <files> --output_format txt
  ```

- Git: this folder is the repository. Decks (`*.apkg`) are distributed as
  GitHub Release assets; `_work_audio/` is ignored and regenerated by
  `plan_audio.py` (deterministic).
