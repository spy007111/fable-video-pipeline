"""Configuration for Fable Video Pipeline."""

import os
from dataclasses import dataclass

# SenseNova 图像生成
SN_IMAGE_API_KEY: str = os.getenv("SN_IMAGE_GEN_API_KEY", "")
SN_BASE_URL: str = os.getenv("SN_BASE_URL", "https://api.sensenova.cn/v1")
SN_IMAGE_MODEL: str = "sensenova-u1-fast"

# Edge-TTS
DEFAULT_VOICE: str = "en-US-GuyNeural"

# 视频参数
WIDTH: int = 1920
HEIGHT: int = 1080
FPS: int = 24
PIX_FMT: str = "yuv420p"

# 字幕字体（检测顺序）
FONT_PATHS: list = [
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
]

# 超时（秒）
IMAGE_TIMEOUT: int = 900
AUDIO_TIMEOUT: int = 60

# 分镜类型（保留字幕、标题、寓意类不生成图片）
SKIP_IMAGE_TYPES: set = {"title", "moral", "subtitle", "quote"}
