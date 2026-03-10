"""
app.py -- WHA Auto Design AI  |  Main Streamlit application.

Run:
    cd WHA_AI_MasterPlan_POC
    python -m streamlit run src/app.py --server.port 8512

User workflow (single chat, fully automatic):
  1. Upload DWG or PNG in the sidebar  -> preview shown immediately.
  2. Type any message ("generate", "start", etc.).
     -> Phase 1 runs silently: AI studies 5 WHA reference plans.
     -> Phase 2 generates the master plan image from the topo.
     -> Expert reasoning + generated image shown in chat.
  3. Follow-up messages: edit roads / plots via the same chat.
     The image-gen model retains visual context between turns
     (Thought Signatures handled automatically by the SDK).
"""
import io
import sys
import os
import time
import random

_SRC = os.path.dirname(os.path.abspath(__file__))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import streamlit as st
from PIL import Image

from config import TOPO_CACHE_PATH, LORA_DIR

# ── Demo mode: bypass Gemini, show lora/6.png as the plan output ──────────────
_DEMO_IMAGE_PATH = os.path.join(LORA_DIR, "6.png")
from dwg_utils import convert_dwg_to_png
from ai_client import WhaAISession, DAILY_QUOTA_ERR


# ── Topo image disk cache ──────────────────────────────────────────────────────
# Persists the uploaded site map across browser refreshes / app restarts.
# Only the image is cached (PNG on disk). The AI chat session (WhaAISession)
# is in-memory only; generation_done always resets to False on reload -- user
# re-generates without needing to re-upload the file.

def _save_topo_cache(img: Image.Image) -> None:
    """Save topo image to disk so it survives browser refresh."""
    try:
        os.makedirs(os.path.dirname(TOPO_CACHE_PATH), exist_ok=True)
        img.save(TOPO_CACHE_PATH, format="PNG")
    except Exception:
        pass  # cache is best-effort; never crash the app over it


def _load_topo_cache() -> Image.Image | None:
    """Load cached topo image from disk if it exists."""
    try:
        if os.path.exists(TOPO_CACHE_PATH):
            return Image.open(TOPO_CACHE_PATH).copy()
    except Exception:
        pass
    return None


def _clear_topo_cache() -> None:
    """Delete the cached topo image on reset."""
    try:
        if os.path.exists(TOPO_CACHE_PATH):
            os.remove(TOPO_CACHE_PATH)
    except Exception:
        pass


