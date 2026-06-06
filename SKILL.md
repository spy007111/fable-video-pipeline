---
name: fable-video-pipeline
description: |
  寓言故事视频自动化流水线 — 从素材到成品的全流程技能（v4）。
  支持：分镜脚本生成、角色一致性图片生成、英文配音、电影风格字幕渲染。
triggers:
  - "寓言视频制作"
  - "fable video"
  - "寓言故事视频"
  - "fable-video"
  - "寓言双语视频"
metadata:
  project: User Projects
  tier: 1
  category: video-production
  user_visible: true
  version: 4
---

# Fable Video Pipeline v4

寓言故事视频自动化流水线 — 从分镜脚本到成品的全流程技能（v4）。

## 核心原则（v4 新增）

| 原则 | v3 做法（错误） | v4 做法（正确） |
|------|---------------|----------------|
| **标题卡** | 纯色背景 + 文字叠加 | scene_01 场景图做背景 + 叠加中英文大标题 |
| **字幕来源** | 手动改写或 LLM 重写 | 严格用 `voiceover_script.json` 英文原文 + `story_script.json` 的 `narration_cn` 中文原文 |
| **片段时长** | 估算值 | `ffprobe` 实测音频时长（秒精度） |
| **drawtext** | shell 变量拼接（撇号导致静默失败） | `subprocess` 列表传参 + `replace("'", "\\'")` 转义 |
| **字幕颜色** | 灰色/浅色 | 中文 `0xFFFF00` 亮黄，英文 `0xFFFFFF` 纯白 |

---

## 完整执行流程（v4）

```
step 1: 创建项目目录
step 2: 编写 story_script.json（分镜脚本）
step 3: 生成 voiceover_script.json（英文配音脚本）
step 4: 生成场景图（SenseNova 2K 2752x1536）
step 5: 生成音频（Edge-TTS）
step 6: 生成视频片段（ffmpeg，每片段精确时长）
step 7: 渲染字幕（中英原文，textfile/转义二选一）
step 8: 拼接最终视频
step 9: 验证与上传 YouTube
```

---

## Step 1 — 创建项目目录

```bash
OUTPUT_DIR="/usr/local/lib/hermes-agent/fable-output/<故事名>"
mkdir -p "$OUTPUT_DIR"
```

---

## Step 2 — 编写 story_script.json

每个分镜包含 `id`、`description`、`narration_cn`（中文原文）。

```json
[
  {
    "id": "title",
    "description": "Title card: ancient Chinese pastoral landscape with a shepherd and his sheep",
    "character": "shepherd",
    "narration_cn": "亡羊补牢",
    "narration_en": "Mending the Fold After Losing Sheep"
  },
  {
    "id": "scene_01",
    "description": "A shepherd tending his sheep in a peaceful morning field, sheep grazing in a simple wooden pen",
    "character": "shepherd",
    "narration_cn": "古时候有一个人，养了几只羊。一天早上，他去放羊，发现少了一只。",
    "narration_en": "Once upon a time, there lived a shepherd who raised several sheep..."
  }
]
```

**关键字段**：
- `narration_cn`：中文配音原文（最终字幕中文来源），带完整标点
- `narration_en`：英文配音原文（仅供参考故事内容，不直接用于配音）

---

## Step 3 — 生成 voiceover_script.json

为每个分镜生成英文配音脚本（与 `story_script.json` 的 `id` 对应）：

```json
[
  {
    "id": "title",
    "text": "Mending the Fold After Losing Sheep. A Chinese fable.",
    "duration_estimate": 5
  },
  {
    "id": "scene_01",
    "text": "Once upon a time, there lived a shepherd who raised several sheep. One morning, he went to tend his flock and discovered one sheep was missing.",
    "duration_estimate": 12
  }
]
```

**原则**：`voiceover_script` 的 `text` 必须是**配音实际读出的英文**，不能与 story_script 的 narration_en 相同（因为 narration_en 是叙事中文的英文翻译，配音稿是口语化版本）。

---

## Step 4 — 生成场景图

**API 配置**：
- Key：`SN_IMAGE_GEN_API_KEY`（`~/.hermes/.env`，注意不是 `wrk-` 开头的 key）
- Base URL：`https://token.sensenova.cn/v1`
- 端点：`/images/generations`
- 尺寸：**`2752x1536`**（必须，11种固定尺寸之一，乘号和非乘号都不要搞错）

**角色一致性**：每张 prompt 嵌入相同的角色描述块。

