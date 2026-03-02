# WHA AI Master Plan POC

An AI-powered industrial master plan generator for WHA industrial estates.  
Upload a site boundary DWG → get a fully-labelled master plan image in WHA visual style.

**Live demo:** `streamlit run src/app.py` → http://localhost:8512

---

## How It Works

```
DWG file upload
      │
      ▼
dwg_utils.py  ──  ConvertAPI (cloud DWG→PNG)
      │
      ▼  PIL Image
┌─────────────────────────────────────────────────┐
│  WhaAISession  (ai_client.py)                   │
│                                                  │
  Phase 1 — Site Understanding  (LOCAL)          |
│    Qwen2.5-VL-7B via transformers               |
│    Reads reference plans + topo examples        │
│    → concise site facts (entry, basins)         │
│                                                  │
│  Phase 2 — Plan Generation                      │
│    Qwen-Image-Edit-2511 (LOCAL, diffusers)      │
│    Pink boundary preprocessor enforces edge     │
│    WHA style references injected for quality    │
│    → master plan PIL image                      │
│                                                  │
│  Edit loop — iterative refinement               │
│    Re-calls local pipeline with last image      │
└─────────────────────────────────────────────────┘
```

---

## Project Structure

```
WHA_AI_MasterPlan_POC/
├── src/
│   ├── app.py            # Streamlit UI (port 8512)
│   ├── ai_client.py      # Two-phase AI pipeline
│   ├── config.py         # API keys, model names, paths
│   ├── prompts.py        # System + generation prompts
│   └── dwg_utils.py      # DWG → PNG via ConvertAPI
├── lora/                 # WHA visual style references (9 images)
│   ├── 1.png … 5.png     # Broader style library
│   └── target1-3.png     # Closest output-style examples
├── output/               # Generated master plans saved here
├── tools/
│   └── autocad_converter.py  # Local AutoCAD COM automation (DWG→DXF)
├── third_party/          # Git submodules
│   ├── Qwen-Image/       # QwenLM model cards + LoRA training guide
│   ├── ComfyUI/          # Alternative Phase 2 backend (ControlNet)
│   ├── diffusers/        # HF diffusers source (QwenImageEditPlusPipeline)
│   └── LocalAI/          # Local OpenAI-compatible server reference
├── docs/                 # Project documentation
├── ARCHITECTURE.md       # AI engineering deep-dive analysis
├── requirements.txt
└── .gitignore
```

---

## Setup

### 1. Clone with submodules

```bash
git clone --recurse-submodules https://github.com/zok213/RealEstate
cd RealEstate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Phase 2 local inference requires PyTorch + CUDA.**  
> The default `requirements.txt` installs CPU-only torch.  
> For GPU (recommended — RTX 3090 / A100, ~20 GB VRAM):
> ```bash
> pip install torch --index-url https://download.pytorch.org/whl/cu124
> ```
> First run downloads Qwen-Image-Edit-2511 weights (~16 GB) automatically.

### 3. Configuration

In `src/config.py` or as environment variables:

| Variable | Purpose | Default |
|---|---|---|
| `CONVERTAPI_SECRET` | DWG → PNG cloud conversion | hardcoded in config |
| `LOCAL_VLM_MODEL` | Phase 1 VLM model name | `Qwen/Qwen2.5-VL-7B-Instruct` |
| `LOCAL_INFERENCE_DEVICE` | `"auto"` / `"cuda"` / `"cpu"` | `"auto"` |
| `HF_HOME` | Override HuggingFace model cache path | system default |

### 4. Run

```bash
streamlit run src/app.py --server.port 8512
```

---

## Models Used

All models run **100% locally** — no API keys, no cloud, no data leaves your machine.

| Phase | Model | Library | Size |
|---|---|---|---|
| Phase 1 VLM | `Qwen/Qwen2.5-VL-7B-Instruct` | `transformers` | ~15 GB |
| Phase 2 Image Gen | `Qwen/Qwen-Image-Edit-2511` | `diffusers` | ~16 GB |

Weights download automatically to `~/.cache/huggingface` on first run.  
Both phases fall back to demo mode silently if torch/GPU is unavailable.

---

## What Was Built

- **Full project cleanup** — removed TestFit adapters, OR-Tools engine, Pydantic models, and all dead code from the original scaffold
- **Gemini API fully removed** — replaced with Qwen-only pipeline (OpenAI SDK throughout, no Google SDK)
- **Local inference** — Phase 2 migrated from HuggingFace cloud Inference API to local `QwenImageEditPlusPipeline` (no API token, no rate limits, no data leaves the machine)
- **Pink boundary preprocessor** — 35 px bold boundary enforcement, interior cream fill, blue road neutralisation
- **WHA style references** — reference plans injected at 1280px quality-95 JPEG for visual consistency
- **Streamlit UI** — upload DWG, run Phase 1 silently, generate plan, iterative edit loop, remove site map button
- **Git setup** — repo at `https://github.com/zok213/RealEstate`, 4 submodules, comprehensive `.gitignore`

---

## Documentation

- [Architecture Analysis](ARCHITECTURE.md) — honest AI engineering assessment, scoring, improvement roadmap
- [Executive Summary](docs/01_Executive_Summary.md)
- [Technical Architecture](docs/02_Technical_Architecture.md)
- [Implementation Guide](docs/03_Implementation_Guide_2Weeks.md)
- [Demo Script](docs/08_Demo_Script.md)
