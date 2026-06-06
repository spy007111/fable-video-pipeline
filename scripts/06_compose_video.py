#!/usr/bin/env python3
"""Step 6: Compose final video from renders, audio, and subtitles."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config.settings import WIDTH, HEIGHT, FPS, PIX_FMT


def load_script(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_time(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m:02d}:{s:05.2f}"


def get_clips(render_dir: str, audio_dir: str, script: list) -> list:
    """Pair each scene with its render and audio."""
    clips = []
    render_d = Path(render_dir)
    audio_d = Path(audio_dir)

    for scene in script:
        scene_id = scene.get("id", "unknown")
        scene_type = scene.get("type", "").lower()
        if scene_type in ("title", "quote", "moral"):
            continue

        img = render_d / f"{scene_id}.png"
        audio = audio_d / f"{scene_id}.mp3"

        if not img.exists() or not audio.exists():
            print(f"[WARN] Missing assets for {scene_id}: img={img.exists()}, audio={audio.exists()}")
            continue

        clips.append({"id": scene_id, "img": str(img), "audio": str(audio)})

    return clips


def make_subclip(clip: dict, out_path: str, subtitle_ass: str, font_path: str) -> bool:
    """Build single scene clip with ASS subtitles burned in."""
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    # Probe audio duration
    dur_proc = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            clip["audio"],
        ],
        capture_output=True, text=True
    )
    try:
        duration = float(dur_proc.stdout.strip())
    except Exception:
        duration = 3.0

    abs_font = Path(font_path).resolve()
    abs_ass = Path(subtitle_ass).resolve()

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", clip["img"],
        "-i", clip["audio"],
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        "-pix_fmt", PIX_FMT,
        "-shortest",
        "-vf", (
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
            f"format={PIX_FMT},"
            f"subtitles={abs_ass}:force_style='FontName={abs_font}@\\'Noto Sans CJK SC\\'',"
            f"channelsplit=channel_layout=stereo"
        ),
        "-t", str(duration),
        out_path,
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"[OK] Clip {clip['id']} -> {out_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Clip {clip['id']}: {e.stderr.decode('utf-8', errors='ignore')[:200]}")
        return False


def concat_clips(clips: list, output_path: str, clips_dir: str) -> bool:
    """Concatenate all clips using ffmpeg concat demuxer."""
    list_file = Path(clips_dir) / "_concat_list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for c in clips:
            f.write(f"file '{c['out']}'\n")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        "-movflags", "+faststart",
        output_path,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"[OK] Final video -> {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Concat failed: {e.stderr.decode('utf-8', errors='ignore')[:200]}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-dir", required=True)
    parser.add_argument("--audio-dir", required=True)
    parser.add_argument("--subtitle-ass", required=True)
    parser.add_argument("--script", required=True)
    parser.add_argument("--output-path", required=True)
    args = parser.parse_args()

    # Resolve font
    from src.config.settings import FONT_PATHS
    font_path = None
    for p in FONT_PATHS:
        if Path(p).exists():
            font_path = str(p)
            break
    if not font_path:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    script = load_script(args.script)
    clips_raw = get_clips(args.render_dir, args.audio_dir, script)

    clips_out = []
    out_dir = str(Path(args.output_path).parent / "clips")
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    for clip in clips_raw:
        out_path = str(Path(out_dir) / f"{clip['id']}.mp4")
        if Path(out_path).exists():
            clips_out.append({"id": clip["id"], "out": out_path})
            continue
        if make_subclip(clip, out_path, args.subtitle_ass, font_path):
            clips_out.append({"id": clip["id"], "out": out_path})
        else:
            print(f"[WARN] Skipping {clip['id']} due to errors")

    if not clips_out:
        print("[ERROR] No clips generated. Aborting.")
        sys.exit(1)

    concat_clips(clips_out, args.output_path, out_dir)


if __name__ == "__main__":
    main()
