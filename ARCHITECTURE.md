# WHA AI Master Plan POC -- Architecture Analysis

> Engineering assessment aligned with Standard Operating Procedure v1.0 (March 2026).
> Client: WHA Corporation | Regulator: IEAT B.E. 2555 | Sites: WHA RY36, GVTP, IER

---

## System Overview

`
+-------------------------------------------------------------------+
|   User (browser)  <->  Streamlit (port 8512)                      |
|                                                                   |
|   +-------------------+     +-------------------------------+    |
|   | DWG / PNG upload  |---->| dwg_utils.py  (ConvertAPI)    |    |
|   +-------------------+     +---------------+---------------+    |
|                                             | PIL Image           |
|   +-----------------------------------------v-----------------+  |
|   | Three-Tier Constraint Hierarchy                            |  |
|   |                                                             |  |
|   |  PRIORITY 1 -- BOUNDARY INTEGRITY  (Non-Negotiable)        |  |
|   |    Pink polygon = hard mask. 100% containment enforced.    |  |
|   |    Violations: legal title non-compliance, IEAT rejection  |  |
|   |                                                             |  |
|   |  PRIORITY 2 -- ROAD SKELETON  (Before any plot is drawn)   |  |
|   |    Step 1: 30m primary spine from blue road inward         |  |
|   |    Step 2: 16m secondary grid -> 300-400m block definition  |  |
|   |    Step 3: ONLY THEN subdivide blocks into plots            |  |
|   |    IEAT Clause 6.1 (primary 30m), Clause 6.3 (secondary)   |  |
|   |                                                             |  |
|   |  PRIORITY 3 -- PLOT SUBDIVISION MATRIX  (From roads)        |  |
|   |    J-series: 8,000-14,000 sqm, aspect 1:1-1:3              |  |
|   |    A-series: edge plots (boundary angle), C-series: mega   |  |
|   |    Utility zones designated BEFORE plot numbering begins    |  |
|   +-------------------------------------------------------------+  |
|                                             |                      |
|   +-----------------------------------------v-----------------+  |
|   | WhaAISession  (ai_client.py)                               |  |
|   |                                                             |  |
|   |  Phase A -- LAYOUT DRAFTING  [phase1_understand()]         |  |
|   |    Qwen2.5-VL-7B-Instruct (LOCAL, transformers)            |  |
|   |    Reads DWG topo + WHA reference plans                    |  |
|   |    -> boundary cartography, basin nominations,             |  |
|   |       road skeleton, draft plot matrix, site params        |  |
|   |                                                             |  |
|   |  Phase B -- CONSTRAINT OPTIMISATION  [phase2_generate()]   |  |
|   |    QwenImageEditPlusPipeline (LOCAL, diffusers)             |  |
|   |    _preprocess_topo_for_gen(): 35px pink boundary enforce  |  |
|   |    Gravity-first utility placement:                         |  |
|   |      Low points -> Retention Ponds -> WWTP ->              |  |
|   |      Substation at boundary/grid proximity                  |  |
|   |    Targets: saleable >=70%, green buffer >=5%              |  |
|   |    Note: AI-simulated; dedicated solver not yet connected  |  |
|   |                                                             |  |
|   |  Phase C -- REGULATORY VERIFICATION  [edit() / review]     |  |
|   |    IEAT B.E. 2555 clause-by-clause reasoning               |  |
|   |    Road widths, pond sizing, WWTP setbacks, hydrant grid   |  |
|   |    Note: AI-reasoned; programmatic rule engine TBD         |  |
|   |                                                             |  |
|   |  Edit loop -- iterative refinement                          |  |
|   |    QwenImageEditPlusPipeline(last_image, instruction)       |  |
|   +-------------------------------------------------------------+  |
|                                                                   |
|   third_party/                                                    |
|     Qwen-Image/   -- reference code + LoRA training guide        |
|     ComfyUI/      -- alternative Phase B backend (ControlNet)    |
|     diffusers/    -- source of QwenImageEditPlusPipeline         |
|     LocalAI/      -- alternative local API server (future)       |
+-------------------------------------------------------------------+
`

---

## Phase A -- Layout Drafting  (Qwen2.5-VL-7B-Instruct, LOCAL)

**GOOD:**
- Fully local -- zero cloud cost, no data leaves the machine (satisfies SOP
  Chain of Custody: client DWG files are never transmitted externally).
- Qwen2.5-VL-7B reads pink boundary lines, brown contour density, and blue
  road connection points directly from the DWG-exported PNG.
- Asking targeted structured questions (boundary, basins, entry, constraints)
  produces the five output elements required by the SOP: boundary cartography,
  depression mapping, road skeleton, plot draft, site parameter set.
