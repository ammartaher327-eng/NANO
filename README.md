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

| Feature | v0.1 (`Nano v0.1.py`) | v0.2 (`Nano v0.2.py`) | v0.4 (`Nano v0.4.py`) | v0.5 (`Nano v0.5.py`) | v0.6 (`Nano v0.6.py`) | **v0.7 (`nano_engine.py` + `nano_ui.py`)** |
|---------|----------------------|----------------------|----------------------|---------------------------|---------------------------|---------------------------|
| **Model** | Phi-4-mini-instruct (3.8B) | Phi-4-mini-instruct (3.8B) | Phi-4-mini-instruct (3.8B) | **Phi-4-mini-instruct (3.8B) @ 4-bit** | **Phi-4-mini-instruct (3.8B) @ 4-bit** | **Phi-4-mini-instruct (3.8B) @ 4-bit** |
| **Quantization** | ❌ FP16 | ❌ FP16 | ❌ FP16 | ✅ **NF4 4-bit (bitsandbytes)** | ✅ **NF4 4-bit (bitsandbytes)** | ✅ **NF4 4-bit (bitsandbytes)** |
| **VRAM Usage** | ~7.6 GB | ~7.6 GB | ~7.6 GB | **~2.5 GB** | **~2.5 GB** | **~2.5 GB** |
| **Chat Template** | ❌ Raw tokenization | ✅ `apply_chat_template` | ✅ `apply_chat_template` | ✅ `apply_chat_template` | ✅ `apply_chat_template` | ✅ `apply_chat_template` |
| **Conversation Loop** | ❌ Single-turn | ✅ `while True` with exit | ✅ `while True` with exit | ✅ `while True` with exit | ✅ `while True` with exit | ✅ **Async TUI (Textual)** |
| **History / Memory** | ❌ None | ✅ Rolling window (6 turns) | ✅ Rolling window (6 turns) | ✅ Rolling window (6 turns) | ✅ Rolling window (6 turns) | ✅ Rolling window (12 turns) |
| **Generation Prompt** | ❌ Model autocompletes | ✅ `add_generation_prompt=True` | ✅ `add_generation_prompt=True` | ✅ `add_generation_prompt=True` | ✅ `add_generation_prompt=True` | ✅ `add_generation_prompt=True` |
| **Interrupt Handling** | ❌ None | ✅ `KeyboardInterrupt` catch | ✅ `KeyboardInterrupt` catch | ✅ `KeyboardInterrupt` catch | ✅ `KeyboardInterrupt` catch | ✅ **Non-blocking async** |
| **GPU** | ✅ CUDA | ✅ CUDA | ✅ CUDA | ✅ CUDA (quantized) | ✅ CUDA (quantized) | ✅ CUDA (quantized) |
| **System Prompt** | ❌ Hardcoded | ❌ Hardcoded | ❌ Hardcoded | ✅ **Dynamic (concise/standard)** | ✅ **Dynamic (concise/standard)** | ✅ **Dynamic (concise/standard)** |
| **Tool Use** | ❌ None | ❌ None | ✅ Keyword routing + SymPy | ✅ Keyword routing + SymPy | ✅ Keyword routing + SymPy | ✅ **Modular `MathTool` class** |
| **Tool Fallback** | ❌ N/A | ❌ N/A | ✅ Graceful error fallback | ✅ Graceful error fallback | ✅ Graceful error fallback | ✅ Structured `status/result/tool` |
| **Code Quality** | Prototype | Prototype | Prototype | Prototype | **Refactored + modular tool dispatch** | **Clean architecture (engine/UI split)** |
| **Interface** | CLI | CLI | CLI | CLI | CLI | **TUI (Textual / Rich)** |

### v0.1 — Single-Turn Prototype
- Loads model + tokenizer, moves to CUDA
- Single `input()` → single `generate()` → single response
- **Problem:** Without chat template, model treats prompt as completion task (autocompletes instead of answering)

