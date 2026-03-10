"""
ai_client.py — Two-phase AI pipeline (cloud: OpenRouter + Gemini).

Phase 1 — Silent Reference Understanding
  Qwen3-VL-235B-A22B-Thinking via OpenRouter API.
  Advanced vision-language model with extended reasoning.
  Analyses WHA reference plans + topo examples.
  Returns concise factual site data (<= 800 words).

Phase 2 — Master Plan Generation
  Google Gemini 3.1 Flash Image Preview via google-genai.
  Takes: sys prompt + few-shot refs + topo image + Phase 1 facts.
  Returns: generated master-plan PIL image.

Follow-up — Edit mode
  Re-calls Gemini with the last generated image + new edit instruction.
"""
import base64
import io
import os
import re
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation, binary_fill_holes

from openai import OpenAI
import google.genai as genai
from google.genai import types as genai_types

from config import (
    FEW_SHOT_PATHS,
    GEMINI_API_KEY,
    GEMINI_IMAGE_MODEL,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    PHASE1_ENABLED,
    PHASE2_ENABLED,
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
# Gemini inline image limit is 4 MB — 1600px PNG stays well under that
_TOPO_MAX_PX = 1600


# ── OpenRouter client helper ──────────────────────────────────────────────────


def _make_openrouter_client() -> OpenAI:
    """
    Return an openai.OpenAI client pointed at the OpenRouter endpoint.
    Raises RuntimeError if OPENROUTER_API_KEY is not set.
    """
    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. "
            "Get a free key at https://openrouter.ai and set the env var."
        )
    return OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )


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


# ── VLM text helpers ──────────────────────────────────────────────────────

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


# ── Reasoning log helper ──────────────────────────────────────────────────────

_LOG_DIR = Path(__file__).parent.parent / "output" / "reasoning_logs"