- AutoProcessor handles image resizing and tokenisation; bfloat16 + device_map
  auto manages VRAM.

**BAD / RISK:**
- The 7B model is significantly weaker than 72B for reading dense CAD drawings
  -- label font sizes, plot codes, and dimension text at 1280px may be missed.
- Phase A analysis feeds Phase B as text only (max 600 chars). The VLM spatial
  reasoning (where the entry point IS on the image) is lost -- Phase B cannot
  see marked coordinates unless they are drawn on the topo image.
- VRAM: ~15 GB for 7B bfloat16. On machines with <16 GB VRAM the model may
  OOM or fall back to CPU (slow, ~5-10 min for a single analysis pass).

**IMPROVEMENT IDEAS:**
1. After Phase A, extract coordinates from the narrative and draw  entry arrows
   + basin circles on the preprocessed topo before passing to Phase B --
   direct spatial signal for the generator (SOP requirement: spatial feedback loop).
2. Upgrade to Qwen2.5-VL-32B (quantised to 4-bit via bitsandbytes) for better
   CAD label reading without full 72B VRAM cost.
3. Prompt the model to output Phase 1-5 in structured JSON matching the SOP
   output table (boundary cartography, depression map, road skeleton, plot
   matrix, site parameter set) rather than free-form prose.

---

## Phase B -- Constraint Optimisation  (Qwen-Image-Edit-2511, LOCAL)

**GOOD:**
- Running locally via diffusers = zero cloud cost, no rate limits, zero
  data-privacy risk (WHA site layouts never leave the machine).
- QwenImageEditPlusPipeline natively accepts multiple input images -- WHA
  style references + topo pass as a unified multi-image prompt.
- Qwen-Image-Edit-2511 is a 20B MMDiT model with genuine image composition
  understanding suitable for spatial fill and boundary-following tasks.
- BF16 CUDA inference uses ~20 GB VRAM (RTX3090/A100). CPU fallback works
  but takes 20-40 min per image.
- Demo fallback keeps the app runnable without GPU.

**BAD / RISK:**
- MAJOR: Model was not fine-tuned on industrial master plans. It has no built-in
  concept of plot codes J11/J12, WWTP grey hatch, or retention pond diagonal
  hatch. Style prompting battles the model's photorealistic training distribution.
- MAJOR: Boundary conformance is the hardest unsolved problem. The pink boundary
  preprocessor signals the edge, but a diffusion model in pixel space will
  still struggle to clip plot corners at exact diagonal boundary angles.
  The SOP requires 100% containment -- this is not geometrically guaranteed.
- Heavy VRAM requirement (20 GB+) blocks most laptops and cloud free tiers.
- num_inference_steps=40 at 20B scale = 5-15 min on consumer GPU, 20-40 min
  on CPU. Streamlit UI appears frozen with no progress bar.
- Phase B is currently AI-simulated constraint optimisation -- it does not run
  a mathematical solver. Plot areas are proportional estimates, not computed.

**IMPROVEMENT IDEAS:**
1. Fine-tune on WHA corpus: 200-step LoRA on 20-30 completed WHA plans would
   drastically improve style adherence and IEAT-aware layout reasoning.
   DiffSynth-Studio supports LoRA training in 4 GB VRAM via layer offload.
2. ComfyUI + ControlNet (Comfy-Org/ComfyUI in third_party/): For strict boundary
   tracing, ControlNet Canny/Scribble conditioning is technically more principled
   than prompting an image-edit model. Enforces hard pixel-level constraints.
3. LightX2V acceleration (QwenLM README): 25x inference speedup via diffusion
   distillation. Reduces 40-step inference to ~2 steps.
4. FP8 quantisation (DiffSynth-Studio): Cuts VRAM from ~20 GB to ~8 GB,
   enabling RTX3070/4070 execution.
5. Add Streamlit progress bar via pipeline callback_on_step_end.

---

## Phase C -- Regulatory Verification  (IEAT B.E. 2555)

**Current state:** Phase C runs inside the same AI analysis pass as Phase A/B.
The system cross-references the generated layout against embedded IEAT rules.
This is AI-reasoned -- not exhaustive automated clause verification.

**IEAT Compliance Implementation Status:**

| IEAT Clause | Requirement | Status |
|---|---|---|
| Clause 6.1 | Primary road >=30m ROW (>1,000 rai) | Implemented |
| Clause 6.3 | Secondary road >=16m ROW | Implemented |
| Clause 7 | Road gradient <=4% | Implemented |
| Clause 15-16 | Storm drainage Rational Method Q=0.278xCxIxA | Partial |
| Clause 20 | Pump house at every retention pond | Implemented |
| Clause 21 | Flood berm >=10-yr flood + 50cm | Planned |
| Clause 30 | WWTP: 80% of daily water supply volume | Partial |
| Clause 31 | Sewage system separate from storm drainage | Implemented |
| Clause 36 | Power: 50 KVA per saleable rai | Planned |
| Clause 38 | Fire hydrant <=150m spacing | Planned |
| IEAT General | Green buffer >=5% of total site area | Implemented |
| WHA Standard | Saleable area >=70% of total site area | Implemented |

