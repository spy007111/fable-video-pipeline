# Fable Video Pipeline

将中国古代成语/寓言故事自动转成高质量双语短视频：**分镜 → AI 绘图 → 配音 → 字幕 → 片段合成 → 最终成片**。

## 核心功能

- 输入一段故事文案，自动生成双语视频
- 基于固定角色定义保持同一人物/服饰视觉一致性
- 逐镜头时序对齐：画面与语音严格对应
- ASS 字幕层叠（中文在上，英文在下，同时间段叠加）
- 最终输出 1080p MP4，可自动第二版迭代

## 技术栈

- **绘画**：SenseNova `sensenova-u1-fast`（直连 `/v1/images/generations`）
- **配音**：Edge-TTS `en-US-GuyNeural`
- **合成**：FFmpeg + ffprobe
- **字幕格式**：ASS V4+（固定样式、避免跳动）

## 前置依赖

```
# 系统依赖（Ubuntu/Debian）
sudo apt-get update && sudo apt-get install -y ffmpeg python3 python3-pip

# Python 依赖
pip install requests

# Edge-TTS
pip install edge-tts

# SenseNova 环境变量（见 .env.example）
export SN_IMAGE_GEN_API_KEY="your_api_key"
export SN_BASE_URL="https://token.sensenova.cn/v1"
```

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/<your-username>/fable-video-pipeline.git
cd fable-video-pipeline
```

### 2. 准备环境变量

```bash
cp .env.example .env
# 编辑 .env，填入 SenseNova API Key
```

### 3. 创建故事脚本

参考 `examples/voiceover_script.json`，按顺序定义镜头：

- `id`：镜头唯一标识（`title`, `scene_1`, `scene_2`...）
- `cn`：中文旁白
- `en`：英文旁白
- `dur_est`：预估时长（秒），仅做排序参考

**注意**：字幕文本**必须**从 `voiceover_script.json` 的 `en` 字段读取，禁自动用 Whisper 反写。

### 4. 定义角色块

在 `examples/CHARACTERS.md` 列出所有角色，每个角色具备：

- 外貌特征
- 服饰颜色（多时必须显式区分）

示例：

```markdown
- 平民养羊人：短黑发髻、布衣、褐袍、布腰带、布裤、草鞋
- 狼：灰毛、竖耳、绿眼、体型中等
```

### 5. 设计分镜 Prompt

每个 prompt 固定嵌入对应角色的 CHARACTER 块，确保跨镜头一致性。

尾部**必须**加上：
```
NO TEXT, NO WORDS, NO LETTERS, NO ENGLISH anywhere in the image
```

### 6. 运行流水线

**方式一：一键执行（推荐）**

```bash
bash scripts/run_pipeline.sh
```

脚本会自动完成：
1. 遍历 `voiceover_script.json`
2. 调用 SenseNova 逐帧出图（输出到 `render/`）
3. 调用 Edge-TTS 逐句配音（输出到 `audio/`）
4. 按时间戳拼合单个镜头片段（输出到 `clips/`）
5. 拼接所有片段为最终 MP4（输出到 `output/`）

**方式二：分步调试**

```bash
# 第一步：绘图
python3 scripts/sn_agent_runner.py sn-image-generate \
  --prompt "<你的分镜 prompt>" \
  --image-size 2k --aspect-ratio 16:9 --timeout 900 \
  --save-path render/scene_1.png

# 第二步：配音
edge-tts --voice en-US-GuyNeural \
  --text "Once upon a time, there was a shepherd..." \
  --write-media audio/scene_1.mp3

# 第三步：合成单镜头
ffmpeg -loop 1 -i render/scene_1.png -i audio/scene_1.mp3 \
  -c:v libx264 -tune stillimage -c:a aac -b:a 192k \
  -pix_fmt yuv420p -shortest -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" \
  clips/scene_1.mp4
```

详见 [PIPELINE.md](PIPELINE.md) 获取底层细节。

## 时间戳与字幕生成

```bash
# 读取每个音频时长（秒）
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 audio/title.mp3  # 输出 5.012000

# 累加生成 ASS 字幕时间轴
```

ASS 字幕配置要求：
- 采用 V4+ 样式（`WrapStyle: 0`）
- 中文字体：`Noto Serif CJK SC`
- 英文字体：Noto Serif CJK SC
- 中英同时间段叠加，中文在上，英文在下

## 输出文件结构

```
fable-output/
  <故事名>/
    render/           # AI 绘制的静态画面（PNG）
    audio/            # 逐句配音（MP3）
    clips/            # 单个镜头合成片段（MP4）
    <故事名>_v1.mp4   # 最终成片
```

## 已知问题

| 问题 | 表现 | 解决方案 |
|------|------|----------|
| SenseNova ReadTimeout | `sensenova-u1-fast` 长 prompt 超时 | 增大 `--timeout` 至 900–1200 |
| SenseNova 500 错误 | 连续失败 | 终止重试，先用已生成图出首版 |
| Edge-TTS 专有名词发音偏差 | 人名/地名不准 | 简化角色名，或用付费 TTS |
| 字幕源错误 | 字幕文本与语音不一致 | 字幕只能读 `voiceover_script.json` 的 `en` 字段 |

## 参考文档

- [references/multi-character-prompts-2026-06-05.md](references/multi-character-prompts-2026-06-05.md)
- [references/gaoshan-liushui-sync-fix-v3-2026-06-05.md](references/gaoshan-liushui-sync-fix-v3-2026-06-05.md)
- [references/tts-pronunciation-errors-2026-06-05.md](references/tts-pronunciation-errors-2026-06-05.md)

## 贡献

欢迎 Issue 和 PR。建议贡献路径：

1. Fork 本仓库
2. 创建特性分支 `git checkout -b feature/amazing-flow`
3. 提交 `git commit -m 'Add amazing flow'`
4. 推送 `git push origin feature/amazing-flow`
5. 开 PR

## 许可证

本项目采用 [MIT](LICENSE) 许可证。
