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

- frequency deck: `Example1` always **male**, `Example2` always **female**,
  headword alternates by rank parity (odd → male, even → female)
  → 3,440 male / 3,439 female clips
- verb deck: the missing form (`Answer`) **male**, the full sentence **female**
- verb lemma is *not* voiced — it is already shown on the front as a cue
- random per clip, `random.Random(20261027)`

Re-running with the same seed reproduces the exact same voice assignment.

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

Packages both decks with genanki.

```
.venv/bin/python build_audio_decks.py
# or: --deck freq|verb   --outdir DIR   --workdir DIR
```

### 5. `verify_decks.py`

Structural check of the packaged files: sound references resolve, no
unreferenced media, note/card counts match, no clips under 0.25 s.

```
.venv/bin/python verify_decks.py
```

---

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
