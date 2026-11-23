# Kaitu AI: Phi-4-mini Fine-Tuning Pipeline (`phi4:mini-kaitu`)

This repository contains the complete fine-tuning pipeline, curated dataset engineering tools, benchmarks, and production runtime guards for **Kaitu**, a local, privacy-respecting AI assistant running on Windows.

The production model **`phi4:mini-kaitu`** is derived from **Microsoft Phi-4-mini (3.8B)** via QLoRA fine-tuning on Dual NVIDIA T4 GPUs and quantized to 4-bit (`Q4_K_M GGUF`). It is deployed locally via [Ollama](https://ollama.com).

> 💡 **Looking for the complete personal AI assistant?**
> If you want to access the final deployed model, run the desktop client, and test the full assistant with local tools and integrations, visit the main repository:  
> 👉 [**https://github.com/kunal0040/Kaitu**](https://github.com/kunal0040/Kaitu)

---

## 🚀 Quick Start

### 1. Chat via Ollama CLI
```powershell
ollama run phi4:mini-kaitu
```

### 2. Chat with Production Runtime Guards (Recommended)
```powershell
python scripts/bridge_kaitu.py "Hello Kaitu! What are your strengths?"
```
The bridge automatically routes prompts through `phi4:mini-kaitu` on Ollama and filters output through `KaituOutputCleaner` and `KaituCommandGuard`.

### 3. Use in Antigravity Chat
A workspace skill is provided in `.agents/skills/kaitu/SKILL.md`. Simply ask in chat:
> *"Ask Kaitu: <your question>"*

### 4. Local OpenAI-Compatible API
- **Endpoint**: `http://localhost:11434/v1`
- **Model Name**: `phi4:mini-kaitu`
- **API Key**: `ollama` (or any string)

---

## 🏛️ System Architecture

```
                       [User Prompt]
                             │
                             ▼
                 ┌───────────────────────┐
                 │  KaituMemory          │ ── Injects user & assistant identity
                 └───────────────────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │  Ollama Engine        │
                 │  (phi4:mini-kaitu)    │ ── Local GPU inference (Dual T4 trained)
                 └───────────────────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │  KaituOutputCleaner   │ ── Purges trailing "Answer:", enforces [Your Name]
                 └───────────────────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │  KaituCommandGuard    │ ── Blocks dangerous commands (-f, rm -rf, DROP)
                 └───────────────────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │  KaituCodeValidator   │ ── Validates Python syntax with ast.parse
                 └───────────────────────┘
                             │
                             ▼
                       [Safe Output]
```

---

## 📂 Repository Layout

```
Finetune-Phi4-mini/
├── README.md                           # Main project overview & quickstart
├── FINETUNE_LOG.md                     # Exhaustive technical fine-tuning log (V1 - V8)
├── .agents/skills/kaitu/SKILL.md       # Antigravity skill for direct chat integration
├── data/
│   ├── v6/                             # Gold-standard V6 training & eval datasets
│   └── benchmarks/
│       ├── eval_200_prompts.json       # Original shared benchmark prompts
│       ├── eval_300_prompts.json       # Comprehensive 300 benchmark prompts
│       └── eval_500_prompts.json       # Extended 500 benchmark prompts
├── scripts/
│   ├── bridge_kaitu.py                 # CLI & skill bridge to phi4:mini-kaitu
│   ├── kaitu_safety_and_guard.py       # Production guards (CommandGuard, Cleaner, Validator)
│   ├── benchmark_3way.py               # Automated Ollama benchmark evaluation runner
│   ├── score_v6_comprehensive.py       # Comprehensive regression benchmark scorer
│   ├── score_500_best_to_worst.py      # Quality ranking engine (Best to Worst)
│   └── build_kaggle_kernel.py          # Kaggle interactive kernel packager & generator
└── results/
    └── benchmarks/                     # JSON evaluation outputs across benchmark runs
```

---

## 📊 Model Scorecard Summary (Shared Prompts)

| Benchmark Version | Shared 200 Score | Primary Characteristics |
|---|---|---|
| **V4** | ~134 (67%) | Strong technical knowledge; third-person name leaks |
| **V5 / V5_fixed** | ~116 (58%) | Expanded into math & everyday; self-dialogue & name leaks |
| **V6 (`phi4:mini-kaitu`)** | **~134 (67%)** | **Best balanced overall: 0 name leaks, strong math & architecture** |
| **V7 / V8** | ~117 (58%) | Overfitting: role confusion, invented commands, delimiter ticks |

For full version history, root-cause analyses, and benchmark breakdowns across all 8 iterations, see [FINETUNE_LOG.md](file:///d:/Antigravity/Finetune/FINETUNE_LOG.md).