def _save_reasoning_log(reasoning: str, analysis: str) -> None:
    """
    Write Phase 1 Qwen reasoning + analysis to a timestamped .md file in
    output/reasoning_logs/ so the full chain-of-thought can be inspected.
    """
    try:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = _LOG_DIR / f"qwen_reasoning_{ts}.md"
        lines = [
            f"# Qwen Phase-1 Reasoning Log — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "---\n",
            "## Chain-of-Thought / Thinking\n",
            reasoning or "*(no reasoning captured)*",
            "\n\n---\n",
            "## Final Site Analysis\n",
            analysis or "*(no analysis captured)*",
            "\n",
        ]
        log_path.write_text("\n".join(lines), encoding="utf-8")
    except Exception:
        pass  # logging failure must never crash the main pipeline


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
        if not PHASE1_ENABLED:
            self.phase1_reasoning = ""
            self.phase1_analysis = ""
            self.phase1_done = True
            return ""

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
                "text": (
                    f"=== {len(ref_images)} WHA Reference Master Plans ==="
                ),
            })
            for img in ref_images:
                # JPEG at 1024px: ~150-300 KB vs 3+ MB PNG — fewer tokens
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": _pil_to_jpeg_data_url(
                            img, max_px=1024, quality=85
                        )
                    },
                })

        if tgt_images:
            content.append({
                "type": "text",
                "text": (
                    f"=== {len(tgt_images)} WHA Completed Plan Examples ==="
                    "\n(Study for visual style: colours, labels, legend)"
                ),
            })
            for img in tgt_images:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": _pil_to_jpeg_data_url(
                            img, max_px=1024, quality=85
                        )
                    },
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
        _save_reasoning_log(
            self.phase1_reasoning, self.phase1_analysis
        )
        return self.phase1_analysis

    # ── Phase 2 ──────────────────────────────────────────────────────────────

    def phase2_generate(
        self,
        topo_image: Image.Image,
        user_prompt: str = "",
    ) -> tuple[str, Image.Image | None]:
        """
        Generate master plan via Gemini 3.1 Flash Image Preview.

        Part ordering (visual-dominant — critical for boundary fidelity):
          1. SYSTEM_PROMPT           — role + hard rules (as system_instruction)
          2. Few-shot WHA style refs — establish visual output style
          3. Topo (preprocessed)     — boundary canvas + planning base
          4. GENERATION_PROMPT       — synthesis instruction
          5. Phase 1 facts (full) — entry points + basins + constraints, LAST
          6. User instruction (skip trivial words)
        """
        if not PHASE2_ENABLED:
            self.phase2_done = True
            return ("Phase 2 (Gemini) is disabled.", None)

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

        # Phase 1 facts — full analysis, no truncation
        facts_text = ""
        if self.phase1_analysis:
            facts_text = (
                "\nSITE FACTS FROM SPATIAL ANALYSIS\n"
                "(entry points + basins + planning constraints):\n"
                + self.phase1_analysis
            )

        user_note = ""
        cleaned = user_prompt.strip()
        if cleaned and cleaned.lower() not in _TRIVIAL:
            user_note = f"\n\nInstruction: {cleaned}"

        # NOTE: SYSTEM_PROMPT is in system_instruction below — do NOT repeat
        # it here or it will be sent twice, wasting tokens and confusing model.
        combined_prompt = (
            few_shot_text
            + "\n\n"
            + boundary_canvas_text
            + "\n\n"
            + planning_base_text
            + "\n\n"
            + GENERATION_PROMPT
            + facts_text
            + user_note
        )

        # ── GEMINI IMAGE GENERATION ───────────────────────────────────────
        if not GEMINI_API_KEY:
            return ("GEMINI_API_KEY not configured.", None)
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)

        # Part ordering per Google multimodal best practices:
        #   1.  Few-shot style-reference images (visual vocabulary)
        #   2.  Topo boundary image (canvas + planning base)
        #   3.  Instruction text (combined_prompt) — LAST
        # Placing images before text gives Gemini visual context first.
        few_shot_imgs = _load_images(FEW_SHOT_PATHS)
        parts: list = []

        # Few-shot references: cap at 1024 px, JPEG Q85 (~200-400 KB each)
        for fs_img in few_shot_imgs:
            fs_img = _resize_for_api(fs_img, max_px=1024)
            if fs_img.mode not in ("RGB", "L"):
                fs_img = fs_img.convert("RGB")
            fs_buf = io.BytesIO()
            fs_img.save(fs_buf, format="JPEG", quality=85)
            fs_buf.seek(0)
            parts.append(genai_types.Part.from_bytes(
                data=fs_buf.read(), mime_type="image/jpeg",
            ))

        # Topo image (already resized to max 1600 px)
        if resized_topo.mode not in ("RGB", "L"):
            resized_topo = resized_topo.convert("RGB")
        topo_buf = io.BytesIO()
        resized_topo.save(topo_buf, format="PNG")
        topo_buf.seek(0)
        parts.append(genai_types.Part.from_bytes(
            data=topo_buf.read(), mime_type="image/png",
        ))

        # Instruction text LAST (after visual context)
        parts.append(genai_types.Part.from_text(text=combined_prompt))

        try:
            response = gemini_client.models.generate_content(
                model=GEMINI_IMAGE_MODEL,
                contents=genai_types.Content(
                    role="user",
                    parts=parts,
                ),
                config=genai_types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    # TEXT allows Gemini rejection messages to surface
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )
            gen_image = None
            resp_text = ""
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None and gen_image is None:
                    gen_image = Image.open(
                        io.BytesIO(part.inline_data.data)
                    ).copy()
                elif hasattr(part, "text") and part.text:
                    resp_text += part.text
            if gen_image is None:
                reason = resp_text or "No detail returned."
                return (
                    f"Gemini returned no image: {reason[:300]}", None
                )
            self._last_generated = gen_image
            return "", gen_image
        except Exception as exc:
            return (
                f"Gemini error: {type(exc).__name__} — {str(exc)[:300]}",
                None,
            )

    # ── Edit mode ─────────────────────────────────────────────────────────────

    def edit(self, user_text: str) -> tuple[str, Image.Image | None]:
        """
        Edit the last generated plan via Gemini image generation.
        Sends the previously generated image + edit instruction to Gemini.
        """
        if not PHASE2_ENABLED:
            return ("Phase 2 (Gemini) is disabled.", None)

        if self._last_generated is None:
            return (
                "Please generate a master plan first before requesting edits.",
                None,
            )

        edit_prompt = EDIT_SYSTEM + "\n\n" + user_text

        # ── GEMINI IMAGE EDIT ─────────────────────────────────────────────
        if not GEMINI_API_KEY:
            return (
                "GEMINI_API_KEY not set. Get key at https://aistudio.google.com",
                None,
            )
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)

        # Image first, then edit instruction text
        img_buf = io.BytesIO()
        last = self._last_generated
        if last.mode not in ("RGB", "L"):
            last = last.convert("RGB")
        last.save(img_buf, format="PNG")
        img_buf.seek(0)
        parts: list = [
            genai_types.Part.from_bytes(
                data=img_buf.read(), mime_type="image/png",
            ),
            genai_types.Part.from_text(text=edit_prompt),
        ]

        try:
            response = gemini_client.models.generate_content(
                model=GEMINI_IMAGE_MODEL,
                contents=genai_types.Content(
                    role="user",
                    parts=parts,
                ),
                config=genai_types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )
            gen_image = None
            resp_text = ""
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None and gen_image is None:
                    gen_image = Image.open(
                        io.BytesIO(part.inline_data.data)
                    ).copy()
                elif hasattr(part, "text") and part.text:
                    resp_text += part.text
            if gen_image is None:
                reason = resp_text or "No image returned."
                return (
                    f"Gemini edit did not generate an image: {reason}",
                    None,
                )
            self._last_generated = gen_image
            return resp_text, gen_image
        except Exception as exc:
            return (
                f"Gemini edit error: {type(exc).__name__} — {str(exc)[:300]}",
                None,
            )
