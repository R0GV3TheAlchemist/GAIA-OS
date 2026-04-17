# ⚡ GAIA Quick Start — Free, No API Keys Required

You can run GAIA completely free using **Ollama** — an app that runs AI models on your own computer. No account. No credit card. No internet required once set up.

---

## What You Need

- A computer (Windows, Mac, or Linux)
- Python 3.11+ — [Download here](https://www.python.org/downloads/)
- Node.js 18+ — [Download here](https://nodejs.org/)
- Ollama — [Download here](https://ollama.com/) *(free forever)*

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

That's it. The default config already points to Ollama — no editing needed.

---

## Step 4 — Start GAIA

**Start Ollama first** (if it’s not already running):
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

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'core'` | You must run `python -m core.server` from the **root GAIA-APP folder** |
| `Connection refused` on port 8008 | Make sure the backend started without errors |
| `ollama: command not found` | Install Ollama from [ollama.com](https://ollama.com) |
| Slow responses | Try `ollama pull phi3:mini` — it’s smaller and faster |
| Port 5173 already in use | Close other terminals and try again |

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

*GAIA is open-source and free. Built with love. ✨*
