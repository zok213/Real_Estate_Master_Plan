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

_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_root, "src"))

# Pre-create writable directories the app needs at runtime.
os.makedirs(os.path.join(_root, "output", "reasoning_logs"), exist_ok=True)

_app_path = os.path.join(_root, "src", "app.py")

try:
    runpy.run_path(_app_path, run_name="__main__")
except Exception as _exc:
    # Surface the real error on-screen instead of silently crashing.
    import streamlit as st
    st.error(f"**App failed to start:** {_exc}")
    st.code(traceback.format_exc(), language="python")
