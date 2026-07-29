# NANO — Local AI Assistant Prototype

> A minimal, hardware-aware local LLM assistant built for consumer GPUs (4GB VRAM target). This is the **prototype** — the first working iterations of a personal AI that runs entirely on your machine.

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

## 📦 Version Comparison

| Feature | v0.1 (`Nano v0.1.py`) | v0.2 (`Nano v0.2.py`) |
|---------|----------------------|----------------------|
| **Model** | Phi-4-mini-instruct (3.8B) | Phi-4-mini-instruct (3.8B) |
| **Chat Template** | ❌ Raw tokenization | ✅ `apply_chat_template` |
| **Conversation Loop** | ❌ Single-turn | ✅ `while True` with exit |
| **History / Memory** | ❌ None | ✅ Rolling window (6 turns) |
| **Generation Prompt** | ❌ Model autocompletes | ✅ `add_generation_prompt=True` |
| **Interrupt Handling** | ❌ None | ✅ `KeyboardInterrupt` catch |
| **GPU** | ✅ CUDA | ✅ CUDA |

### v0.1 — Single-Turn Prototype
- Loads model + tokenizer, moves to CUDA
- Single `input()` → single `generate()` → single response
- **Problem:** Without chat template, model treats prompt as completion task (autocompletes instead of answering)

### v0.2 — Chat Template + Conversation Loop
- Uses `tokenizer.apply_chat_template(history, add_generation_prompt=True)` — fixes autocompletion
- Multi-turn conversation with rolling history window (`max=6` turns → 12 messages)
- Clean exit via `exit`/`stop` or `Ctrl+C`
- Proper chat formatting for Phi-4-mini-instruct's expected template

---

## 🚀 Quick Start

> **Requires:** Python 3.10+, PyTorch with CUDA, `transformers`, `accelerate`

```bash
# Clone
git clone https://github.com/ammartaher327-eng/NANO.git
cd NANO

# Install deps (CUDA-enabled PyTorch)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate

# Run v0.1 (single-turn)
python "Nano v0.1.py"

# Run v0.2 (multi-turn with history)
python "Nano v0.2.py"
```

---

## 🗺️ Roadmap

### v0.1 — ✅ Done: Foundation
- [x] Load model + tokenizer (Phi-4-mini-instruct)
- [x] Single prompt → single response
- [x] GPU-accelerated (CUDA)

### v0.2 — ✅ Done: Chat UX
- [x] Chat templates (`apply_chat_template`) — fixes autocompletion
- [x] Basic conversation loop (`while True`)
- [x] Rolling conversation history

### v0.3 — 🔄 Next: Memory
- [ ] Conversation history as a real concept (persistent, inspectable)
- [ ] Context as a real concept (summarization, truncation strategies)
- [ ] Session save/load

### v0.4 — 🔜 First Capability: Tools
- [ ] Keyword-based routing (detect intent → route to tool)
- [ ] SymPy math tool with validation + fallback
- [ ] Tool result injection back into context

### v0.5 — ⚡ Speed: Quantization & Offloading
- [ ] 4-bit quantization (bitsandbytes / GGUF)
- [ ] CPU + GPU offloading exploration (llama.cpp `-ngl`)
- [ ] Benchmark tokens/sec vs quality trade-offs

### v0.6 — 🛠️ More Tools
- [ ] Pandas data handling tool (CSV/Excel analysis)
- [ ] Basic search tool (local web search / duckduckgo)
- [ ] Tool registry / plugin system

### v1.0 — ✨ Polish: Production CLI
- [ ] Clean CLI / TUI (argparse/click + rich)
- [ ] Config file (YAML/TOML) — model, ngl, temp, system prompt
- [ ] Phone / web access (Termux, simple web UI)

### v1.0+ — 🚀 Stretch Goals
- [ ] Fine-tuning with Unsloth / QLoRA
- [ ] Attention visualization (hooks + matplotlib)
- [ ] Custom skill format inspired by Hermes Agent

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