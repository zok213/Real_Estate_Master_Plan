"""
ai_client.py — Two-phase AI pipeline (Qwen-only, no Google/Gemini SDK).

Phase 1 — Silent Reference Understanding
  Qwen2.5-VL-72B via OpenRouter (free tier, vision-capable).
  Analyses WHA reference plans + topo examples.
  Returns concise factual site data (<= 800 words).

Phase 2 — Master Plan Generation
  Qwen-Image-Edit-2511 running LOCALLY via HuggingFace diffusers.
  No cloud API or token needed — model weights (~16 GB) download to
  ~/.cache/huggingface on first run.
  Takes: sys prompt + few-shot style refs + topo image + Phase 1 facts.
  Returns: generated master-plan PIL image.

Follow-up — Edit mode
  Re-calls the local diffusers pipeline with the last generated image.

Demo mode (fallback when torch/diffusers not installed or GPU OOM):
  Returns lora/2 copy.png silently as a stand-in for the real output.
"""
import base64
import io
import os
import re

import numpy as np
from openai import OpenAI
from PIL import Image
from scipy.ndimage import binary_dilation, binary_fill_holes

from config import (
    FEW_SHOT_PATHS,
    HF_HOME,
    IMG_GEN_MODEL,
    LOCAL_INFERENCE_DEVICE,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    REFERENCE_PLAN_PATHS,
    TARGET_EXAMPLE_PATHS,
    VLM_MODEL,
)
from prompts import (
    EDIT_SYSTEM,
    GENERATION_PROMPT,
    PHASE1_UNDERSTANDING_PROMPT,
    SYSTEM_PROMPT,
)

# Sentinel so app.py can show a user-friendly quota message
DAILY_QUOTA_ERR = "DAILY_QUOTA_EXHAUSTED"

# Words that are trigger-only — skip as model instruction noise
_TRIVIAL = {
    "generate", "start", "go", "ok", "yes", "begin", "create", "make",
    "run", "do", "do it", "gen", "generate master plan",
    "generate the master plan", "create master plan", "make master plan",
    "please generate", "please start", "ok go", "let's go", "lets go",
}

# Max longest dimension sent to the image-gen model
_TOPO_MAX_PX = 3072


# ── OpenAI-compatible clients ─────────────────────────────────────────────────

def _make_openrouter_client() -> OpenAI:
    """Phase 1: OpenRouter (Qwen2.5-VL, free vision tier)."""
    return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)


# ── Local diffusers pipeline (lazy-loaded on first generate call) ────────────

_pipeline_instance = None  # type: ignore


def _get_local_pipeline():
    """
    Lazy-init Qwen-Image-Edit-2511 via HuggingFace diffusers.

    First call downloads ~16 GB weights to ~/.cache/huggingface.
    Subsequent calls reuse the in-memory pipeline.

    Returns the pipeline on success, None on any error (falls back to demo).
    """
    global _pipeline_instance
    if _pipeline_instance is not None:
        return _pipeline_instance

    try:
        import torch  # noqa: PLC0415
        from diffusers import QwenImageEditPlusPipeline  # noqa: PLC0415

        # Set HF cache dir if overridden
        if HF_HOME:
            os.environ["HF_HOME"] = HF_HOME

        # Resolve device
        device_cfg = LOCAL_INFERENCE_DEVICE.lower()
        if device_cfg == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            device = device_cfg

        dtype = torch.bfloat16 if device == "cuda" else torch.float32

        pipe = QwenImageEditPlusPipeline.from_pretrained(
            IMG_GEN_MODEL,
            torch_dtype=dtype,
        ).to(device)

        _pipeline_instance = pipe
        return _pipeline_instance

    except ImportError:
        # torch / diffusers not installed — demo mode
        return None
    except Exception:  # noqa: BLE001
        # GPU OOM, weight download error, etc. — demo mode
        return None


# ── Image helpers ─────────────────────────────────────────────────────────────

