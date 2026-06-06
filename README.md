# Fable Video Pipeline

自动把中国古代寓言/成语故事制作成高质量双语短视频：**分镜 → AI 绘图 → 英文配音 → 字幕渲染 → 片段合成 → 最终成片**。

项目已产出可播放成片，见下方 [Success Cases](#success-cases)。

## 核心能力

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
git clone https://github.com/<your-username>/fable-video-pipeline.git
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

## 成功案例

### 晏子使楚（已验证）

<a href="https://github.com/spy007111/fable-video-pipeline/raw/main/examples/output/yanzi_shi_chu_final_v4.mp4">
  <img src="https://github.com/spy007111/fable-video-pipeline/raw/main/examples/output/thumbnails/yanzi_shi_chu_thumb.jpg" alt="晏子使楚 预览" width="640">
</a>

| 项目 | 详情 |
|------|------|
| 成品 | `yanzi_shi_chu_final_v4.mp4` |
| 路径 | `/root/fable-output/yanzi_shi_chu/yanzi_shi_chu_final_v4.mp4` |
| 分辨率 | 1920×1080 (16:9) |
| 时长 | 94s |
| 大小 | 7.2 MB |
| 帧率 | 24fps |
| 状态 | 可正常播放 |

验证结论：ASS 字幕按实测音频时长累加；同一 prompt 嵌入恒定角色描述实现基础一致性；drawtext 直出绕过 ASS filter 兼容性问题；累积误差 < 0.05s。

### 滥竽充数（已验证）

<a href="https://github.com/spy007111/fable-video-pipeline/raw/main/examples/output/lan-yu-chong-shu_final_v4.mp4">
  <img src="https://github.com/spy007111/fable-video-pipeline/raw/main/examples/output/thumbnails/lan-yu-chong-shu_thumb.jpg" alt="滥竽充数 预览" width="640">
</a>

| 项目 | 详情 |
|------|------|
| 成品 | `lan-yu-chong-shu_final_v4.mp4` |
| 路径 | `/root/fable-output/lan-yu-chong-shu_final_v4/lan-yu-chong-shu_final_v4.mp4` |
| 分辨率 | 1920×1080 (16:9) |
| 时长 | 46.3s |
| 大小 | 2.49 MB |
| 帧率 | 25fps |
| 状态 | 可正常播放 |

验证结论：命名格式一致，单场景序列稳定；证明同一 pipeline 对多角色画面也能标准产出。

### 疑心生鬼 v8（已验证）

<a href="https://github.com/spy007111/fable-video-pipeline/raw/main/examples/output/yi-xin-sheng-gui_final_v8.mp4">
  <img src="https://github.com/spy007111/fable-video-pipeline/raw/main/examples/output/thumbnails/yi-xin-sheng-gui_thumb.jpg" alt="疑心生鬼 预览" width="640">
</a>

| 项目 | 详情 |
|------|------|
| 成品 | `yi-xin-sheng-gui_final_v8.mp4` |
| 路径 | `/root/fable-output/yi-xin-sheng-gui_final_v8/yi-xin-sheng-gui_final_v8.mp4` |
| 分辨率 | 1920×1080 (16:9) |
| 时长 | 54.5s |
| 大小 | 2.24 MB |
| 帧率 | 25fps |
| 状态 | 可正常播放 |

验证结论：版本迭代至 v8 仍可稳定流水线产出；未使用 ASS filter，改用 drawtext 直出，字幕时间轴按实际音频时长累加。

## 贡献

欢迎提交 PR。建议：从较简单寓言开始，验证故事脚本格式后再挑战多角色场景。

## 项目结构

```
fable-video-pipeline/
├── README.md
├── PIPELINE.md
├── LICENSE
├── .env.example
├── examples/
│   ├── voiceover_script.json
│   └── CHARACTERS.md
├── scripts/
│   ├── run_pipeline.sh
│   ├── 03_generate_image.py
│   ├── 04_generate_audio.py
│   ├── 05_generate_subtitles.py
│   └── 06_compose_video.py
├── src/
│   └── config/
│       └── settings.py
└── references/
    └── ...
```

## 贡献

Issue 和 PR 都欢迎。

## 许可证

MIT
