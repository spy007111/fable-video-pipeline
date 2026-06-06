#!/usr/bin/env python3
"""Step 5: Generate ASS subtitles from voiceover script + audio durations."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config.settings import FONT_PATHS


def find_font() -> str | None:
    for p in FONT_PATHS:
        if Path(p).exists():
            return p
    return None


def load_script(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_durations(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def build_ass(script: list, durations: dict, story_name: str, font_path: str) -> str:
    """Build ASS V4+ subtitle content with drawtext fallback info."""
    lines = []
    lines.append("[Script Info]")
    lines.append("ScriptType: v4.00+")
    lines.append("PlayResX: 1920")
    lines.append("PlayResY: 1080")
    lines.append("")

    lines.append("[V4+ Styles]")
    lines.append(
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding"
    )
    lines.append(
        f"Style: Chinese,{font_path},36,&H00FFFFFF,&H000000FF,"
        f"&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2,1,2,10,10,50,1"
    )
    lines.append(
        f"Style: English,Noto Sans CJK SC,28,&H00CCCCCC,&H000000FF,"
        f"&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2,1,2,10,10,65,1"
    )
    lines.append("")
    lines.append("[Events]")
    lines.append(
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, "
        "MarginV, Effect, Text"
    )

    t = 0.0
    for scene in script:
        scene_id = scene.get("id", "unknown")
        scene_type = scene.get("type", "").lower()

        if scene_type in ("title", "quote", "moral"):
            continue

        en_text = scene.get("en", "")
        cn_text = scene.get("cn", "")

        if not en_text and not cn_text:
            continue

        dur_key = scene_id
        duration = durations.get(dur_key, max(len(en_text) * 0.08, 2.0))

        start = t
        end = t + duration
        t = end

        start_str = f"{int(start // 60)}:{start % 60:05.2f}"
        end_str = f"{int(end // 60)}:{end % 60:05.2f}"

        # Clean text
        en_clean = en_text.replace("\n", " ").replace("\r", " ")
        cn_clean = cn_text.replace("\n", " ").replace("\r", " ")

        if en_clean:
            lines.append(
                f"Dialogue: 0,{start_str},{end_str},English,,0,0,0,,"
                f"{{{en_clean}}}"
            )
        if cn_clean:
            lines.append(
                f"Dialogue: 0,{start_str},{end_str},Chinese,,0,0,0,,"
                f"{{{cn_clean}}}"
            )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True)
    parser.add_argument("--audio-dir", required=True)
    parser.add_argument("--output-ass", required=True)
    parser.add_argument("--story-name", required=True)
    args = parser.parse_args()

    script = load_script(args.script)
    dur_file = Path(args.audio_dir) / "audio_durations.json"
    durations = load_durations(str(dur_file))
    font_path = find_font() or "NotoSansCJK-Regular.ttc"

    ass_content = build_ass(script, durations, args.story_name, font_path)
    Path(args.output_ass).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_ass, "w", encoding="utf-8") as f:
        f.write(ass_content)
    print(f"[OK] ASS subtitles -> {args.output_ass}")


if __name__ == "__main__":
    main()