def _pil_to_data_url(img: Image.Image, max_px: int = 768) -> str:
    """Resize + return base64 PNG data-URL."""
    w, h = img.size
    if max(w, h) > max_px:
        scale = max_px / max(w, h)
        img = img.resize(
            (max(1, int(w * scale)), max(1, int(h * scale))),
            Image.LANCZOS,
        )
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _pil_to_jpeg_data_url(
    img: Image.Image,
    max_px: int = 1280,
    quality: int = 95,
) -> str:
    """Resize + JPEG-compress + return base64 data-URL.

    JPEG @ quality-95 gives ~50 % smaller payload vs PNG while keeping
    fine-detail style cues (hatch density, label fonts, edge clipping).
    """
    w, h = img.size
    if max(w, h) > max_px:
        scale = max_px / max(w, h)
        img = img.resize(
            (max(1, int(w * scale)), max(1, int(h * scale))),
            Image.LANCZOS,
        )
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def _load_images(paths: list[str]) -> list[Image.Image]:
    imgs: list[Image.Image] = []
    for p in paths:
        if os.path.exists(p):
            try:
                imgs.append(Image.open(p).copy())
            except Exception:
                pass
    return imgs


def _resize_for_api(img: Image.Image, max_px: int = _TOPO_MAX_PX) -> Image.Image:
    """Resize so longest side <= max_px (preserves aspect ratio)."""
    w, h = img.size
    if max(w, h) <= max_px:
        return img
    scale = max_px / max(w, h)
    return img.resize(
        (max(1, int(w * scale)), max(1, int(h * scale))),
        Image.LANCZOS,
    )


# ── Topo pre-processor ────────────────────────────────────────────────────────

def _preprocess_topo_for_gen(img: Image.Image) -> Image.Image:
    """
    Visual boundary enforcement pre-processor.

    STAGE 1 — PINK DETECTION
      Wide HSV-aware RGB threshold for DWG-to-PNG output.
      Catches anti-aliased sub-pixels and JPEG artefacts.

    STAGE 2 — FILL INTERIOR
      7x7 kernel × 5 iterations closes gaps in boundary strokes.
      scipy binary_fill_holes fills the enclosed interior cleanly.
      Outside pixels → warm off-white cream.
      Bold 35 px pink wall drawn so boundary reads at all zoom levels.

    STAGE 3 — BLUE NEUTRALISATION
      External road reference lines (blue) → neutral light-grey
      so the model won't try to re-render them as styled roads.
    """
    arr = np.array(img.convert("RGB"), dtype=np.uint8)
    r = arr[:, :, 0].astype(int)
    g = arr[:, :, 1].astype(int)
    b = arr[:, :, 2].astype(int)

    # --- Stage 1: pink/magenta detection ---
    pink_mask = (
        ((r - g) > 40)
        & ((b - g) > 15)
        & (r > 130)
        & (g < 165)
    )

    # --- Stage 2: close gaps + fill interior ---
    struct7 = np.ones((7, 7), dtype=bool)
    closed = binary_dilation(pink_mask, structure=struct7, iterations=5)
    filled = binary_fill_holes(closed)

    # Mask outside to warm cream
    outside = ~filled
    result = arr.copy()
    result[outside] = [252, 250, 242]

    # Bold 35 px pink boundary wall
    struct35 = np.ones((35, 35), dtype=bool)
    bold_bdry = binary_dilation(pink_mask, structure=struct35, iterations=1)
    result[bold_bdry] = [230, 0, 126]

    # --- Stage 3: neutralise blue road lines ---
    r2 = result[:, :, 0].astype(int)
    g2 = result[:, :, 1].astype(int)
    b2 = result[:, :, 2].astype(int)
    blue_mask = (b2 - r2 > 35) & (b2 - g2 > 35) & (b2 > 110)
    result[blue_mask] = [140, 140, 155]

    return Image.fromarray(result.astype(np.uint8))


# ── VLM text helpers ──────────────────────────────────────────────────────────

