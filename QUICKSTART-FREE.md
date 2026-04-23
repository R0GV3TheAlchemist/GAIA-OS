# ⚡ GAIA Quick Start — Free, No API Keys Required

You can run GAIA completely free using **Ollama** — an app that runs AI models on your own computer. No account. No credit card. No internet required once set up.

---

## What You Need

| Requirement | Version | Download |
|---|---|---|
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org/) |
| Ollama | Latest | [ollama.com](https://ollama.com/) |

> **Just want the Windows app?** Download the installer directly from the [Releases page](https://github.com/R0GV3TheAlchemist/GAIA-APP/releases) — no Python or Node needed.

---

## Step 1 — Install Ollama and Download a Free AI Model

1. Download and install Ollama from [https://ollama.com](https://ollama.com)
2. Open a terminal and run:

```bash
ollama pull gemma3:1b
```

This downloads a small, fast AI model (~800MB). It runs entirely on your machine.

> **Slow internet or old computer?** Use an even smaller model:
> ```bash
> ollama pull phi3:mini
> ```

---

## Step 2 — Set Up GAIA

Open a terminal **inside the GAIA-APP folder**, then run:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies (only needed once)
npm install
```

---

## Step 3 — Create Your .env File

Copy the example config:

```bash
# On Mac/Linux:
cp .env.example .env

# On Windows:
copy .env.example .env
```

The default config already points to Ollama — no editing needed.

### Optional: Add a Paid API Key

If you have an OpenAI, Anthropic, or Perplexity key, open `.env` and uncomment the relevant line:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...

# Perplexity Search
PERPLEXITY_API_KEY=pplx-...
PERPLEXITY_MODEL=sonar-pro
```

GAIA works great without any of these.

---

## Step 4 — Start GAIA

**Start Ollama first** (if it's not already running):
```bash
ollama serve
```

Then, in a **new terminal** in the GAIA-APP folder:

```bash
# Start the backend
python -m core.server
```

And in another **new terminal**:

```bash
# Start the frontend
npm run dev
```

---

## Step 5 — Open GAIA

Open your browser and go to:

```
http://localhost:5173
```

GAIA is running. Talk to her. 🌍

---

## Running as Desktop App (Windows)

If you want to run the native Windows desktop app instead of the browser:

```bash
# Development mode
npm run tauri dev

# Or download the pre-built installer from:
# https://github.com/R0GV3TheAlchemist/GAIA-APP/releases
```

The desktop app bundles the Python backend as a sidecar — no separate terminal needed.

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'core'` | Run `python -m core.server` from the **root GAIA-APP folder** |
| `Connection refused` on port 8008 | Make sure the backend started without errors |
| `ollama: command not found` | Install Ollama from [ollama.com](https://ollama.com) |
| Slow responses | Try `ollama pull phi3:mini` — smaller and faster |
| Port 5173 already in use | Close other dev terminals and try again |
| Desktop app won't launch | Make sure Rust is installed: [rustup.rs](https://rustup.rs/) |

---

## Free Models That Work Great with GAIA

| Model | Size | Good For |
|---|---|---|
| `gemma3:1b` | ~800MB | Fast everyday use, low RAM |
| `phi3:mini` | ~2GB | Smart and small |
| `llama3.2:1b` | ~1.3GB | Great reasoning |
| `mistral` | ~4GB | Best quality on stronger computers |

Change the model anytime by editing `OLLAMA_MODEL=` in your `.env` file.

---

*GAIA is free. Built with love. ✨*  
*© 2026 Kyle Steen — All rights reserved.*
