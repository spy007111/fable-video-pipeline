# FableVideo Pipeline（Deep Dive）

本文件补充 `SKILL.md`，解释底层步骤与命令细节。适合定制者与二次开发者参考。

## 1. 素材准备

| 文件 | 说明 | 位置 |
|------|------|------|
| `voiceover_script.json` | 镜头级中文/英文文案、镜头 ID、预估时长 | 项目根目录或 `examples/` |
| `CHARACTERS.md` | 角色外貌与服饰色系定义 | 项目根目录或 `examples/` |

## 2. 绘图

## 注意
1. 启动前需要确保第三发脚本能访问到的 SenseNova 账户，内有足够点数可创建图。
2. 使用别的账号、API 来源也可以，但需要先确认对方版本是否支持 `--save-path` 参数。若函数签名不同，需升级 `sn_agent_runner.py`。
3. 若出现许可问题（401/403），先确认 API 来源；不是所有版本都支持 `--save-path` 覆盖。
4. 先使用 `timeout 5` 快速验证连通性，不要直接上长超时。

### 连接验证

```bash
# 替代命令 - 只验证连通，不生成图片
curl -s -o /dev/null -w "%{http_code}" \
  -X POST "$SN_BASE_URL/images/generations" \
  -H "Authorization: Bearer $SN_IMAGE_GEN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'  # Empty request, expect 401/400 not connection error
```

期望：返回 4xx（API 可达，认证或参数错误），而非连接超时。

### 调用规范

```bash
python3 ~/.hermes/skills/sense-nova-skills/scripts/sn_agent_runner.py \
  sn-image-generate \
  --prompt "$PROMPT" \
  --image-size 2k \
  --aspect-ratio 16:9 \
  --timeout 900 \
  --save-path "$OUTPUT_PATH"
```

**关键点：**

- `--prompt`：必须包含完整 CHARACTER 块与 `NO TEXT/NO LETTERS/NO ENGLISH` 后缀
- `--save-path`：目标文件绝对路径，目录需存在
- `--image-size 2k`：固定 2K（约 2048px），非 2K 可能不通过
- `--timeout`：单请求最长等待（秒）；长 prompt 建议 900–1200
- **禁止**用 `-o` 或其他未认证字段当输出路径

### 超时与重试

| 现象 | 做法 |
|------|------|
| `ReadTimeout`（sensenova） | 同 prompt 重试，先加大 `--timeout` |
| 连续 500 error（>3 次） | 终止，用现有图出首版 |
| 输出与预期风格偏差大 | 检查提示词末尾是否有 `NO TEXT/NO LETTERS` |

## 3. 配音（Edge-TTS）

```bash
edge-tts --voice en-US-GuyNeural \
  --text "$(jq -r '.[] | select(.id=="scene_1") | .en' voiceover_script.json)" \
  --write-media audio/scene_1.mp3
```

**注意：**
- 禁止用 Whisper 转录音频得到字幕文本（会固化 TTS 发音错误）
- 文本必须来自 `voiceover_script.json[].en`
- 专有名词（人名、地名）若发音不准，直接改脚本文本

## 4. 字幕（ASS V4+）

ASS 文件头部必须包含：

```ini
[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Chinese,Noto Serif CJK SC,60,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,2,10,10,40,1
Style: English,Noto Serif CJK SC,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,2,10,10,80,128

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,Chinese,,0,0,0,,{中文字幕内容}
Dialogue: 0,0:00:00.00,0:00:05.00,English,,0,0,0,,{英文字幕内容}
```

## 5. 片段合成（单镜头）

```bash
ffmpeg -loop 1 -i render/scene_1.png -i audio/scene_1.mp3 \
  -c:v libx264 -tune stillimage -shortest \
  -c:a aac -b:a 192k -ar 44100 \
  -pix_fmt yuv420p \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" \
  clips/scene_1.mp4
```

**参数解读：**

- `-loop 1`：将图片循环成视频流
- `-shortest`：在最短流结束时停止（以音频为准）
- `-tune stillimage`：HE 编码静帧优化的码率分配
- `scale=...force_original_aspect_ratio=decrease,pad=...`：等比缩放 + 黑边填充到 1080p

## 6. 拼接成片

先生成 `concat_list.txt`：

```
file '/absolute/path/to/clips/scene_1.mp4'
file '/absolute/path/to/clips/scene_2.mp4'
```

**注意：**
- 必须是**绝对路径**
- `file ` 后有空格
- 每行末尾必须换行 `\n`

```bash
ffmpeg -f concat -safe 0 -i concat_list.txt \
  -c copy -movflags +faststart \
  ${STORY_NAME}_v1.mp4
```

## 7. 验证

```bash
# 视频信息
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration \
  -of default=noprint_wrappers=1 ${STORY_NAME}_v1.mp4

# 抽帧视觉检查
ffmpeg -i ${STORY_NAME}_v1.mp4 -ss 00:00:05 -vframes 1 frame_05s.jpg
ffmpeg -i ${STORY_NAME}_v1.mp4 -ss 00:00:15 -vframes 1 frame_15s.jpg
```

## 8. 常见错误排查

| 错误 | 原因 | 解决 |
|------|------|------|
| `No such file or directory` when running ffmpeg | 绝对路径写错或文件不存在 | 用 `readlink -f` 或目录存在性检查 |
| 字幕错位 | ASS Start/End 时间戳错误 | 用 ffprobe 实测音频时长后再累加 |
| 画面比例拉伸 | pad/scale 顺序错误 | 先 scale 再 pad，不设 `setsar` |
| 长 prompt 超时 | `--timeout` 不足或网络波动 | 增大到 900–1200；重试同 prompt |
| 字幕闪烁/跳动 | WrapStyle 不是 0 | ASS 设置 `WrapStyle: 0` |

## 9. 扩展方向

- **多语言 Q&A**：增加 TTS 音色选择 + 字幕语言切换参数
- **批量生产**：并行调度多部故事
- **风格导出**：每个 prompt 底加风格词（国风/现代/赛博）
- **视频分轨**：添加背景音乐（`amix` 滤镜）

---

生成时间：2026-06-04Fixed: 2026-06-05
维护：FableVideo Pipeline Contributors
