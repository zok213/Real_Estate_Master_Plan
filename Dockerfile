# ═══════════════════════════════════════════════════════════════════════════════
#  WHA Auto Design AI — HF Spaces Docker deployment
#  Multi-stage build:
#    Stage 1 (obfuscator): installs PyArmor, compiles + obfuscates all .py src
#    Stage 2 (runtime):    lean image with only obfuscated code + assets
#
#  API keys are NEVER baked in — set as HF Spaces Secrets (env vars):
#    GEMINI_API_KEY, OPENROUTER_API_KEY, CONVERTAPI_SECRET
# ═══════════════════════════════════════════════════════════════════════════════

# ── Stage 1: obfuscate source ─────────────────────────────────────────────────
FROM python:3.11-slim AS obfuscator
WORKDIR /build

# Copy only source files needed for obfuscation
COPY src/ src/

# Install PyArmor (source obfuscation tool)
RUN pip install --no-cache-dir pyarmor==8.5.11

# Obfuscate all Python modules into dist/
# Output: dist/*.py (encrypted) + dist/pyarmor_runtime_*/
RUN pyarmor gen --output dist \
        src/app.py \
        src/ai_client.py \
        src/config.py \
        src/dwg_utils.py \
        src/prompts.py


# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.11-slim
WORKDIR /app

# System libraries required by Pillow / scipy
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies (pinned via requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Obfuscated source (no readable .py files in the final image) ──────────────
COPY --from=obfuscator /build/dist/ src/

# ── Runtime assets ────────────────────────────────────────────────────────────
# Reference master plan images (needed at startup for few-shot prompting)
COPY lora/ lora/

# Expert reasoning markdown files (read at runtime for context)
COPY expert_reasoning/ expert_reasoning/

# Site constraint parameters
COPY constraints.json .

# Streamlit server config (port 7860 for HF Spaces)
COPY .streamlit/ .streamlit/

# Pre-create writable directories the app writes to at runtime
RUN mkdir -p output/reasoning_logs input

# ── Security: run as non-root ─────────────────────────────────────────────────
RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

# HF Spaces standard port
EXPOSE 7860

# ── Entrypoint ────────────────────────────────────────────────────────────────
CMD ["python", "-m", "streamlit", "run", "src/app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.fileWatcherType=none", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false"]
