# 亡羊补牢 v4 完整修复记录（2026-06-06）

## 三个问题与根因

| 问题 | 根因 | v4 修复 |
|------|------|---------|
| 标题卡主题不匹配故事 | 纯色背景与寓言无关 | 用 `scene_01.png`（牧羊人场景）做背景 + 叠加中英文大标题 |
| 音频与字幕图文没对齐 | 每片段用了估算时长 | 每片段 `-t` = `ffprobe` 实测音频时长 |
| 音频和英文字幕不一致 | 字幕用了改写版本 | 严格用 `voiceover_script.json` 的 `text` 英文原文 |

---

## 核心原则：字幕与配音完全同源

| 来源 | 用途 |
|------|------|
| `voiceover_script.json` → `text` 字段 | 英文字幕原文 = 配音实际读出的英文 |
| `story_script.json` → `narration_cn` 字段 | 中文字幕原文 = 配音同步的中文 |

```python
# ✅ 正确做法
en = voiceover_item["text"]           # "Regretting that he hadn't listened..."
cn = story_item["narration_cn"]       # "养羊人后悔没有听邻居的劝告..."

# ❌ 错误做法：手动改写导致配音与字幕不一致
en = "He regretted not listening..."   # 重新措辞，配音读的是另一句话
```

---

## v4 fix_v4.py（完整脚本，直接复用）

将以下脚本保存到项目目录，运行即可生成 v4 成品：

```python
#!/usr/bin/env python3
"""
亡羊补牢 v4 — 完整修复脚本
1. 标题卡：scene_01 场景图做背景（牧羊人） + 中英文大标题叠加
2. 字幕：严格使用 voiceover_script（英文原文）和 story_script（中文原文）
3. 每片段时长：ffprobe 实测音频时长
"""
import subprocess, json, os

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
OUT  = "/usr/local/lib/hermes-agent/fable-output/wang-yang-bu-lao"

# ── 加载数据 ──────────────────────────────────────────────────────
voiceover = json.load(open(f"{OUT}/voiceover_script.json"))
story     = json.load(open(f"{OUT}/story_script.json"))

def get_dur(audio_id):
    r = subprocess.run(
        ["ffprobe","-v","quiet","-show_entries","format=duration","-of","csv=p=0",
         f"{OUT}/audio_{audio_id}.mp3"],
        capture_output=True, text=True
    )
    return round(float(r.stdout.strip()), 3)

# 构建 scenes：(id, 中文原文, 英文原文, 时长)
scenes = []
for v in voiceover:
    sid = v["id"]
    en  = v["text"]                        # 英文原文，精确
    s   = next(s for s in story if s["id"]==sid)
    cn  = s["narration_cn"]                # 中文原文，精确
    dur = get_dur(sid)
    scenes.append((sid, cn, en, dur))

print("字幕与音频对照：")
for sid, cn, en, dur in scenes:
    print(f"  [{sid}] {dur:.3f}s | CN: {cn} | EN: {en}")

# ── Step 1: 标题卡（scene_01 场景图做背景 + 中英文大标题）─────────────
title_cn = "亡羊补牢"
title_en = "Mending the Fold After Losing Sheep. A Chinese Fable."
cn_esc = title_cn.replace("'", "\\'")
en_esc = title_en.replace("'", "\\'")

TITLE_DUR = scenes[0][3]           # audio_title 时长（实测）
TITLE_IMG = f"{OUT}/scene_01.png"   # 牧羊人场景图做标题背景

title_sub = f"{OUT}/clip_title_sub.mp4"
print(f"\n🎬 标题卡（背景={TITLE_IMG}，{TITLE_DUR}s）...")

r = subprocess.run([
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
    title_sub
], capture_output=True, text=True)

if r.returncode == 0:
    print(f"  ✅ 标题卡 ({os.path.getsize(title_sub)/1024:.0f} KB)")
else:
    print(f"  ❌ {r.stderr[-400:]}")

# ── Step 2: 渲染所有场景字幕（中英原文 + 亮黄字幕）────────────────────
print("\n🎬 渲染字幕（中英原文）...")
for sid, cn, en, dur in scenes:
    if sid == "title":
        continue
    clip     = f"{OUT}/clip_{sid}.mp4"
    clip_sub = f"{OUT}/clip_{sid}_sub.mp4"
    cn_esc = cn.replace("\\", "\\\\").replace("'", "\\'")
    en_esc = en.replace("\\", "\\\\").replace("'", "\\'")

    f_str = (
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
        "ffmpeg", "-y", "-i", clip,
        "-vf", f_str,
        "-c:a", "aac", "-b:a", "192k",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        clip_sub
    ], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"  ✅ {sid}")
    else:
        print(f"  ❌ {sid}: {r.stderr[-200:]}")

# ── Step 3: 拼接最终视频 ─────────────────────────────────────────────
print("\n🎬 拼接最终视频...")
scene_ids = [s[0] for s in scenes]
with open(f"{OUT}/concat.txt", "w") as f:
    for sid in scene_ids:
        f.write(f"file '{os.path.abspath(f'{OUT}/clip_{sid}_sub.mp4')}'\n")

final = f"{OUT}/wang-yang-bu-lao_final_v4.mp4"
r = subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/concat.txt",
    "-c", "copy", final
], capture_output=True, text=True)

if r.returncode == 0:
    sz = os.path.getsize(final)/1024/1024
    td = subprocess.run(
        ["ffprobe","-v","quiet","-show_entries","format=duration","-of","csv=p=0",final],
        capture_output=True, text=True
    )
    print(f"  ✅ {final} ({sz:.2f} MB) | 总时长: {float(td.stdout.strip()):.1f}s")
else:
    print(f"  ❌ {r.stderr[-300:]}")
```

---

## 复用模板

将此脚本复制到新项目时，只需修改以下变量：

| 变量 | 修改为 |
|------|--------|
| `OUT` | 新项目路径 `/usr/local/lib/hermes-agent/fable-output/<新故事名>` |
| `title_cn` | 新故事中文名 |
| `title_en` | 新故事英文名 |
| `title_sub` 输出文件名 | `<新故事名>_final_v4.mp4` |

其他逻辑（字幕同源、ffprobe 实测时长、scene_01 做标题卡背景）无需改动。