### v0.2 — Chat Template + Conversation Loop *(absorbs v0.3)*
- Uses `tokenizer.apply_chat_template(history, add_generation_prompt=True)` — fixes autocompletion
- Multi-turn conversation with rolling history window (`max=6` turns → 12 messages)
- Clean exit via `exit`/`stop` or `Ctrl+C`
- Proper chat formatting for Phi-4-mini-instruct's expected template
- **v0.3 (Memory) absorbed here:** Conversation history and context management were implemented directly in v0.2's rolling window — no separate v0.3 release needed.

### v0.4 — First Capability: Tools
- **Keyword-based routing** — detects "solve" keyword → routes to math tool
- **SymPy math tool** with validation & graceful fallback:
  - Extracts expression after "solve" keyword
  - Regex-detects variable names (falls back to `x`)
  - Handles equations (`=`) or expressions (assumes `= 0`)
  - Try/except with graceful error dict fallback
- **Tool result injection** — results injected back into conversation history as `{"role": "tool", "content": ...}`
- Maintains rolling history window with tool messages included

### v0.5 — Speed: 4-bit Quantization & Dynamic System Prompts
- **4-bit quantization** via `BitsAndBytesConfig` (NF4, double quant, fp16 compute) — **~67% VRAM reduction**
- **Dynamic system prompt switching** — "just give me the answer" toggles concise mode; default is precise/scientific
- Maintains all v0.4 capabilities (chat template, history, math tool, interrupt handling)
- Phi-4-mini-instruct at 4-bit fits comfortably in 4GB VRAM with headroom for KV-cache

### v0.6 — Refactored Tool Dispatch + Cleaner Architecture *(Current CLI)*
- **Modular tool dispatcher** — extracted math solver into `MathTool` class with `can_handle()` / `execute()` pattern
- **Cleaner keyword routing** — dedicated `route_tool()` function, easier to extend for new tools
- **Structured tool results** — consistent `{"status": "ok|error", "result": ..., "tool": "..."}` format
- **Removed duplicate logic** — single source of truth for system prompts, history trimming
- **Ready for v0.7 tool registry** — architecture supports plug-and-play tool additions
- Maintains all v0.5 capabilities (4-bit NF4, dynamic prompts, math tool, interrupt handling)

### v0.7 — 🛠️ **TUI + Async Architecture** (`nano_engine.py` + `nano_ui.py`)
- **Engine/UI separation** — `NanoEngine` class (inference + tools) + `NanoUI` (Textual TUI)
- **Async non-blocking TUI** — `asyncio.to_thread()` for model loading & generation; UI never freezes
- **Rich terminal interface** — Header/footer, conversation log, input field, status bar, timestamps
- **Green-on-dark theme** — `#080b0a` background, `#00ff9d` accents, rounded borders
- **Extended history** — 12-turn rolling window (up from 6)
- **All v0.6 capabilities preserved** — 4-bit NF4, dynamic prompts, modular MathTool, structured results
- **Foundation for v0.8+** — clean architecture ready for tool registry, plugins, multi-model config

---

## 🚀 Quick Start

> **Requires:** Python 3.10+, PyTorch with CUDA, `transformers`, `accelerate`, `sympy`, `bitsandbytes`, `textual`, `rich`

```bash
# Clone
git clone https://github.com/ammartaher327-eng/NANO.git
cd NANO

# Install deps (CUDA-enabled PyTorch)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate sympy bitsandbytes textual rich

# Run v0.1 (single-turn)
python "Nano v0.1.py"

# Run v0.2 (multi-turn with history)
python "Nano v0.2.py"

# Run v0.4 (multi-turn + math tool)
python "Nano v0.4.py"

# Run v0.5 (4-bit quantized + dynamic prompts + math tool)
python "Nano v0.5.py"

# Run v0.6 (refactored tool dispatch + cleaner architecture + 4-bit)
python "Nano v0.6.py"

# Run v0.7 (TUI + async architecture + engine/UI split)
python nano_ui.py
```

