# WHA AI Master Plan POC

**Client:** WHA Corporation (WHA Group), Thailand  
**Domain:** Industrial Estate Development — Land Subdivision & Master Planning  
**Regulator:** IEAT — Industrial Estate Authority of Thailand, Regulations B.E. 2555 (2012)  
**Sites:** WHA RY36 (Rayong), WHA GVTP, WHA IER

An AI-powered industrial master plan generator. Upload a site boundary DWG to get a structured layout analysis and WHA-style master plan image, respecting IEAT regulations and WHA product standards.

**Run:** streamlit run src/app.py   =>   http://localhost:8512

---

## How It Works

```
DWG / PNG upload  (pink boundary, blue roads, brown contours)
      |
      v
dwg_utils.py  --  ConvertAPI (DWG -> PNG)
      |
      v  PIL Image
+------------------------------------------------------------+
|  Three-Tier Constraint Hierarchy                           |
|                                                            |
|  PRIORITY 1 -- BOUNDARY INTEGRITY (Non-Negotiable)        |
|    All roads/plots must lie 100% within pink boundary     |
|    Pink polygon = hard mask, not a soft guideline          |
|                                                            |
|  PRIORITY 2 -- ROAD SKELETON (Before any plot is drawn)   |
|    30m spine -> 16m grid -> block definition               |
|    IEAT Clause 6.1 (primary 30m), 6.3 (secondary 16m)    |
|                                                            |
|  PRIORITY 3 -- PLOT SUBDIVISION MATRIX (From roads)       |
|    J-series: 8,000-14,000 sqm, aspect 1:1-1:3             |
|    A-series: edge plots; C-series: mega-blocks             |
+------------------------------------------------------------+
      |
      v
+------------------------------------------------------------+
|  WhaAISession (ai_client.py) -- Three-Phase Pipeline      |
|                                                            |
|  Phase A -- LAYOUT DRAFTING  [phase1_understand()]        |
|    Qwen2.5-VL-7B-Instruct  (LOCAL, transformers)          |
|    Input:  DWG topo + WHA reference plans                  |
|    Output: boundary cartography, basin nominations,        |
|            road skeleton, plot matrix, site params         |
|                                                            |
|  Phase B -- CONSTRAINT OPTIMISATION [phase2_generate()]   |
|    Qwen-Image-Edit-2511  (LOCAL, diffusers)                |
|    Pink boundary preprocessor: 35px enforcement           |
|    Gravity-first: ponds -> WWTP -> substation              |
|    Target: saleable >=70%, green buffer >=5%               |
|    Note: AI-simulated; constraint solver TBD               |
|                                                            |
|  Phase C -- REGULATORY VERIFICATION [edit() / review]     |
|    IEAT B.E. 2555 clause-by-clause compliance check        |
|    Road widths, pond sizing, WWTP setbacks, hydrants       |
|    Note: AI-reasoned; programmatic rule engine TBD         |
|                                                            |
|  Edit loop -- iterative refinement                         |
|    Re-calls pipeline with last image + instruction         |
+------------------------------------------------------------+
```

---

## Input Requirements

### Acceptable formats

| Format | Status | Notes |
|---|---|---|
| DWG (AutoCAD) | Recommended | Converted to PNG via ConvertAPI (Aspose-CAD) |
| PNG from CAD export | Acceptable | >=150 DPI, >=2000 x 2000 px for any site > 50 rai |
| JPEG mobile photo | Not acceptable | JPEG artifacts corrupt boundary line detection |

### Required colour coding

| Colour | Represents |
|---|---|
| Pink / Magenta | Legal site boundary and internal zone divisions |
| Blue | External public roads (arterial connections) |
| Brown / Red | Elevation contour lines (topographic depression detection) |

### Boundary rules

- Pink boundary must form a fully closed polygon -- any gap causes plots to extend outside the legal limit
- 100% of the developable site must be within frame; external roads visible >=200m beyond boundary
- Pre-check that the DWG layer BOUNDARY is locked and complete before upload

---

## Project Structure