```python
CHARACTER = """A specific Chinese shepherd, middle-aged about 45 years old,
thin wiry build, wearing traditional ancient Chinese peasant clothing -
loose long brown/grey tunic with wide sleeves, traditional dark brown cloth belt,
dark cloth trousers, simple black cloth shoes, plain black hair tied in a simple topknot,
weathered tan face, small kind eyes, humble peasant appearance, ancient Chinese rural style"""

style = """Contemporary Chinese commercial illustration style, flat design with soft warm colors,
gentle lighting, pastoral Chinese countryside landscape, cinematic storytelling composition"""

prompt = f"""{CHARACTER}, {scene_description}. {style}
NO TEXT, NO WORDS, NO LETTERS, NO ENGLISH anywhere in the image.
ONLY ONE PERSON in the scene."""
```

**标题卡**：`title` 分镜不需要单独生成图片，用 `scene_01.png` 做背景。

---

## Step 5 — 生成音频

```bash
edge-tts --voice en-US-GuyNeural --text "Once upon a time, there lived a shepherd..." \
  --write-media "$OUTPUT_DIR/audio_scene_01.mp3"
```

**声音选择**：
| 声音 | 适用场景 |
|------|----------|
| `en-US-GuyNeural` | 叙事、常规场景（默认） |
| `en-US-AndrewNeural` | 恍然大悟、温情时刻 |
| `en-GB-RyanNeural` | 道德总结、权威感 |
| `en-US-AriaNeural` | 紧张、戏剧性场景 |
| `en-US-JennyNeural` | 平和、日常、轻松场景 |

---

## Step 6 — 生成视频片段（精确时长）

```python
import subprocess, json

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
OUT  = "/usr/local/lib/hermes-agent/fable-output/<故事名>"

def get_dur(audio_path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", audio_path],
        capture_output=True, text=True
    )
    return round(float(r.stdout.strip()), 3)

# 示例：生成 scene_01 片段
dur = get_dur(f"{OUT}/audio_scene_01.mp3")

subprocess.run([
    "ffmpeg", "-y",
    "-loop", "1", "-i", f"{OUT}/scene_01.png",
    "-i", f"{OUT}/audio_scene_01.mp3",
    "-vf", (
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
        "format=yuv420p"
    ),
    "-c:v", "libx264", "-preset", "fast", "-crf", "23",
    "-c:a", "aac", "-b:a", "192k",
    "-t", str(dur),          # ← 精确时长（ffprobe 实测）
    "-pix_fmt", "yuv420p",
    "-shortest",
    f"{OUT}/clip_scene_01.mp4"
], capture_output=True)
```

**⚠️ 必须用 `ffprobe` 实测时长**，不能用 `duration_estimate` 估算值，误差 < 0.02s。

---

## Step 7 — 渲染字幕（中英原文，v4 标准）

**两个可用方案，推荐方案 A**：

### 方案 A（推荐）：subprocess 列表传参 + 转义

```python
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

def render_subtitles(clip_path, cn_text, en_text, clip_sub_path):
    # 转义：单引号、反斜杠（通过 subprocess 列表传参，不进 shell）
    cn_esc = cn_text.replace("\\", "\\\\").replace("'", "\\'")
    en_esc = en_text.replace("\\", "\\\\").replace("'", "\\'")

    filter_str = (
        f"drawtext=text='{cn_esc}':fontsize=42:fontcolor=0xFFFF00:"
        f"x=(w-text_w)/2:y=h-115:fontfile={FONT}:"
        f"borderw=2:bordercolor=black@0.9:"
        f"shadowcolor=black:shadowx=2:shadowy=2,"
        f"drawtext=text='{en_esc}':fontsize=30:fontcolor=0xFFFFFF:"
        f"x=(w-text_w)/2:y=h-70:fontfile={FONT}:"
        f"borderw=1:bordercolor=black@0.7:"
        f"shadowcolor=black:shadowx=1:shadowy=1"
    )

    r = subprocess.run([
        "ffmpeg", "-y", "-i", clip_path,
        "-vf", filter_str,
        "-c:a", "aac", "-b:a", "192k",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        clip_sub_path
    ], capture_output=True, text=True)

    if r.returncode != 0:
        print(f"  ❌ {r.stderr[-200:]}")
        return False
    return True
```

### 方案 B（更可靠）：`textfile=` 参数

将字幕文本写入临时文件，FFmpeg 从文件读取，彻底绕过 shell 引号问题：

