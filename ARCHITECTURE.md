# WHA AI Master Plan POC — Architecture Analysis
> Deep engineering assessment: what works, what doesn't, how to improve.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│   User (browser)  ←→  Streamlit (port 8512)                     │
│                                                                   │
│   ┌─────────────────┐        ┌──────────────────────────────┐   │
│   │ DWG upload      │──PNG──▶│ dwg_utils.py (ConvertAPI)    │   │
│   └─────────────────┘        └──────────────┬───────────────┘   │
│                                              │ PIL Image          │
│   ┌─────────────────────────────────────────▼───────────────┐   │
│   │ WhaAISession  (ai_client.py)                             │   │
│   │                                                           │   │
│   │  Phase 1 ── phase1_understand()                          │   │
│   │    ├─ Load reference plans + target examples (lora/)     │   │
│   │    ├─ Encode to base64 data-URLs                         │   │
│   │    └─ OpenRouter → Qwen2.5-VL-72B (free) → site facts   │   │
│   │                                                           │   │
│   │  Phase 2 ── phase2_generate()                            │   │
│   │    ├─ _preprocess_topo_for_gen() (pink boundary enforce) │   │
│   │    ├─ Load 7 few-shot style references                   │   │
│   │    └─ diffusers QwenImageEditPlusPipeline (LOCAL)        │   │
│   │         → master plan PIL image                          │   │
│   │                                                           │   │
│   │  Edit ── edit()                                          │   │
│   │    └─ QwenImageEditPlusPipeline(last_image, instruction) │   │
│   └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│   third_party/                                                    │
│     Qwen-Image/   ← reference code + examples                    │
│     ComfyUI/      ← alternative Phase 2 backend (future)         │
│     diffusers/    ← source of QwenImageEditPlusPipeline          │
│     LocalAI/      ← alternative local API server (future)        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase-by-Phase Assessment

### Phase 1 — Site Understanding (Qwen2.5-VL-72B via OpenRouter)

**GOOD:**
- 72B vision model is genuinely capable of reading WHA reference plans and
  annotated drawings — label font size, plot codes, dimensions visible at 1280px.
- Free OpenRouter tier is cost-zero for low-volume POC use.
- OpenAI SDK used → trivial to swap models or switch to local later.
- Asking only 3 targeted questions (entry, basins, constraints) keeps responses
  concise and avoids hallucinated layout geometry.

**BAD / RISK:**
- OpenRouter free tier has daily quota limits and rate throttling. For demo days
  or concurrent users, the call can silently fail.
- The model response quality varies — the free tier serves smaller quantised
  variants at peak load; paid tier (`qwen2.5-vl-72b-instruct`) is more stable.
- Phase 1 analysis is fed to Phase 2 as text only (max 600 chars). The VLM
  reasoning about *where* to place features is lost — it can only describe,
  not spatially locate features in pixel coordinates.

**IMPROVEMENT IDEAS:**
1. Extract bounding boxes / polygons from Phase 1 (ask the VLM to output
   JSON with pixel coordinates of entry points and basins).
2. Overlay those coordinates on the topo image as coloured markers *before*
   sending to Phase 2 — direct spatial signal for the generator.
3. Fall back to `qwen/qwen2.5-vl-32b-instruct:free` when 72B quota is hit.

---

### Phase 2 — Plan Generation (Qwen-Image-Edit-2511 via diffusers, LOCAL)

**GOOD:**
- Running locally via diffusers = zero cloud cost, no rate limits, zero
  data-privacy risk (WHA site layouts never leave the machine).
- `QwenImageEditPlusPipeline` natively accepts multiple input images — lets
  us pass all 7 few-shot references + the topo as a unified multi-image prompt.
  This is architecturally cleaner than the old HF Inference approach.
- Qwen-Image-Edit-2511 is a 20B MMDiT model (not a 7B upscaler) — it has
  real understanding of image composition, boundaries, and spatial fill.
- BF16 CUDA inference uses ~20 GB VRAM (A100/RTX3090 territory). CPU fallback
  works but takes 20–40 min per image.
- Demo fallback (`lora/2 copy.png`) keeps the app runnable without GPU.

**BAD / RISK:**
- **MAJOR**: The model was not fine-tuned on industrial master plans. It has no
  built-in concept of "plot codes J11/J12", "WWTP with grey hatch", or
  "retention pond blue diagonal hatch". The few-shot prompting approach battles
  the model's photorealistic training distribution.
- **MAJOR**: Boundary conformance is the hardest task. The pink boundary
  preprocessor helps signal the edge, but a diffusion model working in pixel
  space will still struggle to clip plotlands at exactly the right diagonal angle.
  The model is optimised for semantic edits (change hair colour, add object) —
  not strict polygon tracing.
- Heavy VRAM requirement (20 GB+) is a barrier for most laptops and cloud
  free tiers. Without an A100/RTX4090, the model either OOMs or runs on CPU.
- First run downloads ~16 GB of weights. No fallback if download fails mid-way.
- `num_inference_steps=40` at 20B scale is ~5–15 min on consumer GPU,
  ~20–40 min on CPU. The Streamlit app will appear frozen with no progress bar.

**IMPROVEMENT IDEAS:**
1. **Fine-tune on WHA corpus**: Even a 200-step LoRA on 20–30 completed WHA
   plans would drastically improve style adherence. See `diffusers` LoRA
   training scripts and DiffSynth-Studio (mentioned in QwenLM README, runs
   in 4 GB VRAM via layer-by-layer offload).