**IMPROVEMENT IDEAS:**
1. Build a programmatic rule engine (Python functions for each IEAT clause)
   that evaluates the Phase A output JSON against numeric thresholds.
2. Connect to a constraint optimisation solver (OR-Tools / PuLP) for Phase B
   that guarantees 100% boundary containment, exact area ratios, and road
   dimensional compliance -- replacing the current AI simulation.

---

## Pre-Processor  (_preprocess_topo_for_gen)

**GOOD:**
- Pink boundary detection handles JPEG artifacts and anti-aliasing.
- 7x7 kernel x 5 iterations + binary_fill_holes closes small DWG line gaps.
- 35px bold pink wall is prominent for Phase B to read.
- Blue->grey road neutralisation prevents the model from re-styling external
  road reference lines.

**BAD:**
- Hard-coded colour thresholds (r-g > 40, b-g > 15) only work for WHA cerise/
  magenta. Different client CAD colour = wrong output, no warning.
- Cream fill blanks all internal annotations -- existing infrastructure context lost.

**IMPROVEMENT IDEAS:**
1. Make pink thresholds configurable in config.py or auto-detect dominant thin-line
   bright colour in the uploaded DWG.
2. Preserve a light greyscale version of internal annotations instead of blanking
   them entirely.

---

## Tool Ecosystem

| Repo | Role | Status |
|---|---|---|
| QwenLM/Qwen-Image | Model cards, LoRA training guide, prompt examples | Used as reference |
| huggingface/diffusers | Core dependency -- QwenImageEditPlusPipeline lives here | Direct dependency |
| Comfy-Org/ComfyUI | Alternative Phase B backend -- ControlNet boundary enforcement | Future option |
| mudler/LocalAI | Alternative local API server for Phase A (llama.cpp) | Future option |

---

## Current Output Quality

`
                CURRENT IMPLEMENTATION
+===========================================+
|  Phase A -- Layout Drafting   ######....  |  6/10  local 7B, CAD reading ok
|  Phase B -- Plan Generation   ####......  |  4/10  boundary fidelity gap
|  Preprocessor                 #######...  |  8/10  best component
|  UI (Streamlit)               ######....  |  7/10  add progress bar
|  Boundary conformance         ###.......  |  3/10  hard unsolved problem
|  IEAT compliance coverage     #####.....  |  5/10  partial -- 6/12 clauses
+===========================================+
`

**What makes this POC credible:**
- Zero external infrastructure -- single streamlit run command, fully local
- Three-tier constraint hierarchy matches IEAT engineering methodology
- Five-phase SOP output structure (boundary, basins, roads, plots, params)
- Pink boundary preprocessor is technically valid and creative
- End-to-end pipeline in clean Python; data never leaves the machine

**What prevents production use:**
1. Boundary conformance -- diffusion model cannot reliably trace an irregular polygon
   at sub-metre precision. Solution: ControlNet (ComfyUI) or constraint-inpainting.
2. No mathematical solver -- plot areas and saleable ratios are estimates only.
   Production requires OR-Tools / PuLP constraint engine.
3. VRAM requirement -- 20 GB for Phase B eliminates most hardware.
4. No spatial feedback loop -- Phase A text output does not mark coordinates on
   the topo image; Phase B cannot see spatial context unless visually annotated.
5. Phase C is AI-reasoned opinion, not exhaustive programmatic clause verification.

---

## Recommended Next Steps  (priority order)

1. Mark Phase A findings on topo image -- draw entry arrow + basin circles before
   Phase B receives the image (direct spatial signal, SOP requirement).
2. Add VRAM check on startup -- warn if VRAM < 20 GB before loading Phase B pipeline.
3. Add inference progress callback -- pipeline callback_on_step_end -> Streamlit bar.
4. LoRA fine-tune on 20-30 completed WHA drawings -- DiffSynth-Studio, 4 GB VRAM.
5. Build programmatic IEAT rule engine for Phase C -- Python functions per clause.
6. Evaluate ComfyUI + ControlNet Canny for Phase B boundary enforcement.
7. LightX2V acceleration -- reduces Phase B generation from ~15 min to ~2 min.

---

*Aligned with: Standard Operating Procedure v1.0, March 2026*
*Regulatory reference: IEAT Regulations B.E. 2555 (2012)*