```python
import tempfile

cn_file = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
cn_file.write(cn_text)
cn_file.close()

en_file = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
en_file.write(en_text)
en_file.close()

filter_str = (
    f"drawtext=textfile='{cn_file.name}':fontsize=42:fontcolor=0xFFFF00:"
    f"x=(w-text_w)/2:y=h-115:fontfile={FONT}:"
    f"borderw=2:bordercolor=black@0.9,"
    f"drawtext=textfile='{en_file.name}':fontsize=30:fontcolor=0xFFFFFF:"
    f"x=(w-text_w)/2:y=h-70:fontfile={FONT}:"
    f"borderw=1:bordercolor=black@0.7"
)

subprocess.run(["ffmpeg", "-y", "-i", clip_path, "-vf", filter_str,
                "-c:a", "copy", "-c:v", "libx264", "-preset", "medium", "-crf", "23",
                clip_sub_path], capture_output=True)

os.unlink(cn_file.name)
os.unlink(en_file.name)
```

### 字幕标准参数（v4）

| 项目 | 值 |
|------|-----|
| 中文字幕颜色 | `0xFFFF00`（亮黄） |
| 英文字幕颜色 | `0xFFFFFF`（纯白） |
| 中文字幕位置 | `y=h-115` |
| 英文字幕位置 | `y=h-70` |
| 中文字幕字号 | `42` |
| 英文字幕字号 | `30` |
| 中文字幕描边 | `borderw=2:bordercolor=black@0.9` |
| 英文字幕描边 | `borderw=1:bordercolor=black@0.7` |
| 字体 | `NotoSansCJK-Regular.ttc` |
| 字幕行 | 单行，无 `\n`，带标点 |

---

## Step 8 — 标题卡（v4 专用流程）

**⚠️ 标题卡必须使用 scene_01 场景图做背景**，与故事主题相关（不能是纯色背景或无关图片）。

```python
title_cn = "亡羊补牢"
title_en = "Mending the Fold After Losing Sheep. A Chinese Fable."
TITLE_IMG = f"{OUT}/scene_01.png"   # 场景图做标题背景
TITLE_DUR = get_dur(f"{OUT}/audio_title.mp3")

cn_esc = title_cn.replace("'", "\\'")
en_esc = title_en.replace("'", "\\'")

subprocess.run([
    "ffmpeg", "-y",
    "-loop", "1", "-i", TITLE_IMG,
    "-i", f"{OUT}/audio_title.mp3",
    "-vf", (
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
        "format=auto,eq=saturation=0.3:brightness=-0.15,"
        f"drawtext=text='{cn_esc}':fontsize=100:fontcolor=white:"
        f"x=(w-text_w)/2:y=(h-text_h)/2-40:fontfile={FONT}:"
        f"borderw=3:bordercolor=black@0.8:shadowcolor=black:shadowx=3:shadowy=3,"
        f"drawtext=text='{en_esc}':fontsize=36:fontcolor=0xCCCCCC:"
        f"x=(w-text_w)/2:y=(h-text_h)/2+80:fontfile={FONT}:"
        f"borderw=2:bordercolor=black@0.6:shadowcolor=black:shadowx=2:shadowy=2"
    ),
    "-c:v", "libx264", "-preset", "fast", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k",
    "-t", str(TITLE_DUR), "-pix_fmt", "yuv420p", "-shortest",
    f"{OUT}/clip_title_sub.mp4"
], capture_output=True)
```

---

## Step 9 — 拼接最终视频

```bash
# 按顺序写入 concat 列表
for sid in title scene_01 scene_02 scene_03 scene_04 scene_05 scene_06 scene_07 moral; do
  echo "file '/path/to/clip_${sid}_sub.mp4'" >> concat.txt
done

ffmpeg -y -f concat -safe 0 -i concat.txt -c copy final_v4.mp4
```

---

## Step 10 — YouTube 上传

**Token 刷新关键**（2026-06-06）：`Credentials` 必须包含 `token_uri`：

