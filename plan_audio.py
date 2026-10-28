#!/usr/bin/env python3
"""Plan the audio for both Serbian decks.

Reads the two source .apkg files and writes:

    _work_audio/clips.json        every clip to synthesize (unique key)
    _work_audio/freq/notes.json   notes + audio filenames for packaging
    _work_audio/verb/notes.json   same, for the verb-pattern deck

Voice scheme (the four voices that scored 0.99 on the Đ test):

    male pool    Charon, Fenrir
    female pool  Kore, Autonoe, Vindemiatrix

    frequency deck   word alternates by rank (odd male / even female),
                     Example1 always male, Example2 always female
    verb deck        the missing form (Answer) male, the sentence female

Voices are drawn at random per clip from the matching pool, with a fixed
seed so the plan is reproducible.

    python plan_audio.py
"""

from __future__ import annotations

import html
import json
import random
import re
import sqlite3
import tempfile
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "_work_audio"

FREQ_DECK = ROOT / "source" / "Serbian_Frequency_complete.apkg"
VERB_DECK = ROOT / "source" / "Serbian_Verb_Patterns.apkg"

MALE = ["Charon", "Fenrir"]
FEMALE = ["Kore", "Autonoe", "Vindemiatrix"]

SEED = 20261027
rng = random.Random(SEED)


def pick(pool: list[str]) -> str:
    return rng.choice(pool)


def clean(text: str) -> str:
    """Plain text for the TTS model: strip tags, entities and extra space."""
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def read_deck(path: Path) -> list[dict]:
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(path) as z:
            z.extract("collection.anki2", tmp)
        con = sqlite3.connect(Path(tmp) / "collection.anki2")
        model = list(json.loads(con.execute("select models from col").fetchone()[0]).values())[0]
        fields = [f["name"] for f in model["flds"]]
        rows = con.execute("select guid, tags, flds from notes order by id").fetchall()
        con.close()

    notes = []
    for guid, tags, flds in rows:
        values = flds.split("\x1f")
        note = dict(zip(fields, values))
        note["_guid"] = guid
        note["_tags"] = tags.split()
        notes.append(note)
    return notes


def plan_freq() -> dict:
    notes = read_deck(FREQ_DECK)
    out, clips = [], []
    for n in notes:
        rank = int(n["Rank"])
        word_voice = pick(MALE if rank % 2 == 1 else FEMALE)
        ex1_voice = pick(MALE)
        ex2_voice = pick(FEMALE)

        key = f"f{rank:04d}"
        names = {
            "word": f"{key}_{'m' if word_voice in MALE else 'f'}_word.mp3",
            "ex1": f"{key}_m_ex1.mp3",
            "ex2": f"{key}_f_ex2.mp3",
        }
        for field, voice, text in (
            ("word", word_voice, clean(n["Word"])),
            ("ex1", ex1_voice, clean(n["Example1"])),
            ("ex2", ex2_voice, clean(n["Example2"])),
        ):
            clips.append(
                {
                    "key": names[field][:-4],
                    "file": names[field],
                    "text": text,
                    "voice": voice,
                    "deck": "freq",
                }
            )

        out.append(
            {
                "rank": rank,
                "word": n["Word"],
                "cyrillic": n["Cyrillic"],
                "pos": n["POS"],
                "meaning": n["Meaning"],
                "example1": n["Example1"],
                "example1_en": n["Example1_EN"],
                "example2": n["Example2"],
                "example2_en": n["Example2_EN"],
                "word_audio": names["word"],
                "example1_audio": names["ex1"],
                "example2_audio": names["ex2"],
                "word_voice": word_voice,
                "example1_voice": ex1_voice,
                "example2_voice": ex2_voice,
                "guid": n["_guid"],
                "tags": n["_tags"],
            }
        )
    return {"notes": out, "clips": clips}


def plan_verb() -> dict:
    notes = read_deck(VERB_DECK)
    out, clips = [], []
    for idx, n in enumerate(notes, start=1):
        answer_voice = pick(MALE)
        sentence_voice = pick(FEMALE)
        key = f"v{idx:03d}"
        names = {
            "answer": f"{key}_m_answer.mp3",
            "sentence": f"{key}_f_sent.mp3",
        }
        for field, voice, text in (
            ("answer", answer_voice, clean(n["Answer"])),
            ("sentence", sentence_voice, clean(n["Sentence"])),
        ):
            clips.append(
                {
                    "key": names[field][:-4],
                    "file": names[field],
                    "text": text,
                    "voice": voice,
                    "deck": "verb",
                }
            )

        out.append(
            {
                "rank": n["Rank"],
                "verb": n["Verb"],
                "gloss": n["Gloss"],
                "person": n["Person"],
                "prompt": n["Prompt"],
                "answer": n["Answer"],
                "sentence": n["Sentence"],
                "english": n["English"],
                "paradigm": n["Paradigm"],
                "past": n["Past"],
                "pair": n["Pair"],
                "note": n["Note"],
                "answer_audio": names["answer"],
                "sentence_audio": names["sentence"],
                "answer_voice": answer_voice,
                "sentence_voice": sentence_voice,
                "guid": n["_guid"],
                "tags": n["_tags"],
            }
        )
    return {"notes": out, "clips": clips}


def main() -> None:
    WORK.mkdir(exist_ok=True)
    freq = plan_freq()
    verb = plan_verb()

    for name, data in (("freq", freq), ("verb", verb)):
        d = WORK / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "notes.json").write_text(
            json.dumps(
                {"count": len(data["notes"]), "notes": data["notes"]},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    clips = freq["clips"] + verb["clips"]
    keys = {c["key"] for c in clips}
    assert len(keys) == len(clips), "duplicate clip keys"
    (WORK / "clips.json").write_text(
        json.dumps(clips, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"frequency : {len(freq['notes'])} notes, {len(freq['clips'])} clips")
    print(f"verbs     : {len(verb['notes'])} notes, {len(verb['clips'])} clips")
    print(f"total     : {len(clips)} clips, {sum(len(c['text']) for c in clips)} chars")

    voices = Counter((c["deck"], c["voice"]) for c in clips)
    for deck in ("freq", "verb"):
        parts = {v: voices[(deck, v)] for v in MALE + FEMALE if voices[(deck, v)]}
        print(f"  {deck} voices: {parts}")

    chars = Counter(c["text"] for c in clips)
    dup = [(t, n) for t, n in chars.items() if n > 1]
    print(f"  repeated texts: {len(dup)}")
    for t, n in sorted(dup, key=lambda x: -x[1])[:5]:
        print(f"    {n}x {t!r}")

    special = sorted({ch for c in clips for ch in c["text"] if not ch.isalnum() and ch not in " .,!?;:'\"-–—()"})
    print(f"  unusual characters: {special}")
    print(f"  empty texts: {sum(1 for c in clips if not c['text'].strip())}")


if __name__ == "__main__":
    main()