2. **ComfyUI + ControlNet**: For strict boundary tracing, `Comfy-Org/ComfyUI`
   (in `third_party/`) with a ControlNet Canny/Scribble condition is technically
   more principled than prompting an image-edit model. ControlNet enforces hard
   pixel-level constraints. This could be Phase 2 v2.
3. **Use LightX2V acceleration** (mentioned in QwenLM README): 25× inference
   speedup via diffusion distillation. Reduces 40-step inference to ~2 steps
   with minimal quality loss. Install from `ModelTC/Qwen-Image-Lightning`.
4. **Add a Streamlit progress bar** that polls the pipeline via a background
   thread — prevents the UI from appearing frozen.
5. **Use FP8 quantisation** (DiffSynth-Engine / DiffSynth-Studio): Cuts VRAM
   requirement from ~20 GB to ~8 GB, enabling RTX3070/4070 execution.

---

### Pre-Processor (_preprocess_topo_for_gen)

**GOOD:**
- Pink boundary detection is robust — handles JPEG artifacts, anti-aliasing,
  sub-pixel grey blending at edges.
- 7×7 kernel × 5 iterations + binary_fill_holes is technically solid for
  closing small gaps in DWG-exported boundary lines.
- 35 px bold pink wall is extremely prominent for the generator to read.
- Blue→grey road neutralisation prevents the model from re-styling external
  road reference lines.

**BAD:**
- Hard-coded colour thresholds `(r - g) > 40`, `(b - g) > 15` only work for
  WHA's cerise/magenta boundary colour. If a client uses a different CAD colour,
  the preprocessor silently produces wrong output.
- The cream fill (`[252, 250, 242]`) is a good interior signal but any dots,
  text, or notations inside the boundary are also blanked — useful context
  (existing buildings, infrastructure) is lost.

**IMPROVEMENT IDEAS:**
1. Make the pink thresholds configurable in `config.py` or auto-detect the
   dominant "thin-line bright colour" in the uploaded DWG.
2. Preserve a light greyscale version of internal annotations instead of
   completely blanking them — gives the model more spatial context.

---

## Tool Ecosystem — Role of Each Third-Party Repo

| Repo | Role in This Project | Status |
|------|---------------------|--------|
| `QwenLM/Qwen-Image` | **Primary** — provides model cards, quick-start code, LoRA training guides, prompt engineering examples. Read the `src/examples/` folder. | Used as reference |
| `huggingface/diffusers` | **Core dependency** — `QwenImageEditPlusPipeline` lives here. Also has LoRA training scripts (`examples/research_projects/`). Required to stay on git HEAD for Qwen support. | Direct dependency |
| `Comfy-Org/ComfyUI` | **Alternative Phase 2 backend** — node-based workflow with Qwen-Image native support (announced Aug 2025). Better for ControlNet boundary enforcement. Higher setup complexity. | Future option |
| `mudler/LocalAI` | **Alternative API server** — if you want an OpenAI-compatible local endpoint for Phase 1 (run Qwen2.5-VL via llama.cpp locally). Not needed for Phase 2 (diffusers is simpler). | Future option |

---

## Honest Overall Assessment

```
                CURRENT ARCHITECTURE
╔═══════════════════════════════════════╗
║  Phase 1 Cloud (OpenRouter)  ██████░░ ║  7/10  solid, free-tier risk
║  Phase 2 Local (diffusers)   ████░░░░ ║  4/10  works, GPU barrier
║  Preprocessor                 ███████░ ║  8/10  best part of the system
║  UI (Streamlit)               ██████░░ ║  7/10  clean, add progress bar
║  Boundary conformance         ████░░░░ ║  3/10  hard unsolved problem
╚═══════════════════════════════════════╝
```

**What makes this POC impressive:**
- Zero external infrastructure — single `streamlit run` command
- The colour-coded few-shot reference system is a real insight
- The preprocessor's pink boundary approach is creative and technically valid
- End-to-end pipeline in <500 lines of clean Python

**What prevents production use:**
1. Boundary conformance — the biggest gap. A diffusion model cannot reliably
   trace an irregular polygon with precision. Even with preprocessing, you will
   get plots that overflow the boundary. Solution: ControlNet (ComfyUI) or
   constraint-inpainting post-processing.
2. Style consistency — without LoRA fine-tuning on WHA drawings, every run
   looks different. The model has to "guess" what WHA style means from 7 images.
3. VRAM requirement — 20 GB eliminates most hardware. Fine-tuning + FP8
   quantisation (DiffSynth-Studio) is the right path.
4. No spatial feedback loop — Phase 1 analysis is text-only. The generator
   cannot "see" where the entry point is unless it's visually marked on the topo.

---

## Recommended Next Steps (priority order)

1. **Add VRAM estimation on startup** — check `torch.cuda.get_device_properties()`
   and warn if VRAM < 20 GB before trying to load the pipeline.
2. **Mark Phase 1 findings on the topo image** — draw entry arrow + basin
   circles on the preprocessed topo so Phase 2 sees spatial context directly.
3. **Add inference progress callback** — `pipeline.set_progress_bar_config()`
   or a custom `callback_on_step_end` to emit Streamlit progress bar updates.
4. **LoRA fine-tune on existing WHA drawings** — 20–30 completed plans,
   100–200 training steps. Use DiffSynth-Studio for 4 GB VRAM compatibility.
5. **Evaluate ComfyUI + Qwen-Image workflow** — specifically for boundary
   enforcement via ControlNet Canny conditioning on the pink boundary image.
6. **Install LightX2V acceleration** — reduces generation time from ~15 min
   to ~2 min on RTX3090 with minimal quality loss.