```
WHA_AI_MasterPlan_POC/
+-- src/
|   +-- app.py            # Streamlit UI (port 8512)
|   +-- ai_client.py      # Three-phase AI pipeline
|   +-- config.py         # Model names, paths, inference settings
|   +-- prompts.py        # System + generation prompts (IEAT-aware)
|   +-- dwg_utils.py      # DWG -> PNG via ConvertAPI
+-- output/               # Generated master plans saved here
+-- tools/
|   +-- autocad_converter.py  # Local AutoCAD COM automation (DWG->DXF)
+-- third_party/          # Git submodules
|   +-- Qwen-Image/       # QwenLM model cards + LoRA training guide
|   +-- ComfyUI/          # Alternative Phase B backend (ControlNet)
|   +-- diffusers/        # HF diffusers (QwenImageEditPlusPipeline)
|   +-- LocalAI/          # Local OpenAI-compatible server reference
+-- docs/                 # Project documentation
+-- ARCHITECTURE.md       # Pipeline deep-dive, IEAT compliance status
+-- requirements.txt
+-- .gitignore
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

Phase B local inference requires PyTorch + CUDA.
Default `requirements.txt` installs CPU-only torch.

**GPU requirements:**

| Tier | Hardware | VRAM | Notes |
|---|---|---|---|
| Minimum | 1x RTX 4090 | 24 GB | Phase A + Phase B, slower generation (~10-15 min/image) |
| Recommended (full flow) | 2x RTX 4090 | 48 GB total | Full pipeline, parallel Phase A+B, production speed |

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu124
```

First run downloads Qwen-Image-Edit-2511 weights (~16 GB) automatically.

### 3. Configuration

In src/config.py or as environment variables:

| Variable | Purpose | Default |
|---|---|---|
| CONVERTAPI_SECRET | DWG -> PNG cloud conversion | hardcoded in config |
| LOCAL_VLM_MODEL | Phase A VLM model name | Qwen/Qwen2.5-VL-7B-Instruct |
| LOCAL_INFERENCE_DEVICE | auto / cuda / cpu | auto |
| HF_HOME | Override HuggingFace model cache path | system default |

### 4. Run

```bash
streamlit run src/app.py --server.port 8512
```

---

## Models Used

All models run 100% locally -- no API keys, no cloud, no client data leaves the machine.

| Phase | Model | Library | Size |
|---|---|---|---|
| Phase A -- Layout Drafting VLM | Qwen/Qwen2.5-VL-7B-Instruct | transformers | ~15 GB |
| Phase B -- Plan Generation | Qwen/Qwen-Image-Edit-2511 | diffusers | ~16 GB |

Weights download automatically to ~/.cache/huggingface on first run.
Both phases fall back to demo mode silently if torch/GPU is unavailable.

---

## IEAT Compliance Status

| IEAT Clause | Requirement | Status |
|---|---|---|
| Clause 6.1 | Primary road >=30m ROW (>1,000 rai estates) | Implemented |
| Clause 6.3 | Secondary road >=16m ROW | Implemented |
| Clause 7 | Road gradient <=4% | Implemented |
| Clause 15-16 | Storm drainage: Rational Method (Q=0.278xCxIxA) | Partial |
| Clause 20 | Pump house at every retention pond | Implemented |
| Clause 21 | Flood berm >=10-yr flood + 50cm | Planned |
| Clause 30 | WWTP: 80% of daily water supply volume | Partial |
| Clause 31 | Sewage system separate from storm drainage | Implemented |
| Clause 36 | Power: 50 KVA per saleable rai | Planned |
| Clause 38 | Fire hydrant <=150m spacing | Planned |
| IEAT General | Green buffer >=5% of total site area | Implemented |
| WHA Standard | Saleable area >=70% of total site area | Implemented |

---

## Prototype Disclosure

This system is a Proof of Concept (POC). The AI engine analyses site topography against historical WHA reference plans and encoded IEAT rules to produce a structured layout analysis. Phases B and C (constraint optimisation and regulatory verification) are currently AI-simulated within a single pass, not mathematically computed by dedicated solvers. All output is a generative draft requiring expert human review before engineering or legal use.

Output is:
- Schematic master plan narrative -- suitable for human review
- Parameter recommendations -- for constraint engine input
- IEAT compliance flag report -- identifies gaps for resolution
- NOT an IEAT-approved plan
- NOT a statutory land subdivision document
- NOT a warranted boundary definition

---

## Documentation

- [Architecture Analysis](ARCHITECTURE.md) -- pipeline deep-dive, IEAT compliance, improvement roadmap
- [Executive Summary](docs/01_Executive_Summary.md)
- [Technical Architecture](docs/02_Technical_Architecture.md)
- [Implementation Guide](docs/03_Implementation_Guide_2Weeks.md)
- [Demo Script](docs/08_Demo_Script.md)
