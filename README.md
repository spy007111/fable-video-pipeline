# Fable Video Pipeline

自动把中国古代寓言/成语故事制作成高质量双语短视频：**分镜 → AI 绘图 → 英文配音 → 字幕渲染 → 片段合成 → 最终成片**。

> ⚠️ **重要提醒**：图文生成，视频质量由大模型能力决定。当前默认使用 `sensenova-u1-fast`（免费），换用更强大的模型（如 GPT-Image-2）可显著提升画质。

## YouTube 频道

📺 **aimorningread**：https://www.youtube.com/@aimorningread

每晚一个寓言双语讲述，20:30 更新。

## 功能特性 🎯

- 输入一段故事文案 + 分镜描述，自动生成 1080p 双语字幕短视频
- 固定角色描述嵌入每个 prompt，跨镜头保持视觉一致性
- 逐镜头时序对齐：画面与语音严格对应
- ASS 字幕层叠（中文在上，英文在下）
- 可独立使用每个 stage，也可一键跑通全流程

## 技术栈

| 模块 | 技术 |
|------|------|
| 绘图 | SenseNova `sensenova-u1-fast` |
| 配音 | Edge-TTS `en-US-GuyNeural` |
| 合成 | FFmpeg + ffprobe |
| 字幕 | ASS V4+ / drawtext 直出 |

## 快速开始

```bash
git clone https://github.com/spy007111/fable-video-pipeline.git
cd fable-video-pipeline
cp .env.example .env
pip install edge-tts requests
bash scripts/run_pipeline.sh <故事名> examples/voiceover_script.json
```

## 视频输出

- 分辨率：1920×1080 (16:9)
- 编码：H.264 + AAC
- 画幅：按原始比例等比缩放后黑边填充（不变形）
- 时长：60–180s 自适应
- 典型大小：3–10 MB / 分钟

## 成功案例（直接播放）

👉 **点击任意缩略图进入演示页，在线播放所有视频：**

https://spy007111.github.io/fable-video-pipeline/

---

| 晏子使楚 | 滥竽充数 | 疑心生鬼 | 亡羊补牢 |
|:---:|:---:|:---:|:---:|
| <a href="https://spy007111.github.io/fable-video-pipeline/"><img src="https://spy007111.github.io/fable-video-pipeline/yanzi_shi_chu_thumb.jpg" width="280" style="border-radius:10px; transition: transform .2s; border:1px solid #333;"></a> | <a href="https://spy007111.github.io/fable-video-pipeline/"><img src="https://spy007111.github.io/fable-video-pipeline/lan-yu-chong-shu_thumb.jpg" width="280" style="border-radius:10px; transition: transform .2s; border:1px solid #333;"></a> | <a href="https://spy007111.github.io/fable-video-pipeline/"><img src="https://spy007111.github.io/fable-video-pipeline/yi-xin-sheng-gui_thumb.jpg" width="280" style="border-radius:10px; transition: transform .2s; border:1px solid #333;"></a> | <a href="https://spy007111.github.io/fable-video-pipeline/"><img src="https://spy007111.github.io/fable-video-pipeline/wang-yang-bu-lao_thumb_v4.jpg" width="280" style="border-radius:10px; transition: transform .2s; border:1px solid #333;"></a> |
| **94s** · 7.2 MB · v4 | **46.3s** · 2.49 MB · v4 | **54.5s** · 2.24 MB · v8 | **54.7s** · 3.18 MB · v4 |
| 24fps · 1920×1080 | 25fps · 1920×1080 | 25fps · 1920×1080 | 25fps · 1920×1080 |
| ASS+drawtext | 多角色稳定 | drawtext 直出 | 亮黄字幕+标题卡 |

> 💡 **点击缩略图 → 进入演示页 → 点击播放按钮直接观看，无需下载**

---

## 项目结构

```
fable-video-pipeline/
├── README.md
├── PIPELINE.md
├── LICENSE
├── .env.example
├── docs/                  ← 在线演示页（含视频，可直接播放）
├── examples/
│   └── output/           ← 视频成品
└── scripts/
    ├── run_pipeline.sh
    └── 03-06_*.py         ← 各阶段处理脚本
```

## 贡献

欢迎提交 PR。建议：从较简单寓言开始，验证故事脚本格式后再挑战多角色场景。

## 如何使用本 Skill

本项目包含一个完整的 Hermes Agent skill，可以复用到你自己的 Hermes 环境中。

### 目录结构

```
fable-video-pipeline/
├── SKILL.md              ← Skill 定义文件
├── scripts/              ← 流水线脚本
├── references/           ← 技术文档与经验总结
└── templates/            ← 分镜模板
```

### 安装方式（任选其一）

**方式 A：复制到本地 skills 目录（推荐）**

```bash
# 克隆仓库
git clone https://github.com/spy007111/fable-video-pipeline.git
cd fable-video-pipeline

# 复制到 Hermes skills 目录
cp -r SKILL.md ~/.hermes/skills/video-production/fable-video-pipeline/
cp -r scripts/ ~/.hermes/skills/video-production/fable-video-pipeline/
cp -r references/ ~/.hermes/skills/video-production/fable-video-pipeline/
cp -r templates/ ~/.hermes/skills/video-production/fable-video-pipeline/
```

**方式 B：通过 HermeTalk 安装（待上线）**

等待发布到 ClawHub 后，可用以下命令安装：

```bash
curl -sL "<download-url>" -o /tmp/fable-video-pipeline.zip
unzip -o /tmp/fable-video-pipeline.zip -d ~/.hermes/skills/video-production/
```

### 触发方式

在 Hermes Agent 中直接说：

- `帮我制作一个寓言视频`
- `用 fable-video-pipeline 生成视频`
- `寓言故事视频制作`

### 依赖

- Python 3 + `edge-tts`、`requests`
- FFmpeg（合成视频用）
- SenseNova API Key（绘图用，可替换为 GPT-Image-2 提升画质）

---

## 许可证

MIT