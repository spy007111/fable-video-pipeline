#!/usr/bin/env python3
"""Step 4: Generate audio clips from voiceover script using Edge-TTS."""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config.settings import DEFAULT_VOICE


async def synthesize_one(text: str, output_path: str, voice: str) -> None:
    """Call edge-tts via its Communicate API."""
    try:
        from edge_tts import Communicate
    except ImportError:
        raise RuntimeError("edge-tts not installed. Run: pip install edge-tts")

    communicate = Communicate(text, voice)
    await communicate.save(output_path)


async def main_async(args):
    with open(args.script, "r", encoding="utf-8") as f:
        script = json.load(f)

    audio_dir = Path(args.output_dir)
    audio_dir.mkdir(parents=True, exist_ok=True)

    lang = args.lang
    voice = args.voice

    tasks = []
    scene_ids = []

    for scene in script:
        scene_id = scene.get("id", "unknown")
        scene_type = scene.get("type", "").lower()

        if scene_type in ("title", "quote"):
            continue

        text = scene.get(lang, "")
        if not text:
            continue

        output_path = str(audio_dir / f"{scene_id}.mp3")

        if os.path.exists(output_path):
            continue

        tasks.append(synthesize_one(text, output_path, voice))
        scene_ids.append(scene_id)

    if tasks:
        await asyncio.gather(*tasks)
        print(f"[OK] Generated {len(tasks)} audio clips")

    # Write durations
    durations = {}
    for audio_file in sorted(audio_dir.glob("*.mp3")):
        key = audio_file.stem
        try:
            import subprocess, re
            result = subprocess.run(
                [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(audio_file),
                ],
                capture_output=True, text=True
            )
            durations[key] = float(result.stdout.strip())
        except Exception:
            durations[key] = 0.0

    dur_file = audio_dir / "audio_durations.json"
    with open(dur_file, "w", encoding="utf-8") as f:
        json.dump(durations, f, indent=2, ensure_ascii=False)
    print(f"[OK] Audio durations -> {dur_file}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    parser.add_argument("--lang", default="en", choices=["en", "cn", "en_primary"])
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
