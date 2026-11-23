# Kaitu AI — Fine-Tuning Phi-4-mini

<p align="center">
  <b>QLoRA Fine-Tuning · Dataset Engineering · Model Evaluation · Local AI Deployment</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Base_Model-Phi--4--mini_(3.8B)-blue?style=flat-square">
  <img src="https://img.shields.io/badge/Fine--Tuning-QLoRA-orange?style=flat-square">
  <img src="https://img.shields.io/badge/Quantization-Q4_K_M-green?style=flat-square">
  <img src="https://img.shields.io/badge/Deployment-Ollama-black?style=flat-square">
  <img src="https://img.shields.io/badge/Development-AI--Assisted-purple?style=flat-square">
  <img src="https://img.shields.io/badge/License-MIT-blueviolet?style=flat-square">
</p>

---

> [!TIP]
> **Looking for the complete personal AI assistant application?**  
> This repository contains the machine learning fine-tuning pipeline, benchmarks, and dataset tools. To access the final deployed model, desktop interface, integrations, and runtime tools, visit the primary repository:  
> 👉 [**https://github.com/kunal0040/Kaitu**](https://github.com/kunal0040/Kaitu)

---

## Overview

**Kaitu AI** is a fine-tuning project focused on adapting Microsoft's **Phi-4-mini (3.8B)** into a locally deployable personal AI assistant.

The project explores how iterative dataset engineering, parameter-efficient fine-tuning (PEFT), quantization, rigorous behavioral evaluation, and external runtime safeguards can substantially improve the capabilities of a compact language model under consumer hardware constraints.

Rather than relying on a single training run, the project went through eight distinct iterations (**V1–V8**), involving continuous dataset refinement, hand-graded behavioral evaluations, failure root-cause analysis, and regression testing. The final production baseline selected for deployment is **V6**, distributed locally as `phi4:mini-kaitu` through Ollama.

---

## Project Objectives

- **Compact Assistant**: Develop a responsive, privacy-respecting conversational assistant using a lightweight model (<4B parameters).
- **Behavioral Tuning**: Improve instruction following, everyday reasoning, safe command execution, and coding assistance while eliminating synthetic persona artifacts.
- **Dataset Engineering**: Experiment with curated domain splits, negative-constraint prompts, and synthetic dialogue mitigation.
- **Regression Tracking**: Empirically evaluate multi-version drift and identify the capacity boundary where further SFT causes performance degradation.
- **Local Deployment & Guards**: Quantize to 4-bit GGUF for low-latency inference on local hardware and implement deterministic Python runtime guards.

---

## AI-Assisted Development

This project was developed with assistance from **Google Antigravity**, an AI-powered agentic development environment.

Antigravity was utilized throughout the development cycle to assist with pipeline orchestration, data preparation scripts, automated Kaggle job generation, regression tracking, and tool bridges. All training outcomes, benchmark scorecards, and model behaviors were independently evaluated and verified.

---

## Model Specifications

| Parameter | Details |
|---|---|
| **Project Name** | Kaitu AI |
| **Base Model** | Microsoft Phi-4-mini-Instruct |
| **Base Parameter Count** | 3.8 Billion |
| **Fine-Tuning Method** | QLoRA (4-bit NormalFloat, Rank 16, Alpha 32) |
| **Training Framework** | Hugging Face (`transformers`, `peft`, `bitsandbytes`, `trl`) |
| **Training Compute** | Dual NVIDIA Tesla T4 GPUs (Kaggle Cloud) |
| **Quantization** | 4-bit GGUF (`Q4_K_M`) via `llama.cpp` |
| **Active Binary Size** | ~2.49 GB |
| **Local Inference Engine** | Ollama |
| **Production Baseline** | **Version 6 (V6)** |
| **Ollama Model Identifier** | `phi4:mini-kaitu` |

---

## Training & Evaluation Iterations

Across eight iterations, empirical testing demonstrated that continuous SFT on small models does not produce linear improvements. Beyond a certain capacity threshold, aggressive fine-tuning introduces seesaw regressions:

| Version | Focus / Methodology | Main Observations & Outcome |
|---|---|---|
| **V1–V4** | Initial dataset & technical foundations | Strong technical baseline and architecture knowledge; suffered from third-person identity leaks (`"Kunal's AI"`). |
| **V5** | Broad dataset expansion (everyday & math) | Coverage expanded, but synthetic dialogue tags (`Kunal:` / `AI:`) and math formatting bled into normal text. |
| **V5_fixed** | Formatting & token delimiter repairs | Repaired synthetic dialogue; improved benchmark score from 46% to 58%, though identity leaks persisted. |
| **V6** | Identity repair, tone softening & math refinement | **Selected Production Baseline (66% overall)**. Zero third-person leaks, natural conversational tone, peak architecture score. |
| **V7** | Targeted SFT patching for residual V6 edge cases | Introduced regressions: flipped user/assistant identity roles (`"Your name is Kaitu"`), invented shell commands. |
| **V8** | Formatting suppression & hyperparameter tuning | Delimiter mismatch caused doubled periods (`..`) across ~60 answers; confirmed diminishing returns of further SFT. |

---

## Benchmark Results

All versions were evaluated on a shared multi-category benchmark suite covering coding, system architecture, instruction following, reasoning, and casual interaction.

> *Note: Scores represent project-specific hand-graded evaluations designed to detect behavioral drift and regressions across iterations.*

### Overall Performance Trend

| Model Version | Shared Benchmark Score | Accuracy Percentage |
|---|---|---|
| **V5** | 139 / 300 | 46% |
| **V5_fixed** | 176 / 300 | 58% |
| **V6 (`phi4:mini-kaitu`)** | **198 / 300** | **66% (Selected)** |
| **V7** | 176 / 300 | 58% |
| **V8** | 174 / 300 | 58% |

### V6 Detailed Category Breakdown

| Evaluation Category | V6 Score | Benchmark Focus |
|---|---|---|
| **Identity & Persona** | 12 / 20 | First-person stance, boundary grounding, refusal of fabricated identities |
| **Casual Conversation** | 15 / 20 | Warmth, natural banter, concise conversational replies |
| **Instruction Following** | 12 / 20 | Word limits, format constraints, negative requirements |
| **Coding & Python Syntax** | 11 / 20 | Clean function implementation, standard library usage |
| **Debugging** | 9 / 20 | Identifying root cause, stack traces, subtle logic bugs |
| **Architecture & Systems** | **17 / 20** | Distributed systems, caching, database selection, CAP theorem |
| **General Knowledge** | 14 / 20 | Real literature recommendations, history, science facts |
| **Reasoning & Logic** | **17 / 20** | Word problems (bat & ball, Monty Hall, tailwind, jug puzzles) |
| **Uncertainty & Boundaries** | 15 / 20 | Honest refusals regarding inaccessible local files, banks, and hardware |
| **Support & Advice** | 12 / 20 | Practical developer career tips, prioritization, productivity |
| **Shared 200 Subtotal** | **134 / 200 (67%)** | Standard evaluation baseline |
| **New 100 Prompts** | **64 / 100 (64%)** | Held-out evaluation prompts |
| **Total Score** | **198 / 300 (66%)** | **Best overall balance** |

---

## Why V6 Was Retained Over V7 / V8

Fine-tuning small models (~3.8B parameters) reveals a distinct **capacity boundary**:
1. **Identity Inversion in V7/V8**: Repetitive reinforcement of identity tokens caused the model to confuse who was the assistant and who was the user.
2. **Format Contamination**: Heavy training on math explanations caused mathematical step prefixes (`Answer: ...`, `Step 1:`) to leak into casual creative writing.
3. **Seesaw Effect**: Fixing rare edge cases via SFT broke previously stable capabilities (e.g. math accuracy and exception handling).

**The Solution**: Ship **V6 weights** as the frozen neural core, and resolve formatting quirks and destructive command risks using lightweight, deterministic Python runtime guards.

---

## System Architecture

The deployed model operates behind a defense-in-depth runtime pipeline that manages identity injection, output normalization, and command safety:

```
                          [User Prompt]
                                │
                                ▼
                    ┌───────────────────────┐
                    │      KaituMemory      │ ── Dynamically injects user & persona context
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │     Ollama Engine     │
                    │   (phi4:mini-kaitu)   │ ── Local 4-bit GPU inference
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   KaituOutputCleaner  │ ── Strips stray "Answer:" headers & normalizes sign-offs
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   KaituCommandGuard   │ ── Intercepts destructive commands (git -f, rm -rf, DROP)
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   KaituCodeValidator  │ ── Verifies Python syntax via AST parsing
                    └───────────────────────┘
                                │
                                ▼
                          [Safe Output]
```

---

## Runtime Safeguards

Located in [`scripts/kaitu_safety_and_guard.py`](scripts/kaitu_safety_and_guard.py):

- **`KaituOutputCleaner`**: Eliminates trailing `Answer:` / `Step` prefixes from non-math responses, cleans doubled terminal periods, and standardizes email sign-offs to `[Your Name]`.
- **`KaituCommandGuard`**: Rule-based regex filter that catches high-risk suggestions (`git push --force`, `rm -rf`, raw table drops) and replaces them with non-destructive alternatives (`git pull --rebase origin main`, backups).
- **`KaituCodeValidator`**: Runs Python's `ast.parse` over code blocks in model completions to catch syntax errors before displaying them.
- **`KaituCalculator`**: Intercepts multi-step math prompts (compound growth, percentages) for exact deterministic calculation.
- **`KaituMemory`**: Ensures dynamic session identity without hardcoding user names into base model weights.

> *Security Notice: These safeguards represent an added defensive layer and do not replace a full OS-level sandbox. All generated code and shell commands should be reviewed before execution.*

---

## Cloud Training Pipeline (Kaggle Dual T4)

### Hardware Constraints
Local training was constrained by an ASUS TUF A15 laptop (NVIDIA RTX 2050, 4 GB VRAM). Due to Windows WDDM overhead, usable VRAM drops to ~2.9 GB, which is insufficient for 4-bit gradient backpropagation (~4.5–5.0 GB required).

### Cloud Workflow & Optimizations
1. **Automated Kernel Packaging**: [`scripts/build_kaggle_kernel.py`](scripts/build_kaggle_kernel.py) generates a self-contained Kaggle notebook with embedded datasets, dependency setup, and quantization steps.
2. **Gzip Buffer Compression**: Raw datasets embedded in `.ipynb` files trigger socket aborts on Windows if uncompressed. Compressing the buffers with `gzip` keeps notebook payloads under 220 KB.
3. **Quantization & Export**: Models are exported directly to 16-bit GGUF, quantized to `Q4_K_M` via `llama.cpp`, and pulled directly into local Ollama storage.

---

## Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- Git

### 1. Clone the Repository
```powershell
git clone https://github.com/kunal0040/Finetune-Phi4-mini.git
cd Finetune-Phi4-mini
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Run the Model via Ollama
If `phi4:mini-kaitu` is registered locally in Ollama:
```powershell
ollama run phi4:mini-kaitu
```

### 4. Run with Runtime Guards (Recommended)
```powershell
python scripts/bridge_kaitu.py "Hello Kaitu! What are your core strengths?"
```

### 5. Local OpenAI-Compatible API
Connect any standard LLM client to Ollama's local API:
- **Endpoint**: `http://localhost:11434/v1`
- **Model**: `phi4:mini-kaitu`
- **API Key**: `ollama` (placeholder)

---

## Repository Structure

```
Finetune-Phi4-mini/
├── README.md                           # Master project guide, benchmarks & architecture
├── Modelfile                           # Ollama configuration for phi4:mini-kaitu
├── requirements.txt                    # Project Python dependencies
├── config/
│   └── training_config.yaml            # QLoRA hyperparameters & token limits
├── .agents/skills/kaitu/
│   └── SKILL.md                        # Antigravity skill for chat integration
├── data/
│   ├── v6/                             # Gold-standard V6 training & eval datasets (JSONL)
│   └── benchmarks/                     # 200, 300, and 500 prompt evaluation suites
├── kaggle_job/                         # Generated standalone cloud training packages
├── notebooks/                          # Interactive training notebooks
├── scripts/
│   ├── bridge_kaitu.py                 # CLI & skill bridge to phi4:mini-kaitu
│   ├── kaitu_safety_and_guard.py       # Production guards (CommandGuard, Cleaner, Validator)
│   ├── benchmark_3way.py               # Automated Ollama evaluation runner
│   ├── score_v6_comprehensive.py       # Comprehensive regression benchmark scorer
│   ├── score_500_best_to_worst.py      # Quality ranking engine (Best to Worst)
│   └── build_kaggle_kernel.py          # Automated cloud kernel generator
└── results/
    └── benchmarks/                     # Detailed JSON outputs across versions (V1–V8)
```

---

## Limitations

Kaitu is an experimental fine-tuned small language model (3.8B) and is subject to known SLM constraints:
- Complex multi-step reasoning may occasionally contain logical slips.
- Output formatting may occasionally include unnecessary preambles without runtime filtering.
- Code generation should always be tested; AST parsing verifies syntax but not runtime logic.
- Runtime guards reduce predictable errors but do not guarantee complete safety.

---

## Future Directions

- **Direct Preference Optimization (DPO)**: Applying pair-wise preference tuning (Chosen vs. Rejected) specifically targeting residual formatting artifacts.
- **Scaling to 8B**: Migrating the curated dataset to higher-capacity base models (e.g. Qwen 2.5 7B/14B or Llama 3.1 8B) for deeper multi-turn coding and scientific reasoning.
- **Automated Regression CI/CD**: Integrating the 500-prompt benchmark into an automated evaluation pipeline.

---

## Related Project

The fine-tuned model developed here serves as the neural core for the broader **Kaitu Personal Assistant**:
- 🔗 **Main Assistant Codebase**: [**https://github.com/kunal0040/Kaitu**](https://github.com/kunal0040/Kaitu)

---

## License

This project is licensed under the [MIT License](LICENSE).
