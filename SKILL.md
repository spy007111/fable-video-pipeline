---
name: fable-video-pipeline
description: |
  寓言故事双语视频自动化流水线：分镜 -> 图生 -> 配音 -> 片段 -> 字幕渲染 -> 最终成片。
  适用于中国古代寓言/成语故事的短视频自动生产。
triggers:
  - "寓言视频制作"
  - "fable video"
  - "制作寓言视频"
  - "亡羊补牢"
metadata:
  tier: 1
  category: video-production
  user_visible: true
---

# Fable Video Pipeline

执行标准：先拿到素材后，直接端到端产出成片，不要在未完成时空转轮询。

## 1. 输入
- 故事中文文案
- 角色设定（单主角或多角色）
- 输出目录：默认 `/usr/local/lib/hermes-agent/fable-output/<故事名>/`

## 2. 固定角色块（用于角色一致性）
按故事自定义，嵌入每个分镜 prompt。示例：

- 平民养羊人：短黑发髻、布衣、褐袍、布腰带、布裤、草鞋
- 多角色时，必须为每个角色建独立描述块，并显式区分服饰颜色

## 3. 分镜脚本（JSON）
`voiceover_script.json`：
```json
[
  {"id": "title", "cn": "...", "en": "...", "dur_est": 5},
  {"id": "scene_1", "cn": "...", "en": "...", "dur_est": 7}
]
```

## 4. 图生流程
- 调用路径：`sn_agent_runner.py sn-image-generate`
- 传入 `--save-path`，不要用 `-o` 当保存路径
- 必要参数：`--image-size 2K --aspect-ratio 16:9 --timeout 900`
- 输出：`render/<id>.png`

## 5. 配音流程（Edge-TTS）
- 命令：`edge-tts --voice en-US-GuyNeural --text "..." --write-media audio_<id>.mp3`
- 文本必须从 `voiceover_script.json` 的 `en` 字段取，严禁用 Whisper 转录音频生成字幕文本（TTS 发音错误会被转录进字幕）

## 6. 时间戳准则
- 用 `ffprobe` 精确读取每个音频时长
- 累加生成 ASS 时间戳，不缩放
- 最后一个字幕条延长到视频结束，覆盖 concat 帧对齐误差

## 7. 字幕渲染（ASS）
- 使用 `subtitles=` 滤镜，不要用 `drawtext` 多行文本
- 中文字体：`Noto Serif CJK SC`；英文字体：`Noto Serif CJK SC`
- 中英同时间段叠加，中文在上，英文在下
- 必须 `WrapStyle: 0`，避免多行跳动

## 8. 交付与运行脚本
- 对于每次运行，上下文来自 Hermes 对话中的用户输入。
- 用户通常不会手动运行脚本；流水线由 Hermes agent 直接调用执行。
- 要得到最新、权威的管道定义，请始终读取当前文件或执行解释性命令；不要凭记忆或假设过期版本。

## 9. 片段合成
- 每个片段：静态图 + 对应音频
- `-t` 用音频实际时长
- scale/pad 到 1920x1080

## 10. 拼接
- `concat` 列表：每行格式为 `file '<绝对路径>'\n`
- 必须 ` -safe 0`
- 常见错误：缺少 `file ` 前缀、路径空字符串、缺少行尾换行

## 11. 成片命名
`<故事名>_v1.mp4`，仅对已落齐素材先出首版，避免无限等待缺失素材。

## 12. 验证与交付
- 用 `ffprobe` 验证时长和分辨率
- 至少抽帧 2 帧做字幕与语音一致性视觉确认
- 若 Telegram 可用，直接通过 `MEDIA:` 路径发送；若不可用，给出本地路径

## 已知阻塞模式
1. SenseNova `500 internal error`：某些 scene 连续失败时，终止重试，先用已有图出首版
2. Edge-TTS 专有名词发音偏差：如需人名地名准确，改用付费 TTS 或简化角色名
3. 字幕源错误：ASS 文本来源只能是 `voiceover_script.json`
