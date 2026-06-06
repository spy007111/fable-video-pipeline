# Fable Video Pipeline

自动把中国古代寓言/成语故事制作成高质量双语短视频：**分镜 → AI 绘图 → 英文配音 → 字幕渲染 → 片段合成 → 最终成片**。

> ⚠️ **重要提醒**：图文生成，视频质量由大模型能力决定。当前默认使用 `sensenova-u1-fast`（免费），换用更强大的模型（如 GPT-Image-2）可显著提升画质。

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

| 晏子使楚 | 滥竽充数 | 疑心生鬼 |
|:---:|:---:|:---:|
| <a href="https://spy007111.github.io/fable-video-pipeline/"><img src="https://spy007111.github.io/fable-video-pipeline/yanzi_shi_chu_thumb.jpg" width="360" style="border-radius:10px; transition: transform .2s; border:1px solid #333;"></a> | <a href="https://spy007111.github.io/fable-video-pipeline/"><img src="https://spy007111.github.io/fable-video-pipeline/lan-yu-chong-shu_thumb.jpg" width="360" style="border-radius:10px; transition: transform .2s; border:1px solid #333;"></a> | <a href="https://spy007111.github.io/fable-video-pipeline/"><img src="https://spy007111.github.io/fable-video-pipeline/yi-xin-sheng-gui_thumb.jpg" width="360" style="border-radius:10px; transition: transform .2s; border:1px solid #333;"></a> |
| **94s** · 7.2 MB · v4 | **46.3s** · 2.49 MB · v4 | **54.5s** · 2.24 MB · v8 |
| 24fps · 1920×1080 | 25fps · 1920×1080 | 25fps · 1920×1080 |
| ASS+drawtext | 多角色稳定 | drawtext 直出 |

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

## 许可证

MIT