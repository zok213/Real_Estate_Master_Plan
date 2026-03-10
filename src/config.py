"""
config.py — Central configuration for WHA Auto Design AI
All API keys are loaded from environment variables.
  - Local dev:  set values in .env  (see .env.example)
  - Production: set as HF Spaces Secrets (Settings → Variables and secrets)
"""
import os
from dotenv import load_dotenv

# Load .env for local development — no-op when running in Docker / HF Spaces
load_dotenv()

# ─── ConvertAPI (DWG → PNG cloud conversion) ─────────────────────────────────
CONVERTAPI_SECRET: str = os.environ.get("CONVERTAPI_SECRET", "")

# ─── Phase 1 Cloud VLM (OpenRouter → Qwen3-VL-235B-A22B-Thinking) ────────────
# Set PHASE1_ENABLED = False when the OpenRouter key is revoked / inactive.
PHASE1_ENABLED: bool = False
OPENROUTER_API_KEY: str = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
VLM_MODEL: str = "qwen/qwen3-vl-235b-a22b-thinking"

# ─── Phase 2 Cloud Image Generation (Google Gemini) ──────────────────────────
# Set PHASE2_ENABLED = False to disable Gemini calls.
PHASE2_ENABLED: bool = True
GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
GEMINI_IMAGE_MODEL: str = "gemini-3.1-flash-image-preview"

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
    os.path.join(LORA_DIR, f"{i}.png") for i in range(1, 7)
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
    os.path.join(LORA_DIR, "6.png"),
]

# ─── IEAT / Site Constraints ──────────────────────────────────────────────────
PRIMARY_ROAD_WIDTH_M: float = 30.0
SECONDARY_ROAD_WIDTH_M: float = 16.0
MIN_SALEABLE_RATIO: float = 0.70       # 70 %
MIN_GREEN_BUFFER_RATIO: float = 0.05   # 5 %