```python
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_PATH = "/root/token.json"
with open(TOKEN_PATH) as f:
    token = json.load(f)

expiry = datetime.fromisoformat(token["expiry"].replace("Z","+00:00")).replace(tzinfo=None)
creds = Credentials(
    token=token["access_token"],
    refresh_token=token["refresh_token"],
    client_id=token["client_id"],
    client_secret=token["client_secret"],
    token_uri=token.get("token_uri", "https://oauth2.googleapis.com/token"),  # ← 必须
    scopes=token.get("scopes", ["https://www.googleapis.com/auth/youtube.force-ssl"]),
    expiry=expiry,
)
if not creds.valid:
    creds.refresh(Request())
    with open(TOKEN_PATH, "w") as f:
        json.dump({"access_token": creds.token, "refresh_token": creds.refresh_token,
            "token_type": "Bearer", "client_id": token["client_id"],
            "client_secret": token["client_secret"],
            "token_uri": creds.token_uri,
            "scopes": list(creds.scopes) if creds.scopes else token.get("scopes", []),
            "expiry": creds.expiry.isoformat()+"Z"}, f, indent=2)

youtube = build("youtube", "v3", credentials=creds)
body = {
    "snippet": {
        "title": "亡羊补牢 | Mending the Fold After Losing Sheep | Chinese Fable",
        "description": "...",
        "tags": ["Chinese Fable", "亡羊补牢", "Mandarin"],
        "categoryId": "27",
    },
    "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
}
from googleapiclient.http import MediaFileUpload
media = MediaFileUpload(video_path, chunksize=10*1024*1024, resumable=True)
req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
# 上传完成后在 YouTube Studio 传统编辑器中删除旧版本
```

---

## 字幕与音频完全同源原则（v4 核心）

**⚠️ 字幕必须与配音使用完全相同的文本**，不能重新措辞：

| 来源 | 用途 |
|------|------|
| `voiceover_script.json` 的 `text` 字段 | 英文配音原文 + 英文字幕原文 |
| `story_script.json` 的 `narration_cn` 字段 | 中文字幕原文 |

```python
# 正确：字幕与配音使用相同的英文文本
en = voiceover_item["text"]           # "Regretting that he hadn't listened..."
cn = story_item["narration_cn"]       # "养羊人后悔没有听邻居的劝告..."

# 错误：手动改写导致配音与字幕不一致
en = "He regretted not listening..."   # 重新措辞，配音读的是另一句话
```

---

## 常见问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| **标题卡滤镜链顺序** | `format=auto`（崩溃） | `scale→pad→format=yuv420p→eq`（固定顺序，eq 必须在 format 之后） |

`format=auto` 在 `drawtext` 前会导致 `Invalid pixel format 'auto'` 崩溃。正确的滤镜链：

```python
vf = (
    "scale=1920:1080:force_original_aspect_ratio=decrease,"
    "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
    "format=yuv420p,eq=saturation=0.3:brightness=-0.15,"   # ← format=yuv420p 在前，eq 在后
    f"drawtext=text='{cn_esc}':..."
)
```
| **音频与字幕不一致** | 字幕用了手动改写版本 | 字幕严格使用 `voiceover_script` 英文原文 + `story_script` 的 `narration_cn` |
| **字幕显示为空白** | `didn't` 等撇号导致 filtergraph 静默失败 | 用 `subprocess` 列表传参，`replace("'", "\\'")` 转义单引号 |
| **片段时长不对** | 用估算值而非实测值 | 每片段 `-t` = `ffprobe -i audio_xxx.mp3 -show_entries format=duration -v quiet -of csv=p=0` |
| **中文字幕颜色太淡** | 浅灰/浅黄色 | 改用 `0xFFFF00` 亮黄 |
| **英文字幕颜色太淡** | 灰色 | 改用 `0xFFFFFF` 纯白 |
| **英文字幕为空** | 取错了字段 | 英文字幕来源是 `voiceover_script.json` 的 `text`，不是 `story_script.json` |
| **角色不一致** | 每张图独立生成 | 每张 prompt 嵌入相同角色描述块 |
| **画面出现英文字** | prompt 约束不足 | 添加 `NO TEXT, NO WORDS, NO LETTERS, NO ENGLISH anywhere in the image` |
| **出现多个人物** | prompt 未限制 | 添加 `ONLY ONE PERSON in the scene` |

---

## 项目目录结构

```
/usr/local/lib/hermes-agent/fable-output/<故事名>/
├── story_script.json          # 分镜脚本（中文原文 narration_cn，英文原文 narration_en）
├── voiceover_script.json      # 英文配音脚本（text 字段 = 配音实际内容）
├── audio_<id>.mp3             # 每个分镜的配音音频
├── scene_01.png ~ scene_XX.png # 场景图（2752x1536）
├── clip_<id>.mp4              # 视频片段（无字幕）
├── clip_<id>_sub.mp4          # 视频片段（带字幕）
└── <故事名>_final_vN.mp4      # 最终成品视频
```

