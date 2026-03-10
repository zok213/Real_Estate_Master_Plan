# WHA Auto Design AI — Hugging Face Spaces Deployment Guide

## Why Docker (not Gradio)

| Factor | Docker ✅ | Gradio ❌ |
|---|---|---|
| UI rewrite needed | None — wraps Streamlit as-is | Full rewrite required |
| Source code hiding | PyArmor obfuscation in build stage | Source always visible |
| HF Spaces support | Official Docker SDK | Native |
| Dependency control | Fully pinned in Dockerfile | Managed by HF |
| Port / runtime | Any port, full control | Managed |

## Source Code Protection — 3 Levels

### Level 1 (Implemented — PyArmor in Docker build)
The Dockerfile's Stage 1 runs PyArmor to encrypt all `.py` files into
unreadable bytecode. Stage 2 (runtime) copies only the encrypted output.
**Result:** The Docker container has no readable Python source.

### Level 2 (Recommended — Private HF Space)
Make the Space private in HF Settings. Source files in the repo are hidden
from everyone except invited collaborators.
**Cost:** HF Pro ($9/month) or HF Enterprise.

### Level 3 (Maximum — Pre-built image from private registry)
Build the Docker image locally, push to a private Docker Hub repo.
HF Space Dockerfile: `FROM your-org/wha-app:latest` — the HF repo has
ONLY one line. Source never leaves your machine.

---

## Step-by-Step Deployment

### Prerequisites
- Hugging Face account: https://huggingface.co
- Git with Git LFS installed (`git lfs install`)
- Docker Desktop (to test locally before pushing)

---

### Step 1: Create the HF Space

1. Go to https://huggingface.co/new-space
2. Settings:
   - **Space name:** `wha-auto-design-ai` (or your preferred name)
   - **License:** Other
   - **SDK:** Docker
   - **Visibility:** Private (recommended for source protection)
3. Click **Create Space**

---

### Step 2: Set API Key Secrets

In your Space → **Settings** → **Variables and secrets** → **New secret**:

| Secret name | Value |
|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key |
| `CONVERTAPI_SECRET` | Your ConvertAPI secret |
| `OPENROUTER_API_KEY` | Your OpenRouter key (optional) |

**Never put API keys in any file that gets committed.**

---

### Step 3: Create a deployment branch

```bash
cd D:\newrealestate\WHA_AI_MasterPlan_POC

# Create and switch to the deployment branch
git checkout -b gemini-hf-deploy

# Verify .env is NOT tracked (should show nothing)
git status --short | findstr ".env"
```

---

### Step 4: Prepare the HF Space README

Rename the template as the root README:

```bash
# Copy the HF Spaces README template to replace the project README
copy hf_spaces_README.md README.md
```

The YAML frontmatter at the top is what HF Spaces reads to configure the Space.

---

### Step 5: Commit deployment files

```bash
# Stage all deployment files (Dockerfile, .streamlit, .dockerignore, etc.)
git add Dockerfile .dockerignore .streamlit/ requirements.txt
git add src/ lora/ expert_reasoning/ constraints.json
git add README.md

# Verify secrets are NOT staged
git status

# Commit
git commit -m "feat: add Docker deployment for HF Spaces"
```

---

### Step 6: Connect and push to HF Spaces

```bash
# Add HF Spaces as a remote (replace YOUR_USERNAME and SPACE_NAME)
git remote add hf-space https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME

# Push the deployment branch to HF Spaces main
git push hf-space gemini-hf-deploy:main
```

HF Spaces will automatically:
1. Detect the `sdk: docker` in README.md
2. Build the Docker image (takes ~5–10 min on first build)
3. Start the container on port 7860
4. Your app is live at: `https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME`

---

### Step 7: Test locally with Docker (before pushing)

```bash
# Build locally to catch any errors before pushing
docker build -t wha-ai-test .

# Run locally with your .env keys
docker run --env-file .env -p 7860:7860 wha-ai-test

# Open: http://localhost:7860
```

---

## File Layout in the HF Space Repo

```
README.md               ← HF YAML frontmatter (sdk:docker, port:7860)
Dockerfile              ← Multi-stage: PyArmor obfuscation + slim runtime
.dockerignore           ← Excludes third_party/, customer docs/, .env, etc.
requirements.txt        ← Python deps (no secrets)
.streamlit/
    config.toml         ← Port 7860, headless, dark theme
src/                    ← Python source (obfuscated inside Docker image)
lora/                   ← Reference plan PNG images (runtime data)
expert_reasoning/       ← Markdown reasoning files (runtime context)
constraints.json        ← IEAT site parameters
```

**NOT in the HF Space repo:**
- `.env` (secrets — set in HF Secrets UI instead)
- `customer docs/` (private customer DWG files)
- `third_party/` (ComfyUI, diffusers, LocalAI — unused in cloud branch)
- `output/` (generated at runtime)
- `docs/`, `tools/`, `tests/` (dev only)

---

## Updating the Deployment

After making code changes:

```bash
git add src/ -p           # stage only what changed
git commit -m "fix: ..."
git push hf-space gemini-hf-deploy:main
```

HF Spaces rebuilds the Docker image automatically on every push.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Build fails: `pyarmor not found` | Check Stage 1 install step in Dockerfile |
| `GEMINI_API_KEY` not set error | Add secret in HF Space Settings |
| Port conflict | Verify `app_port: 7860` in README.md frontmatter |
| Large build context / slow push | Verify `.dockerignore` excludes `third_party/` |
| App crashes on start | Check Space logs → Container logs tab |
| Git LFS quota exceeded | Use `git lfs migrate` or move images to HF Datasets |

---

## Git LFS for `lora/` images

The `lora/` folder contains PNG reference images. If they are large (>50 MB total),
set up Git LFS before pushing:

```bash
git lfs install
git lfs track "lora/*.png"
git add .gitattributes
git commit -m "chore: track lora images in LFS"
```
