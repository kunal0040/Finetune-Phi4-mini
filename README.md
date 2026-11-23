# Kaitu AI: Phi-4-mini Fine-Tuning Pipeline (`phi4:mini-kaitu`)

[![Ollama](https://img.shields.io/badge/Ollama-phi4%3Amini--kaitu-blue.svg)](https://ollama.com)
[![Base Model](https://img.shields.io/badge/Base_Model-Microsoft_Phi--4--mini_(3.8B)-cyan.svg)](https://huggingface.co/microsoft/Phi-4-mini-instruct)
[![Format](https://img.shields.io/badge/Format-Q4__K__M_GGUF_(2.49GB)-green.svg)](https://github.com/ggerganov/llama.cpp)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

This repository contains the complete fine-tuning pipeline, curated dataset engineering, multi-round benchmark evaluations, and production runtime guards for **Kaitu**, a local, privacy-first personal AI assistant running on Windows.

The production model **`phi4:mini-kaitu`** is derived from **Microsoft Phi-4-mini (3.8B)** via QLoRA fine-tuning on Dual NVIDIA Tesla T4 GPUs and quantized to 4-bit (`Q4_K_M GGUF`). It is deployed locally via [Ollama](https://ollama.com).

> 💡 **Looking for the complete personal AI assistant?**  
> If you want to access the final deployed model, run the desktop client, and test the full assistant with local tools and integrations, visit the main assistant repository:  
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

## 📊 Complete Fine-Tuning & Benchmark Scorecard (V1 – V8)

Across eight iterations of dataset engineering, QLoRA fine-tuning, GGUF quantization, and hand-graded evaluations across 300+ prompts, **Version 6 (V6)** proved to be the most capable and well-balanced daily-driver assistant:

| Category | V4 (200) | V5 (300) | V5_fixed (300) | **V6 (`phi4:mini-kaitu`)** | V7 (300) | V8 (300) |
|---|---|---|---|---|---|---|
| **Identity (of 20)** | ~14 | ~11 | ~11 | **~12** | ~8 | ~8 |
| **Casual Conversation** | ~12 | ~8 | ~10 | **~15** | ~12 | ~12 |
| **Instruction Following** | ~13 | ~7 | ~12 | **~12** | ~12 | ~10 |
| **Coding & Python Syntax** | ~10 | ~6 | ~8 | **~11** | ~9 | ~11 |
| **Debugging** | ~11 | ~6 | ~9 | **~9** | ~7 | ~8 |
| **Architecture & Systems** | ~15 | ~13 | ~14 | **~17** | ~15 | ~16 |
| **General Knowledge** | ~13 | ~10 | ~12 | **~14** | ~13 | ~11 |
| **Reasoning & Logic** | ~16 | ~9 | ~14 | **~17** | ~15 | ~14 |
| **Uncertainty & Boundaries** | ~16 | ~11 | ~12 | **~15** | ~14 | ~14 |
| **Support & Advice** | ~14 | ~13 | ~14 | **~12** | ~12 | ~13 |
| **Shared 200 Subtotal** | **~134 (67%)** | **~94 (47%)** | **~116 (58%)** | **~134 (67%)** | **~117 (58%)** | **~117 (58%)** |
| **New 100 Prompts** | *N/A* | ~45 | ~60 | **~64** | ~59 | ~57 |
| **Total 300 Score** | *N/A* | **~139 (46%)** | **~176 (58%)** | **~198 (66%)** | **~176 (58%)** | **~174 (58%)** |

---

## 🔍 Detailed Version Breakdown & Technical Post-Mortem

### Version 4 (Initial Technical Core)
- **Strengths**: Deep technical precision, strong architecture analysis, reliable refusals on ungrounded system questions.
- **Failures**: High frequency of third-person name leaks (`"Kunal's personal AI"`). Narrow scope; struggled with casual banter and practical word math.

### Version 5 & V5_fixed (Expansion & Format Delimiters)
- **V5 Flaws**: Suffered from tokenizer delimiter issues and synthetic self-dialogue (`Kunal:` / `AI:` labels inside completions).
- **V5_fixed**: Cleared synthetic self-dialogue and repaired basic math (bat/ball, tips, speed). Retained 37 third-person leaks and occasional hallucinated facts.

### Version 6 (The Production Baseline — Deployed as `phi4:mini-kaitu`)
- **Key Fixes**:
  - Completely eliminated third-person name leaks (dropped from 37 to 0).
  - Warm, conversational second-person tone.
  - Substantially improved math: bat & ball ($0.05), tip on $85 ($15.30), average speed (40 mph), discount stacking (28%), tailwind (550 mph), sock drawer (3 socks), jug puzzle (4 gallons).
  - Real literature recommendations (*The Martian*, *Big Magic*, *Sapiens*).
  - Architecture answers achieved peak score (~17/20).
- **Residual Flaws**:
  - Trailing `Answer: ...` and `Step 1/Step 2` in ~45 non-math explanations.
  - Advised `git push -f` for non-fast-forward divergence on prompt #86.
  - Signed sample emails as "Kaitu" instead of "[Your Name]".
  - *Resolution*: Handled via deterministic runtime guards (`scripts/kaitu_safety_and_guard.py`).

### Version 7 & Version 8 (Overfitting at 3.8B Capacity)
- **Findings**:
  - Overfitting to high-frequency identity tokens flipped user and assistant roles (`"Your name is Kaitu"`, `"You built me, Kunal"`).
  - Heavy math formatting bled into non-math domains.
  - Fabricated risky commands (#194 recommending `DROP TABLE IF EXISTS` after accidental drop; #94 suggesting `rm -rf ~/envs/*`).
  - V8 developed doubled trailing periods (`..`) across ~60 answers due to delimiter mismatches.
- **Architectural Conclusion**: Validated that further SFT on 3.8B parameters leads to seesaw regressions. The optimal production setup pairs **V6 weights with lightweight runtime guards**.

---

## 🛡️ Production Runtime Guards

Located in `scripts/kaitu_safety_and_guard.py`:

1. **`KaituOutputCleaner`**: Purges trailing `Answer:` / `Step` headers, cleans formatting artifacts, and ensures emails sign off as `[Your Name]`.
2. **`KaituCommandGuard`**: Intercepts destructive commands (`git push -f`, `rm -rf`, fake PostgreSQL `ROLLBACK`).
3. **`KaituCodeValidator`**: Validates all generated Python code blocks via `ast.parse`.
4. **`KaituCalculator`**: Exact deterministic computation for compound percentages, bill splits, and conversions.
5. **`KaituMemory`**: Injects user and assistant identity dynamically into the system prompt at runtime.

---

## ⚡ Cloud Training Pipeline (Kaggle GPU)

- **Local Constraint**: ASUS TUF A15 (AMD Ryzen 7, NVIDIA RTX 2050 4 GB VRAM). WDDM overhead leaves ~2.9 GB usable VRAM—insufficient for 4-bit backpropagation (~4.5–5.0 GB required).
- **Solution**: Offloaded training to free Dual NVIDIA Tesla T4 GPUs on Kaggle Cloud via automated scripts (`scripts/build_kaggle_kernel.py`).
- **Gzip Payload Compression**: Datasets are compressed using `gzip` and base64-encoded to keep generated notebook payloads under 220 KB, preventing Windows Python socket aborts (`WinError 10053`).
- **Direct GGUF Streaming**: Outputs are exported directly to 4-bit GGUF and pulled via Kaggle's authenticated proxy into local Ollama storage.

---

## 📂 Repository Layout

```
Finetune-Phi4-mini/
├── README.md                           # Master project guide, scorecard & technical log
├── Modelfile                           # Production Ollama configuration for phi4:mini-kaitu
├── requirements.txt                    # Python dependencies
├── config/
│   └── training_config.yaml            # QLoRA hyperparameters & token limits
├── .agents/skills/kaitu/SKILL.md       # Antigravity skill for direct chat integration
├── data/
│   ├── v6/                             # Gold-standard V6 training & eval datasets (JSONL)
│   └── benchmarks/
│       ├── eval_200_prompts.json       # Shared 200 benchmark prompts
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
    └── benchmarks/                     # Evaluated outputs across versions (V1–V8, 500 prompts)
```

---

## 🔮 Future Resumption Guide (If Fine-Tuning Again)

If you decide to revisit fine-tuning in the future:
1. **Do NOT run full SFT retraining from scratch**: Retraining on raw datasets rewrites weights unpredictably on 3.8B models.
2. **Use Direct Preference Optimization (DPO)**: Start directly from `phi4:mini-kaitu` (V6) weights and train a small pair-preference dataset (Chosen vs Rejected) targeting only remaining edge cases:
   - *Chosen*: Clean email ending `[Your Name]` / *Rejected*: Signed `Kaitu`.
   - *Chosen*: `git pull --rebase origin main` / *Rejected*: `git push -f`.
3. **Or Scale to an 8B Model**: If you need $\ge 85\%$ accuracy across deep scientific reasoning and multi-turn coding, migrate the dataset to **Qwen 2.5 7B/14B** or **Llama 3.1 8B**, which have inherently higher capacity to absorb complex instruction nuances.