---

## 标准参数

| 项目 | 值 |
|------|-----|
| 分辨率 | 1920×1080（16:9） |
| 图片尺寸 | **2752x1536**（SenseNova 2K） |
| 配音 | Edge-TTS en-US-GuyNeural（默认）|

## TTS 发音避坑：撇号导致 "ord" 错误（必须）

Edge-TTS 对英文撇号 `'s` / `n't` 有已知 bug：会把 `didn't` 读成 "didn ord"，`wouldn't` 读成 "wouldn ord"。

**必须用完整单词替代所有撇号**：

| ❌ 错误 | ✅ 正确 |
|---------|---------|
| `didn't` | `did not` |
| `wouldn't` | `would not` |
| `couldn't` | `could not` |
| `can't` | `cannot` |
| `I've` | `I have` |
| `that's` | `that is` |
| `it's` | `it is` |

**在 `voiceover_script.json` 中每句都检查**，确保没有撇号后再送入 edge-tts。

## 配音声音选择指南（v4）

根据场景情感选择声音，**不用默认单一声音**：

| 声音 | 适用场景 | 情感特点 |
|------|----------|----------|
| `en-US-GuyNeural` | 叙事、常规场景（默认） | 沉稳、正式、叙事感 |
| `en-US-AndrewNeural` | 恍然大悟、温情时刻、灵机一动 | 温暖、有感染力 |
| `en-US-JennyNeural` | 感叹、轻松、哲理感悟 | 友好、有共鸣 |
| `en-GB-RyanNeural` | 道德总结、权威结语 | 英式权威、庄重 |
| `en-US-AriaNeural` | 紧张、戏剧性、冲突 | 自信、有表现力 |
| `en-US-MichelleNeural` | 反思、内省、柔和场景 | 温和、柔软 |

**选择原则**：
- 旁白叙事 → `GuyNeural`
- 角色对话/感叹 → `JennyNeural` / `AndrewNeural`
- 道德总结 → `RyanNeural`
- 戏剧性/紧张 → `AriaNeural`

**在 `voiceover_script.json` 中指定**：
```json
[
  {
    "id": "scene_03",
    "text": "Gongming Yi thought for a moment...",
    "voice": "en-US-AndrewNeural"
  },
  {
    "id": "moral",
    "text": "Moral: Speak and act according to your audience.",
    "voice": "en-GB-RyanNeural"
  }
]
```
| 中文字幕 | `0xFFFF00` 亮黄，fontsize=42，borderw=2 |
| 英文字幕 | `0xFFFFFF` 纯白，fontsize=30，borderw=1 |
| 字幕位置 | 中文 `y=h-115`，英文 `y=h-70` |
| 标题卡背景 | scene_01 场景图（不能用纯色或无关图片） |

---

## 参考文档

| 文档 | 内容 |
|------|------|
| `references/drawtext-escape-pitfall-2026-06-06.md` | drawtext 单引号/特殊字符导致 filtergraph 静默失败的根因与修复 |
| `references/audio-video-sync-precision.md` | 音画同步精度（ffprobe 实测 + frames:v 精确帧数） |
| `references/multi-character-prompts-2026-06-05.md` | 多角色场景提示词（帝王 vs 平民服饰区分） |
| `references/youtube-upload-troubleshooting-v2.md` | YouTube 上传（token 刷新、quota、title 格式） |
| `references/wang-yang-bu-lao-fix-2026-06-06.md` | 亡羊补牢 v4 完整修复记录（可直接复用为模板） |

## 已验证案例

> **Provenance 规则**：新增案例前必须先 `find` 定位最终 `final_v*.mp4`，并用 `ffprobe` 确认时长/分辨率。没有磁盘文件支撑的案例绝不写入成功案例区。

| 寓言 | 成品 | 版本 | 关键验证 |
|------|------|------|----------|
| 亡羊补牢 | `wang-yang-bu-lao_final_v4.mp4` | v4 | 标题卡用 scene_01 场景图，字幕与配音完全同源 |

---

## 后续优化方向

1. **配音质量**：使用 ElevenLabs 自定义发音（解决 "Ziqi→Ziki" 等 TTS 固有偏差）
2. **自动化**：Cron 定时任务自动生产
3. **图片风格**：换用 GPT-Image-2 提升画面质量（当前 SenseNova u1-fast 偏动漫风）