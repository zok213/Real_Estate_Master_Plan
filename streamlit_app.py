"""
streamlit_app.py — HF Spaces / Streamlit Cloud entry point.

Uses runpy.run_path so src/app.py is re-executed on EVERY Streamlit rerun
(unlike `import app` which is cached after the first run and produces a blank
page on all subsequent reruns).
"""
import sys
import os
import runpy
import traceback
import streamlit as st

_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_root, "src"))

# Pre-create writable directories the app needs at runtime.
os.makedirs(os.path.join(_root, "output", "reasoning_logs"), exist_ok=True)

# set_page_config must be the FIRST Streamlit call and only once per session.
if "_page_config_done" not in st.session_state:
    st.set_page_config(
        page_title="WHA Auto Design AI",
        page_icon="\U0001F3D7",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.session_state["_page_config_done"] = True

_app_path = os.path.join(_root, "src", "app.py")

try:
    runpy.run_path(_app_path, run_name="__main__")
except Exception as _exc:
    # Surface the real error on-screen instead of silently crashing.
    st.error(f"**App failed to start:** {_exc}")
    st.code(traceback.format_exc(), language="python")
