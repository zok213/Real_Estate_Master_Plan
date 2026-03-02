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

# ─── Phase 1 Local VLM (Qwen2.5-VL via transformers) ────────────────────────
# Runs LOCALLY — no API key, no internet required after first weight download.
# Weights download automatically on first run (~15 GB for 7B, ~150 GB for 72B).
#
# Recommended defaults by hardware:
#   RTX 3090 / 4090 (24 GB VRAM)  → Qwen/Qwen2.5-VL-7B-Instruct
#   A100 / H100 (40–80 GB VRAM)  → Qwen/Qwen2.5-VL-72B-Instruct
#   CPU only (slow)               → Qwen/Qwen2.5-VL-3B-Instruct
#
# Model card: https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct
LOCAL_VLM_MODEL: str = os.environ.get(
    "LOCAL_VLM_MODEL",
    "Qwen/Qwen2.5-VL-7B-Instruct",
)

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