> **Try it:** Type `solve x^2 - 5x + 6 = 0` or `solve 2x + 5 = 15` in v0.4/v0.5/v0.6/v0.7  
> **Try v0.5/v0.6/v0.7:** Type `just give me the answer` then ask anything for concise mode

---

## 🗺️ Roadmap

### v0.1 — ✅ Done: Foundation
- [x] Load model + tokenizer (Phi-4-mini-instruct)
- [x] Single prompt → single response
- [x] GPU-accelerated (CUDA)

### v0.2 — ✅ Done: Chat UX *(absorbs v0.3)*
- [x] Chat templates (`apply_chat_template`) — fixes autocompletion
- [x] Basic conversation loop (`while True`)
- [x] Rolling conversation history
- [x] **v0.3 Memory absorbed:** persistent/inspectable history, context management, session save/load → implemented as rolling window in v0.2

### v0.4 — ✅ Done: First Capability — Tools
- [x] Keyword-based routing (detect intent → route to tool)
- [x] SymPy math tool with validation + fallback
- [x] Tool result injection back into context

### v0.5 — ✅ Done: Speed — Quantization & Offloading
- [x] 4-bit quantization (bitsandbytes NF4)
- [x] Dynamic system prompts (concise/standard modes)
- [ ] CPU + GPU offloading exploration (llama.cpp `-ngl`)
- [ ] Benchmark tokens/sec vs quality trade-offs

### v0.6 — ✅ Done: Refactored Tool Dispatch
- [x] Modular tool dispatcher pattern (`can_handle` / `execute`)
- [x] Cleaner keyword routing function
- [x] Structured tool result format
- [x] Architecture ready for tool registry / plugin system

### v0.7 — ✅ **Done: TUI + Async Architecture**
- [x] Engine/UI separation (`NanoEngine` + `NanoUI`)
- [x] Async non-blocking TUI with `asyncio.to_thread()`
- [x] Rich terminal interface (Textual + Rich)
- [x] Extended history (12 turns)
- [x] All v0.6 capabilities preserved (4-bit NF4, dynamic prompts, modular tools)

### v0.8 — 🌐 More Tools: Search
- [ ] Pandas data handling tool (CSV/Excel load, stats, filtering, groupby)
- [ ] Tool registry / plugin system (auto-discovery, `@tool` decorator)
- [ ] Basic search tool (DuckDuckGo / web search via API)
- [ ] Local file search (ripgrep / grep wrapper)

### v1.0 — ✨ Polish: Production CLI
- [ ] Clean CLI / TUI (argparse/click + rich)
- [ ] Config file (YAML/TOML) — model, ngl, temp, system prompt
- [ ] Phone / web access (Termux, simple web UI)

### v1.0+ — 🚀 Stretch Goals
- [ ] Fine-tuning with Unsloth / QLoRA
- [ ] Attention visualization (hooks + matplotlib)
- [ ] Custom skill format inspired by Hermes Agent

---

## ⚠️ Known Limitations

| Version | Limitation |
|---------|------------|
| **v0.1** | No chat template → model autocompletes instead of answering |
| **v0.2/v0.4/v0.5/v0.6** | Fixed 6-turn rolling window (hardcoded `max=6`) — no summarization, no persistence |
| **v0.2/v0.4/v0.5/v0.6** | Single model only (Phi-4-mini), no config file |
| **v0.4/v0.5/v0.6** | Keyword routing is brittle ("solve" must appear); SymPy tool only handles single-variable algebra; no tool registry/plugin system (v0.6 architecture ready for it) |
| **v0.7** | TUI requires `textual` + `rich` deps; no mouse scroll in conversation log yet; engine still hardcoded to Phi-4-mini |
| **All versions** | CUDA-only (no CPU fallback); no quantization in v0.1-v0.4; Windows-only paths hardcoded in some spots |
| **v0.5/v0.6/v0.7** | `bitsandbytes` on Windows requires `bitsandbytes-windows` wheel; no explicit layer offloading (`-ngl` equivalent) |

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