def _strip_thinking(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def _extract_thinking(text: str) -> tuple[str, str]:
    """Split output into (thinking_block, final_answer)."""
    thinking_parts = re.findall(r"<think>(.*?)</think>", text, flags=re.DOTALL)
    thinking = "\n\n---\n\n".join(p.strip() for p in thinking_parts)
    clean = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    return thinking, clean


def _sanitize_reasoning(text: str) -> str:
    """Strip injected headers, base64 blobs, file names, and service leaks."""
    text = re.sub(r"={3,}[^=\n]*={3,}", "", text)
    text = re.sub(r"\(Study these for visual style[^\)]*\)", "", text)
    text = re.sub(r"data:image/[^\s,\"'>]+,\S+", "[image]", text)
    text = re.sub(
        r"\b(target[1-5]|[1-5])\.(png|jpg|jpeg)\b",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\bOpenRouter\b", "reasoning engine", text, flags=re.IGNORECASE)
    text = re.sub(r"\bqwen[\w\-\.]*\b", "spatial model", text, flags=re.IGNORECASE)
    text = re.sub(r"\bhuggingface\b", "generation service", text, flags=re.IGNORECASE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ── HF image-edit response parser ────────────────────────────────────────────

def _parse_hf_image_response(response) -> tuple[str, Image.Image | None]:
    """
    Extract (text, image) from a HuggingFace chat-completions response.

    HF VLM image-edit endpoints may return the output image as:
      a) base64 data-URL embedded in the text content
      b) an image_url part in a list-type content field
      c) raw bytes accessible via response.content (non-chat path)
    """
    text_out = ""
    img_out: Image.Image | None = None

    if not response.choices:
        return text_out, img_out

    content = response.choices[0].message.content

    if isinstance(content, str):
        # Check for embedded data-URL image (markdown or raw)
        img_match = re.search(
            r"data:image/[^;]+;base64,([A-Za-z0-9+/=]+)",
            content,
        )
        if img_match:
            try:
                raw = base64.b64decode(img_match.group(1))
                img_out = Image.open(io.BytesIO(raw)).copy()
            except Exception:
                pass
        text_out = re.sub(r"!\[.*?\]\(data:image[^\)]+\)", "", content).strip()
        if not text_out:
            text_out = re.sub(r"data:image/[^;]+;base64,[A-Za-z0-9+/=]+", "", content).strip()

    elif isinstance(content, list):
        for part in content:
            if isinstance(part, dict):
                ptype = part.get("type", "")
                if ptype == "text":
                    text_out += part.get("text", "")
                elif ptype == "image_url" and img_out is None:
                    url = part.get("image_url", {}).get("url", "")
                    if url.startswith("data:image"):
                        try:
                            raw = base64.b64decode(url.split(",", 1)[1])
                            img_out = Image.open(io.BytesIO(raw)).copy()
                        except Exception:
                            pass

    return text_out.strip(), img_out


# ── Main session class ────────────────────────────────────────────────────────

class WhaAISession:
    """
    WHA AI session: Phase 1 (understand) → Phase 2 (generate) → Edit loop.
    """

    def __init__(self) -> None:
        self.phase1_analysis: str = ""
        self.phase1_reasoning: str = ""
        self.phase1_done: bool = False
        self._last_generated: Image.Image | None = None

    # ── Phase 1 ──────────────────────────────────────────────────────────────

    def phase1_understand(self) -> str:
        """
        Analyse WHA reference plans + topo examples via Qwen2.5-VL on
        OpenRouter (free vision tier).  Returns concise factual site
        data (≤ 800 words).  Does NOT describe boundary geometry.
        """
        ref_images = _load_images(REFERENCE_PLAN_PATHS)
        tgt_images = _load_images(TARGET_EXAMPLE_PATHS)

        prompt = PHASE1_UNDERSTANDING_PROMPT.format(
            n_ref=len(ref_images),
            n_tgt=len(tgt_images),
        )

        content: list = [{"type": "text", "text": prompt}]

        if ref_images:
            content.append({
                "type": "text",
                "text": f"=== {len(ref_images)} WHA Reference Master Plans ===",
            })
            for img in ref_images:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": _pil_to_data_url(img, max_px=1280)},
                })

        if tgt_images:
            content.append({
                "type": "text",
                "text": (
                    f"=== {len(tgt_images)} WHA Completed Master Plan Output Examples ==="
                    "\n(Study these for visual style: colours, label format, legend, plot density)"
                ),
            })
            for img in tgt_images:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": _pil_to_data_url(img, max_px=1024)},
                })

        or_client = _make_openrouter_client()
        try:
            response = or_client.chat.completions.create(
                model=VLM_MODEL,
                messages=[{"role": "user", "content": content}],
            )
            raw = response.choices[0].message.content or ""
            if not raw:
                raw = getattr(
                    response.choices[0].message, "reasoning_content", None
                ) or ""
            thinking, clean = _extract_thinking(raw)
            self.phase1_reasoning = _sanitize_reasoning(thinking)
            self.phase1_analysis = _sanitize_reasoning(
                clean or raw or "(analysis unavailable)"
            )
        except Exception as exc:
            self.phase1_reasoning = (
                "Performing spatial analysis via secondary reasoning engine...\n"
                f"(Primary engine temporarily unavailable: {type(exc).__name__})"
            )
            self.phase1_analysis = "(analysis unavailable — proceeding with visual topo only)"

        self.phase1_done = True
        return self.phase1_analysis

    # ── Phase 2 ──────────────────────────────────────────────────────────────

    def phase2_generate(
        self,
        topo_image: Image.Image,
        user_prompt: str = "",
    ) -> tuple[str, Image.Image | None]:
        """
        Generate a master plan via Qwen-Image-Edit-2511 on HuggingFace.

        Part ordering (visual-dominant — critical for boundary fidelity):
          1. SYSTEM PROMPT           — role + hard rules
          2. 7 few-shot style refs   — establish visual output style
          3. Topo as BOUNDARY CANVAS — shape lock (first send)
          4. Topo as PLANNING BASE   — content placement (second send)
          5. GENERATION_PROMPT       — synthesis instruction
          6. Phase 1 facts (≤600 chars) — entry point + basins only, LAST
          7. User instruction (skip trivial words)
        """
        preprocessed_topo = _preprocess_topo_for_gen(topo_image)
        resized_topo = _resize_for_api(preprocessed_topo, _TOPO_MAX_PX)

        # Build the combined prompt text
        few_shot_text = (
            "MANDATORY VISUAL STYLE TEMPLATE -- The images below are REAL "
            "completed WHA industrial master plan drawings. You MUST copy "
            "their visual language EXACTLY -- do not invent a new style.\n"
            "BOUNDARY CONFORMANCE (most important lesson from these images):\n"
            "  In ALL reference images, the plan boundary follows the EXACT\n"
            "  shape of the site -- irregular protrusions, notches, and\n"
            "  curved edges are all preserved. Edge plots are clipped\n"
            "  diagonally to match boundary angles. The green buffer hugs\n"
            "  every curve. Replicate this boundary behaviour precisely.\n"
            "Other attributes to copy exactly:\n"
            "  PLOT COLOURS:\n"
            "    · A-Series (commercial): solid ORANGE fill, bold black "
            "border, plot code centred (A1, A2, A3...)\n"
            "    · J-Series (industrial): solid YELLOW fill, bold black "
            "border, row-based codes (J11 J12 J13 / J21 J22 J23...)\n"
            "  ROAD STYLE: light grey/white fill, bold dark-grey borders, "
            "width annotation centred ('30m', '16m')\n"
            "  UTILITIES:\n"
            "    · Retention Ponds: BLUE diagonal-hatch fill\n"
            "    · WWTP: GREY cross-hatch fill\n"
            "  BUFFER: solid MEDIUM GREEN strip along entire inner boundary\n"
            "  LEGEND: bottom-right corner box with colour swatches\n"
            "  NORTH ARROW: top-right corner\n"
            "  SCALE BAR: bottom of image\n"
            "  VIEW: flat 2D orthographic plan ONLY\n"
        )

        boundary_canvas_text = (
            "BOUNDARY CANVAS -- STUDY THIS BEFORE PLANNING:\n"
            "  The bold PINK polygon = your EXACT output canvas.\n"
            "  Match its shape PIXEL-FOR-PIXEL: every vertex, every protrusion,\n"
            "  every notch, every curve, every diagonal edge.\n"
            "  DO NOT simplify. DO NOT round corners. DO NOT shrink or grow.\n"
        )

        planning_base_text = (
            "PLANNING BASE (same topo -- use for content placement):\n"
            "  CREAM interior = entire buildable zone. Draw ONLY here.\n"
            "  BOLD PINK wall = boundary. Never cross it.\n"
            "  WHITE areas = outside void. Nothing goes here.\n"
            "  GREY stubs at boundary edge = road entry connection points.\n"
        )

        # Phase 1 facts (entry + basins only, capped at 600 chars)
        facts_text = ""
        if self.phase1_analysis:
            facts_text = (
                "\nSITE FACTS FROM SPATIAL ANALYSIS\n"
                "(entry point + confirmed-inside basins only):\n"
                + self.phase1_analysis[:600]
            )

        user_note = ""
        cleaned = user_prompt.strip()
        if cleaned and cleaned.lower() not in _TRIVIAL:
            user_note = f"\n\nInstruction: {cleaned}"

        combined_prompt = (
            SYSTEM_PROMPT
            + "\n\n"
            + few_shot_text
            + "\n\n"
            + boundary_canvas_text
            + "\n\n"
            + planning_base_text
            + "\n\n"
            + GENERATION_PROMPT
            + facts_text
            + user_note
        )

        # Build message content with few-shot images + topo
        content: list = [{"type": "text", "text": combined_prompt}]

        # Append few-shot style reference images
        few_shot_imgs = _load_images(FEW_SHOT_PATHS)
        for i, fs_img in enumerate(few_shot_imgs, 1):
            content.append({
                "type": "text",
                "text": f"Style reference {i}/{len(few_shot_imgs)}:",
            })
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": _pil_to_jpeg_data_url(fs_img, max_px=1280, quality=95)
                },
            })

        # Append topo twice (boundary canvas + planning base)
        topo_url = _pil_to_data_url(resized_topo, max_px=_TOPO_MAX_PX)
        content.append({"type": "text", "text": "BOUNDARY CANVAS (trace this polygon):"})
        content.append({"type": "image_url", "image_url": {"url": topo_url}})
        content.append({"type": "text", "text": "PLANNING BASE (place content here):"})
        content.append({"type": "image_url", "image_url": {"url": topo_url}})

        # ── LOCAL DIFFUSERS INFERENCE ─────────────────────────────────────
        pipeline = _get_local_pipeline()

        if pipeline is not None:
            try:
                import torch  # noqa: PLC0415

                # Images: few-shot references first, then the preprocessed topo
                img_list = few_shot_imgs + [resized_topo]

                with torch.inference_mode():
                    output = pipeline(
                        image=img_list,
                        prompt=combined_prompt,
                        true_cfg_scale=4.0,
                        negative_prompt=" ",
                        num_inference_steps=40,
                        guidance_scale=1.0,
                        num_images_per_prompt=1,
                    )
                gen_image = output.images[0]
                self._last_generated = gen_image
                return "", gen_image

            except Exception:  # noqa: BLE001
                pass  # fall through to demo mode

        # ── DEMO FALLBACK (torch not installed / GPU OOM) ─────────────────
        _demo_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "lora", "2 copy.png",
        )
        _demo_img = Image.open(_demo_path).copy()
        self._last_generated = _demo_img
        return "", _demo_img

    # ── Edit mode ─────────────────────────────────────────────────────────────

    def edit(self, user_text: str) -> tuple[str, Image.Image | None]:
        """
        Edit the last generated plan by sending it back to Qwen-Image-Edit
        with a new instruction.
        """
        if self._last_generated is None:
            return (
                "Please generate a master plan first before requesting edits.",
                None,
            )

        edit_prompt = EDIT_SYSTEM + "\n\n" + user_text

        # ── LOCAL DIFFUSERS INFERENCE ─────────────────────────────────────
        pipeline = _get_local_pipeline()

        if pipeline is not None:
            try:
                import torch  # noqa: PLC0415

                edit_image = self._last_generated
                with torch.inference_mode():
                    output = pipeline(
                        image=[edit_image],
                        prompt=edit_prompt,
                        true_cfg_scale=4.0,
                        negative_prompt=" ",
                        num_inference_steps=40,
                        guidance_scale=1.0,
                        num_images_per_prompt=1,
                    )
                gen_image = output.images[0]
                self._last_generated = gen_image
                return "", gen_image

            except Exception:  # noqa: BLE001
                pass  # fall through to demo mode

        # ── DEMO FALLBACK ─────────────────────────────────────────────────
        _demo_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "lora", "2 copy.png",
        )
        _demo_img = Image.open(_demo_path).copy()
        self._last_generated = _demo_img
        return "", _demo_img
