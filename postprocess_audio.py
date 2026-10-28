#!/usr/bin/env python3
"""Post-process the raw Gemini WAVs into deck-ready MP3s.

Each clip gets the same treatment:

  * trim leading/trailing silence,
  * a static gain so every clip sits at the same speech level, regardless of
    which of the five voices spoke it (raw peaks vary by ~11 dB across voices),
  * a small lead-in and tail pad so Anki's replay button never clips the onset.

Level matching is done from the raw signal: RMS over voiced frames, then the
gain is capped so the peak stays at or below -1.5 dBFS.

    python postprocess_audio.py            # all decks
    python postprocess_audio.py --deck verb
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "_work_audio"
RAW = WORK / "raw"
AUDIO = WORK / "audio"

TARGET_RMS_DB = -20.0
PEAK_CEIL_DB = -1.5
MAX_GAIN_DB = 15.0
MIN_GAIN_DB = -15.0


def levels(path: Path) -> tuple[float, float]:
    """RMS of voiced frames and the peak, both in dBFS."""
    with wave.open(str(path)) as w:
        sr = w.getframerate()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    if data.size == 0:
        return -90.0, -90.0

    x = data.astype(np.float32) / 32768.0
    peak = float(np.max(np.abs(x)))
    frame = max(1, int(0.02 * sr))
    usable = x[: (len(x) // frame) * frame].reshape(-1, frame)
    rms = np.sqrt(np.mean(usable**2, axis=1))
    voiced = rms[rms > 10 ** (-45 / 20)]
    level = float(np.sqrt(np.mean(voiced**2))) if voiced.size else float(np.sqrt(np.mean(x**2)))

    to_db = lambda v: 20 * math.log10(max(v, 1e-9))
    return to_db(level), to_db(peak)


def gain_for(path: Path) -> float:
    level, peak = levels(path)
    gain = TARGET_RMS_DB - level
    gain = min(gain, PEAK_CEIL_DB - peak)
    return max(MIN_GAIN_DB, min(MAX_GAIN_DB, gain))


def encode(src: Path, dest: Path) -> None:
    gain = gain_for(src)
    flt = (
        "silenceremove=start_periods=1:start_duration=0.02:start_threshold=-60dB,"
        "areverse,"
        "silenceremove=start_periods=1:start_duration=0.02:start_threshold=-60dB,"
        "areverse,"
        f"volume={gain:.2f}dB,"
        "adelay=80|80,apad=pad_dur=0.15"
    )
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src),
         "-af", flt, "-ac", "1", "-ar", "24000", "-b:a", "64k", str(dest)],
        check=True,
    )


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", choices=["freq", "verb", "all"], default="all")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    AUDIO.mkdir(parents=True, exist_ok=True)
    decks = ["freq", "verb"] if args.deck == "all" else [args.deck]

    jobs, missing = [], []
    for deck in decks:
        notes = json.loads((WORK / deck / "notes.json").read_text(encoding="utf-8"))["notes"]
        for note in notes:
            for field in ("word_audio", "example1_audio", "example2_audio",
                          "answer_audio", "sentence_audio"):
                name = note.get(field)
                if not name:
                    continue
                src = RAW / f"{name[:-4]}.wav"
                if not src.exists():
                    missing.append(name)
                    continue
                jobs.append((src, AUDIO / name))

    print(f"{len(jobs)} clips to encode, {len(missing)} raw files missing")
    if missing:
        print(f"  first missing: {missing[:5]}")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(lambda j: encode(*j), jobs))

    total = 0.0
    bad = []
    for deck in decks:
        notes = json.loads((WORK / deck / "notes.json").read_text(encoding="utf-8"))["notes"]
        for note in notes:
            for field in ("word_audio", "example1_audio", "example2_audio",
                          "answer_audio", "sentence_audio"):
                name = note.get(field)
                if not name:
                    continue
                p = AUDIO / name
                if not p.exists() or p.stat().st_size < 1000:
                    bad.append((name, "missing"))
                    continue
                d = duration(p)
                total += d
                if d < 0.15 or d > 25:
                    bad.append((name, f"{d:.2f}s"))

    print(f"encoded {len(jobs)} clips, {total / 60:.1f} min of audio")
    if bad:
        for item in bad[:10]:
            print("  BAD:", item)
        raise SystemExit(f"{len(bad)} clip(s) failed verification")
    print("all clips verified")


if __name__ == "__main__":
    main()