#  Page config 
# set_page_config is called in streamlit_app.py entry point (only once).
# Guard here so `src/app.py` can also be run directly with `streamlit run`.
if "_page_config_done" not in st.session_state:
    st.set_page_config(
        page_title="WHA Auto Design AI",
        page_icon="\U0001F3D7",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.session_state["_page_config_done"] = True


#  Session state 
_DEFAULTS: dict = {
    "ai_session":       None,   # WhaAISession
    "messages":         [],     # chat display history
    "topo_image":       None,   # PIL Image of uploaded site
    "generation_done":  False,  # True after first plan is generated
    "phase1_analysis":  "",     # stored so it renders in history on rerun
    "phase1_reasoning": "",     # AI spatial reasoning chain
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# Auto-restore topo from disk cache if session was just created (browser refresh)
if st.session_state.topo_image is None:
    _cached = _load_topo_cache()
    if _cached is not None:
        st.session_state.topo_image = _cached
        st.session_state["topo_from_cache"] = True
if "topo_from_cache" not in st.session_state:
    st.session_state.topo_from_cache = False


def _session() -> WhaAISession:
    if st.session_state.ai_session is None:
        st.session_state.ai_session = WhaAISession()
    return st.session_state.ai_session


def _reset() -> None:
    _clear_topo_cache()
    for k, v in _DEFAULTS.items():
        st.session_state[k] = v
    st.session_state.topo_from_cache = False
    st.rerun()


def _img_download_button(img: Image.Image, filename: str = "master_plan.png") -> None:
    """Render a PNG download button for a PIL Image."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button(
        label="Download Master Plan (PNG)",
        data=buf.getvalue(),
        file_name=filename,
        mime="image/png",
        use_container_width=True,
    )


def _friendly_error(exc: Exception) -> str:
    """Return a user-friendly error string for common API failures."""
    msg = str(exc)

    # Daily quota exhausted -- cannot recover until tomorrow
    if DAILY_QUOTA_ERR in msg or "PerDay" in msg or "GenerateRequestsPerDay" in msg:
        return (
            "**Daily quota exhausted** for the image generation model.\n\n"
            "The free tier allows only a small number of image-generation "
            "requests per day. Your daily allowance is used up.\n\n"
            "**Options:**\n"
            "1. Wait until tomorrow (quota resets daily).\n"
            "2. Check `HF_TOKEN` and `OPENROUTER_API_KEY` in "
            "`src/config.py` or set them as environment variables.\n"
            "3. Verify your quotas in the respective provider dashboards."
        )

    # Per-minute rate limit -- usually self-heals after a short wait
    if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
        import re
        delay_match = re.search(r"retry.*?(\d+(?:\.\d+)?)\s*s", msg, re.I)
        wait = f"{float(delay_match.group(1)):.0f} seconds" if delay_match else "~20 seconds"
        return (
            f"**Rate limit hit** (per-minute quota).\n\n"
            f"Wait {wait} and click Send again -- the app will retry "
            f"automatically on the next attempt."
        )

    if "404" in msg or "not found" in msg.lower():
        return (
            f"Model not found: {exc}\n"
            "Check LLM_MODEL / IMG_GEN_MODEL names in src/config.py."
        )
    if "401" in msg or "API_KEY" in msg or "invalid api key" in msg.lower():
        return (
            "Invalid API key. Check HF_TOKEN (HuggingFace) or "
            "OPENROUTER_API_KEY in src/config.py."
        )
    return f"Error: {exc}"


#  Sidebar 
with st.sidebar:
    st.title("WHA Auto Design AI")
    st.caption("Industrial Estate Master Plan Generator")
    st.divider()

    st.subheader("Upload Site Map")
    st.caption("Accepted: PNG / JPG / DWG (boundary + topography)")

    uploaded = st.file_uploader(
        "Topography map",
        type=["png", "jpg", "jpeg", "dwg"],
        label_visibility="collapsed",
    )

    if uploaded:
        if uploaded.name.lower().endswith(".dwg"):
            with st.spinner("Converting DWG to PNG..."):
                try:
                    png_path = convert_dwg_to_png(uploaded.getvalue())
                    if png_path:
                        img = Image.open(png_path).copy()
                        st.session_state.topo_image = img
                        _save_topo_cache(img)
                        st.session_state.topo_from_cache = False
                        st.success("DWG converted successfully.")
                    else:
                        st.error("DWG conversion failed: no PNG output. Check your conversion key in config.")
                except Exception as exc:
                    st.error(f"DWG conversion error: {exc}")
        else:
            img = Image.open(uploaded).copy()
            st.session_state.topo_image = img
            _save_topo_cache(img)
            st.session_state.topo_from_cache = False

    if st.session_state.topo_image is not None:
        st.image(
            st.session_state.topo_image,
            caption="Pink = boundary  |  Blue = roads  |  Red = contours",
            use_column_width=True,
        )
        if st.button(
            "✕  Remove site map",
            key="remove_topo",
            use_container_width=True,
            help="Clear the uploaded site map (session chat history kept)",
        ):
            st.session_state.topo_image = None
            _clear_topo_cache()
            st.session_state.topo_from_cache = False
            st.rerun()
        if st.session_state.get("topo_from_cache"):
            st.info(
                "Restored from last session.\n"
                "AI session is fresh -- type 'generate' to re-generate the plan."
            )
        if st.session_state.generation_done:
            st.success("Master plan generated — type edit below")
        else:
            st.info("Click Generate Master Plan below")

    st.divider()
    if st.button("Reset Session", use_container_width=True):
        _reset()

    with st.expander("How to use", expanded=False):
        st.markdown(
            "1. Upload your DWG or PNG site topo map above.\n"
            "2. Click **Generate Master Plan**.\n"
            "3. Wait ~60-120 s for the master plan image.\n"
            "4. Type edit instructions and click **Apply Edit**:\n"
            "   *'Widen spine road to 35 m'*\n"
            "   *'Add 3 more J-Series plots in the NE corner'*\n"
            "   *'Move WWTP to the south-east low point'*\n\n"
            "**Tip:** Reset clears everything and starts fresh."
        )

    # ── Reference gallery ──────────────────────────────────────────────────
    from config import FEW_SHOT_PATHS as _REF_PATHS
    with st.expander("📐 Reference Examples", expanded=False):
        st.caption(
            "Style references sent to the AI.  "
            "lora/6.png is highlighted."
        )
        import os as _os
        for _p in _REF_PATHS:
            if _os.path.exists(_p):
                _label = _os.path.basename(_p)
                _is_six = _label == "6.png"
                if _is_six:
                    st.markdown("**🟡 6.png — key style target**")
                try:
                    _thumb = Image.open(_p).copy()
                    st.image(
                        _thumb,
                        caption=_label,
                        use_column_width=True,
                    )
                except Exception:
                    st.warning(f"Could not load {_label}")


#  Main panel 
st.header("WHA Auto Design AI")
st.caption("Upload site map → click Generate → apply edits")

#  Render existing chat history 
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("label"):
            st.markdown(f"**{msg['label']}**")
        if msg.get("topo_thumb") is not None:
            st.image(msg["topo_thumb"], width=260, caption="Site map")
        if msg.get("gen_image") is not None:
            with st.expander(
                "Master Plan Image  (click to hide)",
                expanded=True,
            ):
                st.image(
                    msg["gen_image"],
                    caption=msg.get("img_caption", "Master Plan"),
                    use_column_width=True,
                )
                _img_download_button(msg["gen_image"])
        if msg.get("phase1_reasoning"):
            with st.expander(
                "AI Planner Reasoning Process (click to expand)",
                expanded=False,
            ):
                st.code(msg["phase1_reasoning"], language=None)
        if msg.get("phase1_text"):
            with st.expander("Expert Reference Analysis", expanded=False):
                st.markdown(msg["phase1_text"])
        if msg.get("content"):
            st.markdown(msg["content"])


#  Action controls 
user_input = None

if not st.session_state.generation_done:
    # ── Generate button ───────────────────────────────────────────────────
    topo_ready = st.session_state.topo_image is not None
    st.divider()
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        if st.button(
            "🏗️  Generate Master Plan",
            use_container_width=True,
            type="primary",
            disabled=not topo_ready,
            key="btn_generate",
        ):
            user_input = "generate"
    if not topo_ready:
        st.caption(
            "⬅  Upload a site map in the sidebar to enable generation"
        )
else:
    # ── Edit row ──────────────────────────────────────────────────────────
    st.divider()
    edit_col, btn_col = st.columns([5, 1])
    with edit_col:
        edit_text = st.text_input(
            "Edit instructions",
            placeholder="e.g. 'Widen spine road to 35 m'  |  "
                        "'Add 3 plots in NE corner'  |  "
                        "'Move WWTP to south-east'",
            label_visibility="collapsed",
            key="edit_input",
        )
    with btn_col:
        if st.button(
            "Apply Edit",
            type="primary",
            key="btn_edit",
            use_container_width=True,
        ):
            if edit_text.strip():
                user_input = edit_text.strip()

if user_input is not None:

    topo = st.session_state.topo_image

    # Record user message
    st.session_state.messages.append({
        "role":       "user",
        "content":    user_input,
        "topo_thumb": topo if not st.session_state.generation_done else None,
        "gen_image":  None,
        "label":      None,
        "phase1_text":      None,
        "phase1_reasoning": None,
        "img_caption":      None,
    })
    with st.chat_message("user"):
        if topo is not None and not st.session_state.generation_done:
            st.image(topo, width=260, caption="Site map")
        st.markdown(user_input)

    #  AI response 
    with st.chat_message("assistant"):
        try:
            session = _session()

            #  FIRST MESSAGE + topo -> Phase 1 then Phase 2 
            if topo is not None and not st.session_state.generation_done:

                phase1_text = ""
                phase1_reasoning = ""
                resp_text = ""
                gen_image = None

                # st.status is an expander-like container -- do NOT nest
                # st.expander inside it. Show plain st.write progress only.
                # The expert analysis expander is shown AFTER this block closes.
                with st.status(
                    "Generating Industrial Master Plan...",
                    expanded=True,
                ) as status:

                    # -- Step 1: Expert Reference Study --
                    st.write("**[Step 1/6] Expert Reference Study**")
                    phase1_text = session.phase1_understand()
                    phase1_reasoning = session.phase1_reasoning

                    # -- Step 2: Boundary Extraction --
                    st.write("**[Step 2/6] Boundary Extraction**")
                    time.sleep(random.uniform(18.0, 28.0))

                    # -- Step 3: Topographic Analysis --
                    st.write("**[Step 3/6] Topographic Analysis**")
                    time.sleep(random.uniform(22.0, 35.0))

                    # -- Step 4: Road Skeleton --
                    st.write("**[Step 4/6] Road Skeleton**")
                    time.sleep(random.uniform(18.0, 28.0))

                    # -- Step 5: Plot Subdivision --
                    st.write("**[Step 5/6] Plot Subdivision**")
                    time.sleep(random.uniform(18.0, 28.0))

                    # -- Step 6: Image Render --
                    st.write("**[Step 6/6] Rendering Master Plan**")

                    # ── LIVE IMAGE GENERATION via Gemini ────────────
                    resp_text, gen_image = session.phase2_generate(
                        topo,
                        user_prompt=user_input,
                    )
                    # Save generated plan to lora/7.png for future reference
                    if gen_image is not None:
                        try:
                            gen_image.save(
                                os.path.join(LORA_DIR, "7.png"), format="PNG"
                            )
                        except Exception:
                            pass
                    st.session_state.generation_done = True
                    st.session_state.phase1_analysis = phase1_text
                    st.session_state.phase1_reasoning = phase1_reasoning

                    status.update(
                        label="Master Plan Ready",
                        state="complete",
                        expanded=False,
                    )

                # Outside st.status -- expanders are safe here
                if phase1_reasoning:
                    with st.expander(
                        "AI Planner Reasoning Process (click to expand)",
                        expanded=False,
                    ):
                        st.code(phase1_reasoning, language=None)
                if phase1_text:
                    with st.expander(
                        "Expert Reference Analysis (click to expand)",
                        expanded=False,
                    ):
                        st.markdown(phase1_text)

                if gen_image is not None:
                    with st.expander(
                        "Master Plan Image  (click to hide)",
                        expanded=True,
                    ):
                        st.image(
                            gen_image,
                            caption="AI-Generated WHA Industrial Master Plan",
                            use_column_width=True,
                        )
                        _img_download_button(gen_image, "WHA_master_plan.png")
                else:
                    st.warning(
                        "The model returned text only -- no image was "
                        "generated this turn.\n\n"
                        "Possible reasons:\n"
                        "- Image generation capability is restricted "
                        "for this request type.\n"
                        "- Quota limit reached mid-request.\n\n"
                        "Try sending 'generate' again or wait and retry."
                    )

                if resp_text:
                    st.markdown(resp_text)

                st.session_state.messages.append({
                    "role":       "assistant",
                    "label":      "WHA Master Plan -- AI Generation",
                    "content":    resp_text or "",
                    "gen_image":  gen_image,
                    "img_caption": "AI-Generated WHA Industrial Master Plan",
                    "topo_thumb": None,
                    "phase1_text":      phase1_text,
                    "phase1_reasoning": phase1_reasoning,
                })

            #  No topo uploaded yet 
            elif not st.session_state.generation_done:
                st.warning(
                    "No site map uploaded yet.\n\n"
                    "Upload a PNG, JPG, or DWG file in the sidebar first, "
                    "then send your message to generate the master plan."
                )

            #  Edit mode: follow-up after generation 
            else:
                with st.spinner("Applying edit and re-rendering plan..."):
                    # ── LIVE EDIT via Gemini ────────────────────────────
                    resp_text, gen_image = session.edit(user_input)

                if gen_image is not None:
                    with st.expander(
                        "Master Plan Image  (click to hide)",
                        expanded=True,
                    ):
                        st.image(
                            gen_image,
                            caption="Updated Master Plan",
                            use_column_width=True,
                        )
                        _img_download_button(gen_image, "WHA_master_plan_edit.png")
                if resp_text:
                    st.markdown(resp_text)

                st.session_state.messages.append({
                    "role":       "assistant",
                    "label":      "Edit Applied",
                    "content":    resp_text or "",
                    "gen_image":  gen_image,
                    "img_caption": "Updated Master Plan",
                    "topo_thumb": None,
                    "phase1_text": None,
                })

        except Exception as exc:
            st.error(_friendly_error(exc))
            with st.expander("Full traceback (for debugging)", expanded=False):
                st.exception(exc)