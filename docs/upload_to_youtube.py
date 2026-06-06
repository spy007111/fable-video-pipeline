#!/usr/bin/env python3
"""上传寓言视频到 YouTube @aimorningread"""

import os
import json
from datetime import datetime

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import ResumableUploadError

TOKEN_PATH = "/root/token.json"
BASE_DIR = "/root/fable-video-pipeline/docs"

VIDEOS = [
    {
        "file": "lan-yu-chong-shu_final_v4.mp4",
        "title": "滥竽充数 | The Cook Who Pretended to Play | Chinese Fable",
        "description": """滥竽充数 | The Cook Who Pretended to Play

A story from ancient China about a man who pretended to be a skilled musician to earn a living, but was eventually exposed.

📖 Story: A ruler loved large orchestras. Hundreds of musicians were hired with generous pay. One untalented man, Nan Guo, joined by luck. When the ruler demanded solo performances, he fled in panic.

💡 Moral: Those who lack real skill cannot sustain a pretense forever.

#ChineseFable #滥竽充数 #ChineseStory #Mandarin #LearnChinese

---
Bilingual storytelling | 中英双语讲述
Subscribe for more Chinese fables: https://www.youtube.com/@aimorningread""",
        "tags": ["Chinese Fable", "Chinese Story", "滥竽充数", "Mandarin", "Learn Chinese", "Bilingual", "Ancient China", "Chinese Culture", "成语故事", "中英双语"],
    },
    {
        "file": "yi-xin-sheng-gui_final_v8.mp4",
        "title": "疑心生鬼 | Suspicion Creates Ghosts | Chinese Fable",
        "description": """疑心生鬼 | Suspicion Creates Ghosts

A story from ancient China about how suspicion and fear can make us see things that aren't there.

📖 Story: A man lost his umbrella and suspected his neighbor stole it. Every time he saw the neighbor, the neighbor looked suspicious. Later, he found the umbrella behind his door — the neighbor had never taken it.

💡 Moral: When the heart is suspicious, even a ghost will appear. Suspicion breeds false perception.

#ChineseFable #疑心生鬼 #ChineseStory #Mandarin #LearnChinese

---
Bilingual storytelling | 中英双语讲述
Subscribe for more Chinese fables: https://www.youtube.com/@aimorningread""",
        "tags": ["Chinese Fable", "Chinese Story", "疑心生鬼", "Mandarin", "Learn Chinese", "Bilingual", "Ancient China", "Chinese Culture", "成语故事", "中英双语"],
    },
]

CATEGORY_ID = "27"  # Education


def load_and_refresh_creds():
    with open(TOKEN_PATH) as f:
        token = json.load(f)

    expiry = datetime.fromisoformat(token["expiry"].replace("Z", "+00:00")).replace(tzinfo=None)
    creds = Credentials(
        token=token["access_token"],
        refresh_token=token["refresh_token"],
        client_id=token["client_id"],
        client_secret=token["client_secret"],
        token_uri=token.get("token_uri", "https://oauth2.googleapis.com/token"),
        scopes=token.get("scopes", ["https://www.googleapis.com/auth/youtube.force-ssl"]),
        expiry=expiry,
    )

    if not creds.valid:
        print("  ⚠️ Token 已过期，尝试刷新...")
        creds.refresh(Request())
        # 保存刷新后的 token
        with open(TOKEN_PATH, "w") as f:
            json.dump({
                "access_token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_type": "Bearer",
                "client_id": token["client_id"],
                "client_secret": token["client_secret"],
                "token_uri": token.get("token_uri", "https://oauth2.googleapis.com/token"),
                "scopes": list(creds.scopes) if creds.scopes else token.get("scopes", []),
                "expiry": creds.expiry.isoformat() + "Z",
            }, f, indent=2)
        print("  ✅ Token 已刷新")

    return creds


def upload(video_path: str, metadata: dict, privacy: str = "public") -> str:
    creds = load_and_refresh_creds()
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata["tags"],
            "categoryId": metadata["categoryId"],
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        }
    }

    media = MediaFileUpload(video_path, chunksize=10*1024*1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    print(f"  📤 上传中...")
    response = None
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"  进度: {int(status.progress() * 100)}%")
        except ResumableUploadError as e:
            if "uploadLimitExceeded" in str(e):
                print("  ⚠️ YouTube 每日上传配额已用完，请等待 UTC 午夜重试")
                return None
            raise

    video_url = f"https://www.youtube.com/watch?v={response['id']}"
    return video_url


def main():
    for video in VIDEOS:
        video_path = os.path.join(BASE_DIR, video["file"])
        if not os.path.exists(video_path):
            print(f"❌ 文件不存在: {video_path}")
            continue

        size_mb = os.path.getsize(video_path) / 1024 / 1024
        print(f"\n📹 [{video['file']}] {size_mb:.2f} MB")
        print(f"  标题: {video['title']}")

        metadata = {
            "title": video["title"],
            "description": video["description"],
            "tags": video["tags"],
            "categoryId": CATEGORY_ID,
        }

        video_url = upload(video_path, metadata, privacy="public")
        if video_url:
            print(f"  ✅ {video_url}")
        else:
            print(f"  ❌ 上传失败")


if __name__ == "__main__":
    main()