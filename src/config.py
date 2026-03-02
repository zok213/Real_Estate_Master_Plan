"""
config.py — Central configuration for WHA Auto Design AI
All API keys, model names, file paths, and tunable settings live here.
"""
import os

# ─── ConvertAPI (DWG → PNG cloud conversion) ─────────────────────────────────
CONVERTAPI_SECRET: str = os.environ.get("CONVERTAPI_SECRET", "")

# ─── Phase 1 Cloud VLM (OpenRouter → Qwen2.5-VL-72B) ────────────────────────
# Requires OPENROUTER_API_KEY env var — get a free key at https://openrouter.ai
# The free-tier model qwen2.5-vl-72b-instruct:free has no per-token charge.
OPENROUTER_API_KEY: str = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
VLM_MODEL: str = os.environ.get(
    "VLM_MODEL",
    "qwen/qwen2.5-vl-72b-instruct:free",
)

# ─── Phase 2 Cloud Image Generation (Google Gemini) ──────────────────────────
# Requires GEMINI_API_KEY env var — get a free key at https://aistudio.google.com
# gemini-2.0-flash-preview-image-generation supports multi-image input + output.
GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
GEMINI_IMAGE_MODEL: str = "gemini-2.0-flash-preview-image-generation"

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
