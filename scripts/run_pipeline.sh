#!/bin/bash
# Fable Video Pipeline - Run Script
set -e

# 设置基础变量
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/build"
OUTPUT_DIR="$BUILD_DIR/output"
RENDER_DIR="$BUILD_DIR/render"
AUDIO_DIR="$BUILD_DIR/audio"
TEMP_DIR="$BUILD_DIR/temp"

# 需要用户提供的故事名（用于构建路径）
if [ -z "$1" ]; then
    echo "使用方法: $0 <故事名> [voiceover_script_path]"
    echo "示例: $0 wuyangbulao examples/wuyangbulao.json"
    exit 1
fi

STORY_NAME="$1"
VOICEOVER_SCRIPT="${2:-$PROJECT_ROOT/examples/voiceover_script.json}"
STORY_BUILD_DIR="$BUILD_DIR/$STORY_NAME"
RENDER_DIR="$STORY_BUILD_DIR/render"
AUDIO_DIR="$STORY_BUILD_DIR/audio"
OUTPUT_DIR="$STORY_BUILD_DIR/output"
TEMP_DIR="$STORY_BUILD_DIR/temp"

mkdir -p "$RENDER_DIR" "$AUDIO_DIR" "$OUTPUT_DIR" "$TEMP_DIR"

# 检查依赖工具
check_dependencies() {
    local missing=()
    for cmd in python3 ffmpeg ffprobe curl jq; do
        if ! command -v "$cmd" &> /dev/null; then
            missing+=("$cmd")
        fi
    done
    if [ ${#missing[@]} -ne 0 ]; then
        echo "缺失依赖: ${missing[*]}"
        echo "请先安装: sudo apt-get install -y python3 ffmpeg jq curl"
        exit 1
    fi
}

echo "=== 1. 构建词汇表 ==="
echo "步骤待实现：从 voiceover_script.json 汇总英文词表"
echo "[!] 词汇表生成暂为占位。按 1 跳过"

echo "=== 2. 逐镜头生成图片 ==="
python3 "$SCRIPT_DIR/03_generate_image.py" \
    --script "$VOICEOVER_SCRIPT" \
    --output-dir "$RENDER_DIR" \
    --story-name "$STORY_NAME"

echo "=== 3. 逐镜头生成配音 ==="
python3 "$SCRIPT_DIR/04_generate_audio.py" \
    --script "$VOICEOVER_SCRIPT" \
    --output-dir "$AUDIO_DIR" \
    --voice "en-US-GuyNeural"

echo "=== 4. 生成字幕 ASS ==="
python3 "$SCRIPT_DIR/05_generate_subtitles.py" \
    --script "$VOICEOVER_SCRIPT" \
    --audio-dir "$AUDIO_DIR" \
    --output-ass "$TEMP_DIR/subtitles.ass" \
    --story-name "$STORY_NAME"

echo "=== 5. 合成最终视频 ==="
python3 "$SCRIPT_DIR/06_compose_video.py" \
    --render-dir "$RENDER_DIR" \
    --audio-dir "$AUDIO_DIR" \
    --subtitle-ass "$TEMP_DIR/subtitles.ass" \
    --script "$VOICEOVER_SCRIPT" \
    --output-path "$OUTPUT_DIR/${STORY_NAME}_v1.mp4"

echo "=== 完成 ==="
echo "视频输出: $OUTPUT_DIR/${STORY_NAME}_v1.mp4"
