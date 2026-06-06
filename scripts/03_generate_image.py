#!/usr/bin/env python3
"""Step 3: Generate images from storyboard using SenseNova API."""

import argparse
import json
import os
import sys
import time
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config.settings import (
    SN_IMAGE_API_KEY,
    SN_BASE_URL,
    SN_IMAGE_MODEL,
    IMAGE_TIMEOUT,
    SKIP_IMAGE_TYPES,
)


def load_script(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt(scene: dict) -> str:
    """Build image prompt from scene."""
    parts = []

    if "img_prompt" in scene and scene["img_prompt"]:
        parts.append(scene["img_prompt"])
    elif "description" in scene:
        parts.append(scene["description"])

    if "character" in scene and scene["character"]:
        parts.append(scene["character"])

    style = (
        "Anime style, digital illustration, soft lighting, cinematic composition, "
        "detailed background, emotional storytelling, high quality, 8k"
    )
    parts.append(style)

    parts.append("NO TEXT, NO WORDS, NO LETTERS, NO ENGLISH anywhere in the image")

    return ". ".join(parts)


def generate_image(prompt: str, output_path: str, scene_id: str) -> bool:
    """Generate a single image via SenseNova."""
    if not SN_IMAGE_API_KEY:
        print(f"[!] SN_IMAGE_API_KEY not set, skipping {scene_id}")
        return False

    url = f"{SN_BASE_URL}/images/generations"
    headers = {
        "Authorization": f"Bearer {SN_IMAGE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": SN_IMAGE_MODEL,
        "prompt": prompt,
        "size": "2K",
        "aspect_ratio": "16:9",
    }

    try:
        resp = requests.post(
            url, headers=headers, json=payload, timeout=IMAGE_TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()

        image_url = (
            data.get("data", [{}])[0].get("url")
            or data.get("data", [{}])[0].get("image_url")
        )

        if image_url:
            img_resp = requests.get(image_url, timeout=60)
            img_resp.raise_for_status()
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(img_resp.content)
            print(f"[OK] {scene_id} -> {output_path}")
            return True

        print(f"[!] No image URL in response for {scene_id}: {data}")
        return False

    except requests.exceptions.Timeout:
        print(f"[TIMEOUT] {scene_id}")
        return False
    except Exception as e:
        print(f"[ERROR] {scene_id}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--story-name", required=True)
    args = parser.parse_args()

    scenes = load_script(args.script)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    success = 0
    failed = 0

    for scene in scenes:
        scene_id = scene.get("id", "unknown")
        scene_type = scene.get("type", "").lower()

        if scene_type in SKIP_IMAGE_TYPES:
            print(f"[SKIP] {scene_id} (type={scene_type}, no image needed)")
            continue

        output_path = str(output_dir / f"{scene_id}.png")
        if os.path.exists(output_path):
            print(f"[EXISTS] {scene_id}")
            success += 1
            continue

        prompt = build_prompt(scene)
        if generate_image(prompt, output_path, scene_id):
            success += 1
            time.sleep(1)
        else:
            failed += 1
            time.sleep(2)

    print(f"\n=== Image Generation Done: {success} success, {failed} failed ===")


if __name__ == "__main__":
    main()
