# Fable Video Pipeline

自动把中国古代寓言/成语故事制作成高质量双语短视频：**分镜 → AI 绘图 → 英文配音 → 字幕渲染 → 片段合成 → 最终成片**。

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

## 成功案例

### 竖屏 9:16

<table>
<thead>
<tr>
<th align="center">▶️ 晏子使楚</th>
<th align="center">▶️ 滥竽充数</th>
<th align="center">▶️ 疑心生鬼 v8</th>
</tr>
</thead>
<tbody>
<tr>
<td align="center"><video src="https://spy007111.github.io/fable-video-pipeline/yanzi_shi_chu_final_v4.mp4" controls="" style="width:100%;max-width:400px;border-radius:8px;"></video></td>
<td align="center"><video src="https://spy007111.github.io/fable-video-pipeline/lan-yu-chong-shu_final_v4.mp4" controls="" style="width:100%;max-width:320px;border-radius:8px;"></video></td>
<td align="center"><video src="https://spy007111.github.io/fable-video-pipeline/yi-xin-sheng-gui_final_v8.mp4" controls="" style="width:100%;max-width:320px;border-radius:8px;"></video></td>
</tr>
</tbody>
</table>

| 项目 | 晏子使楚 | 滥竽充数 | 疑心生鬼 v8 |
|------|---------|---------|-------------|
| 时长 | 94s | 46.3s | 54.5s |
| 分辨率 | 1920×1080 | 1920×1080 | 1920×1080 |
| 大小 | 7.2 MB | 2.49 MB | 2.24 MB |
| 帧率 | 24fps | 25fps | 25fps |
| 状态 | ✅ 可正常播放 | ✅ 可正常播放 | ✅ 可正常播放 |

## 项目结构

```
fable-video-pipeline/
├── README.md
├── PIPELINE.md
├── LICENSE
├── .env.example
├── examples/
│   ├── voiceover_script.json
│   └── output/           ← 视频成品
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

## 在线演示

如需更好的播放体验，可访问 **GitHub Pages 演示页**：

https://spy007111.github.io/fable-video-pipeline/

## 贡献

欢迎提交 PR。建议：从较简单寓言开始，验证故事脚本格式后再挑战多角色场景。

## 许可证

MIT