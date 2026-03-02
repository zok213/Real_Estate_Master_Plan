"""
config.py — Central configuration for WHA Auto Design AI
All API keys, model names, file paths, and tunable settings live here.
"""
import os

# ─── ConvertAPI (DWG → PNG cloud conversion) ─────────────────────────────────
CONVERTAPI_SECRET: str = os.environ.get(
    "CONVERTAPI_SECRET",
    "***REMOVED_CONVERTAPI_KEY***",
)

# ─── OpenRouter (Phase 1 VLM) ────────────────────────────────────────────────
# Phase 1 vision analysis uses Qwen2.5-VL via OpenRouter free tier.
OPENROUTER_API_KEY: str = os.environ.get(
    "OPENROUTER_API_KEY",
    "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",
)
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

# Phase 1 VLM — Qwen2.5-VL via OpenRouter (free, vision-capable).
# Swap to any OpenRouter vision model as needed:
#   qwen/qwen2.5-vl-32b-instruct:free
#   qwen/qwen3-vl-235b-a22b-thinking  (heavy thinking, slower)
#   meta-llama/llama-3.2-11b-vision-instruct:free
VLM_MODEL: str = "qwen/qwen2.5-vl-72b-instruct:free"

# ─── Phase 2 Local Image Generation (diffusers) ──────────────────────────────
# Qwen-Image-Edit-2511 runs LOCALLY via HuggingFace diffusers library.
# No API key or cloud service needed — model weights download on first run
# to: ~/.cache/huggingface/hub  (~16 GB for fp16 weights)
#
# Requirements: pip install torch diffusers transformers accelerate
# GPU strongly recommended (CUDA); CPU fallback supported but very slow.
#
# Model card: https://huggingface.co/Qwen/Qwen-Image-Edit-2511
# Source:     https://github.com/QwenLM/Qwen-Image
IMG_GEN_MODEL: str = "Qwen/Qwen-Image-Edit-2511"

# Compute device for local inference: "cuda", "cpu", or "auto"
# "auto" → uses CUDA if available, otherwise CPU.
LOCAL_INFERENCE_DEVICE: str = os.environ.get("LOCAL_INFERENCE_DEVICE", "auto")

# HuggingFace hub cache directory (set empty to use default ~/.cache/huggingface)
HF_HOME: str = os.environ.get("HF_HOME", "")

# ─── Root Paths ───────────────────────────────────────────────────────────────
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(_SRC_DIR)

LORA_DIR = os.path.join(ROOT_DIR, "lora")
EXPERT_DIR = os.path.join(ROOT_DIR, "expert_reasoning")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")
INPUT_DIR = os.path.join(ROOT_DIR, "input")

# Path where the last uploaded topo image is cached so it survives browser refreshes
TOPO_CACHE_PATH: str = os.path.join(OUTPUT_DIR, "topo_cache.png")

# ─── Reference & Target Image Lists ──────────────────────────────────────────
REFERENCE_PLAN_PATHS: list[str] = [
    os.path.join(LORA_DIR, f"{i}.png") for i in range(1, 6)
]

TARGET_EXAMPLE_PATHS: list[str] = [
    os.path.join(LORA_DIR, f"target{i}.png") for i in range(1, 4)
]

# Few-shot visual style references for Phase 2 image generation.
# All 7 completed WHA master plan examples ordered by teaching priority:
#   target1-3 = closest output style (boundary conformance + labelling)
#   2-5       = broader style library (road grid variety, edge clipping)
# Sent at 1280px quality-95 so model reads fine detail: hatch density,
# label font size, border weight, exact boundary clipping of edge plots.
FEW_SHOT_PATHS: list[str] = [
    os.path.join(LORA_DIR, "target1.png"),
    os.path.join(LORA_DIR, "target2.png"),
    os.path.join(LORA_DIR, "target3.png"),
    os.path.join(LORA_DIR, "2.png"),
    os.path.join(LORA_DIR, "3.png"),
    os.path.join(LORA_DIR, "4.png"),
    os.path.join(LORA_DIR, "5.png"),
]

# ─── IEAT / Site Constraints ──────────────────────────────────────────────────
PRIMARY_ROAD_WIDTH_M: float = 30.0
SECONDARY_ROAD_WIDTH_M: float = 16.0
MIN_SALEABLE_RATIO: float = 0.70       # 70 %
MIN_GREEN_BUFFER_RATIO: float = 0.05   # 5 %
