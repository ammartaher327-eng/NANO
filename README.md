# NANO v0.1 — Local AI Assistant Prototype

> A minimal, hardware-aware local LLM assistant built for consumer GPUs (4GB VRAM target). This is the **prototype** — the first working iteration of a personal AI that runs entirely on your machine.

---

## 🎯 Project Vision

Build a capable local AI assistant that:
- Runs **offline** on consumer hardware (RTX 3050 4GB VRAM, 16GB RAM)
- Uses **GPU offloading** (llama.cpp `-ngl`) to run larger models than VRAM allows
- Prioritizes **capability over speed** — accept slower generation for smarter models
- Stays **simple, hackable, and transparent** — no black-box cloud dependencies

---

## 🖥️ Target Hardware

| Component | Spec |
|-----------|------|
| CPU | AMD Ryzen 7 7445HS (8C/16T, Zen 4) |
| RAM | 16GB DDR5 |
| GPU | NVIDIA RTX 3050 Laptop — **4GB VRAM** |
| Storage | 512GB SSD |
| OS | Windows 11 |

---

## 📦 Current State (v0.1 Prototype)

This repository contains the **very first working prototype** — a single-file Python script using Hugging Face Transformers + PyTorch to run **Phi-4-mini-instruct (3.8B)** on CUDA.

```bash
# File: Nano v0.1.py
# - Loads Phi-4-mini-instruct from Hugging Face
# - Moves model to CUDA (GPU)
# - Single-turn chat loop via `input()`
```

### ⚠️ Known Limitations (v0.1)

| Issue | Impact | Planned Fix |
|-------|--------|-------------|
| **VRAM OOM risk** | Phi-4-mini at FP16 needs ~7-8GB VRAM; 4GB will OOM | Switch to **llama.cpp/GGUF with 4-bit quantization + GPU offload (`-ngl`)** |
| Single-turn only | No conversation history/memory | Add chat template + history management |
| No streaming | Full response waits for generation | Add token streaming for perceived speed |
| Hardcoded model | Not configurable | CLI args / config file for model selection |

---

## 🚀 Quick Start (Current Prototype)

> **Requires:** Python 3.10+, PyTorch with CUDA, `transformers`, `accelerate`

```bash
# Clone
git clone https://github.com/ammartaher327-eng/NANO.git
cd NANO

# Install deps (CUDA-enabled PyTorch)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate

# Run (will download ~7GB model on first run)
python "Nano v0.1.py"
```

---

## 🗺️ Roadmap

### v0.2 — GGUF + llama.cpp (GPU Offload)
- [ ] Convert to llama.cpp Python bindings / CLI
- [ ] Use 4-bit GGUF models (Q4_K_M, Q5_K_M)
- [ ] GPU layer offloading (`-ngl 20-30` for RTX 3050 4GB)
- [ ] Support larger models (7B, 8B, 14B) via offload

### v0.3 — Chat UX
- [ ] Multi-turn conversation with history
- [ ] Streaming token output
- [ ] System prompt / persona config
- [ ] Simple CLI flags (`--model`, `--ngl`, `--temp`)

### v0.4 — Assistant Features
- [ ] Tool calling / function calling (local tools)
- [ ] RAG / local document QA
- [ ] Persistent memory / long-term context
- [ ] Voice I/O (Whisper + TTS)

### v1.0 — Polished Local Assistant
- [ ] Clean CLI / TUI
- [ ] Config file (YAML/TOML)
- [ ] Model auto-download / management
- [ ] Cross-platform (Linux/Windows/macOS)

---

## 🤝 Why This Exists

Most local LLM tools assume 8GB+ VRAM or cloud fallback. This project targets the **4GB VRAM reality** many laptop users face — proving you can run capable models by offloading layers to system RAM via llama.cpp, accepting slower tokens for higher intelligence.

> **"Slow but smart > fast but dumb"**

---

## 📄 License

MIT — free to use, modify, distribute.

---

## 🙋 Author

**Ammar Taher** — [@ammartaher327-eng](https://github.com/ammartaher327-eng)

Building NANO as a learning project to understand LLMs "under the hood" — from tokenizer to KV-cache to GPU offloading. Every iteration teaches something new.