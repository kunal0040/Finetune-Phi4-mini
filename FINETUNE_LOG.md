# Kaitu AI: Complete Fine-Tuning & Regression Audit Log (V1 – V8)

> **Current Production Model**: `phi4:mini-kaitu`  
> **Base Weights**: `kaitu-v6-q4_k_m.gguf` (`2.49 GB`, SHA256 layer `sha256:a0195ddb4b7a...`)  
> **Ollama Model ID**: `26094ad60b87`  
> **Model Path**: `D:\Ollama\kaitu-v6-q4_k_m.gguf`  
> **Host Environment**: Dual NVIDIA Tesla T4 (Kaggle Cloud) $\rightarrow$ Local Ollama on Windows

---

## 1. Executive Summary & Production Decision

After eight iterations of dataset engineering, QLoRA fine-tuning, GGUF quantization, and hand-graded benchmarking across 300+ prompts, **Version 6 (V6)** emerged as the most well-balanced, capable, and natural daily-driver assistant for a 3.8B parameter architecture.

### Why Retraining Hit Diminishing Returns (V7 & V8 Findings)
Attempts to patch V6's remaining quirks via further SFT rounds (V7 and V8) triggered the classic capacity boundary of small parameter models (~3.8B):
- **Identity Inversion**: Small models overfit to high-frequency tokens like "Kaitu" and "Kunal", flipping who is the user and who is the assistant (`"Your name is Kaitu"`, `"You built me, Kunal"`).
- **Format Contamination**: Heavy math formatting (`Answer: ...` and `Step 1/Step 2`) bled into casual conversation, writing, and debugging.
- **Seesaw Regressions**: Fixing one edge case (e.g. strict list termination) nudged others into regression (e.g. math discount formulas or newly invented commands).

### The Production Solution: V6 + Runtime Add-On Suite
Rather than continually degrading the base weights through iterative SFT, the optimal production architecture pairs **`phi4:mini-kaitu` (V6)** with lightweight, deterministic Python runtime guards (`scripts/kaitu_safety_and_guard.py`):
1. **`KaituOutputCleaner`**: Strips stray `Answer:` / `Step` headers and replaces assistant-name email signatures with `[Your Name]`.
2. **`KaituCommandGuard`**: Intercepts dangerous CLI suggestions (`git push -f`, `rm -rf`, fake PostgreSQL `ROLLBACK`).
3. **`KaituCodeValidator`**: Validates all generated Python code blocks via `ast.parse`.
4. **`KaituCalculator`**: Exact deterministic calculation for percentages, compound growth, and bill splits.
5. **`KaituMemory`**: Dynamically injects user and assistant identity into the system prompt at runtime.

---

## 2. Iteration History & Comparative Scorecard

All scores are based on hand-graded evaluations on the shared 200 benchmark prompts and 100 new everyday/math prompts:

| Category | V4 (200) | V5 (300) | V5_fixed (300) | **V6 (Selected Baseline)** | V7 (300) | V8 (300) |
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

## 3. Detailed Version Breakdown

### Version 4 (Initial Success)
- **Strengths**: Strong deep technical, architecture, and coding knowledge. High refusal accuracy on ungrounded claims.
- **Failures**: Third-person name leaks everywhere (`"Kunal's personal AI"`). Narrow scope; lacked everyday conversation, casual writing, and practical word math.

### Version 5 & V5_fixed (The Regression and Recovery)
- **V5 Flaws**: Suffered from tokenizer delimiter issues and synthetic self-dialogue (`Kunal:` / `AI:` labels in completions).
- **V5_fixed**: Cleared self-dialogue and repaired basic math (bat/ball, tips, speed). Still had 37 third-person name leaks and factual hallucination bugs (Cassandra vs CockroachDB CAP theorem inverted, onion enzyme invented as "presenilin").

### Version 6 (The Sweet Spot — Deployed as `phi4:mini-kaitu`)
- **Key Fixes**:
  - Completely purged third-person name leaks (dropped from 37 to 0).
  - Strong natural conversational tone with warm second-person address.
  - Math substantially improved: bat & ball ($0.05), tip on $85 ($15.30), average speed (40 mph), discount stacking (28%), tailwind (550 mph), sock drawer (3 socks), jug puzzle (4 gallons).
  - Real literature recommendations (*The Martian*, *Big Magic*, *Sapiens*).
  - Architecture answers became the strongest of any version (~17/20).
- **Residual Flaws (Addressed via Runtime Guards)**:
  - Leaked trailing `Answer: ...` and `Step 1/Step 2` in ~45 non-math explanations.
  - Occasional runaway list loop on prompt #45 (5 programming languages).
  - Signed sample emails as "Kaitu" instead of "[Your Name]".
  - Advised `git push -f` for non-fast-forward divergence on prompt #86.

### Version 7 & Version 8 (Overfitting & Degradation)
- **What Went Wrong**:
  - Overfitting on identity data caused the model to confuse roles (referring to the user as Kaitu, or referring to itself as Kunal).
  - Fabricated new advice (#194 recommending `DROP TABLE IF EXISTS` after accidental drop; #94 recommending `rm -rf ~/envs/*`).
  - V8 developed doubled periods (`..`) at the end of ~60 answers due to delimiter mismatches.
- **Conclusion**: Validated the decision to halt SFT on 3.8B weights and ship V6 with deterministic guards.

---

## 4. Hardware & Cloud Training Pipeline

### Local Constraint
- Laptop: ASUS TUF A15 (AMD Ryzen 7, 16 GB RAM, NVIDIA RTX 2050 4 GB VRAM).
- WDDM overhead leaves ~2.9 GB usable VRAM—insufficient for 4-bit backpropagation (needs ~4.5–5.0 GB).
- All training was offloaded to free cloud GPUs (Dual Tesla T4 on Kaggle).

### Kaggle Workflow Discoveries & Optimizations
1. **Interactive Session Bypass**: Batch queue (`kaggle kernels push`) gets delayed 2–4 hours during peak cluster hours. Navigating to `https://www.kaggle.com/code/<user>/<slug>/edit` and clicking **"Run All"** triggers instant execution (<15 seconds).
2. **Payload Gzip Compression**: Raw JSON notebooks exceeding ~1 MB trigger Windows Python socket aborts (`WinError 10053`). Using `gzip.compress` on embedded dataset buffers keeps `.ipynb` size at ~190–220 KB, pushing cleanly every time.
3. **Signed Proxy Download**: Direct download URLs from Kaggle's Jupyter proxy (`https://kkb-production.jupyter-proxy.kaggle.net/k/.../proxy/files/<model>.gguf`) stream at ~7–9 MB/s directly into `D:\Ollama\`.

---

## 5. Storage State & Cleanup Verification

To keep disk usage clean and prevent bloat, all non-V6 models and temporary weights were permanently deleted:

- **Active GGUF**: `D:\Ollama\kaitu-v6-q4_k_m.gguf` (`2,493,840,288 bytes`)
- **Active Modelfile**: `D:\Ollama\Modelfile_v6`
- **Ollama Models**:
  - `phi4:mini-kaitu` (Active Daily Driver)
  - `huihui_ai/qwen3-abliterated:8b` (Local 8B fallback)
- **Deleted Artifacts**: V1, V3, V4, V5, V7, V8 GGUFs and all intermediate `.tmp` files.
- **Protected Boundaries**: `D:\Python\Kaitu`, Desktop, and Downloads were strictly untouched.

---

## 6. How to Chat with Kaitu

### 1. In Antigravity (This Chat)
The workspace skill `.agents/skills/kaitu/SKILL.md` is active. Simply run or ask:
```powershell
python scripts/bridge_kaitu.py "your message here"
```
The bridge automatically routes your prompt through `phi4:mini-kaitu` on Ollama and filters the output through `KaituOutputCleaner` and `KaituCommandGuard`.

### 2. Standalone Ollama CLI
```powershell
ollama run phi4:mini-kaitu
```

### 3. Local OpenAI-Compatible API
- URL: `http://localhost:11434/v1/chat/completions`
- Model: `phi4:mini-kaitu`

---

## 7. Future Resumption Guide (If Fine-Tuning Again)

If you decide to revisit fine-tuning in the future:
1. **Do NOT run full SFT retraining from scratch**: Retraining on raw dataset rewrites weights unpredictably.
2. **Use Direct Preference Optimization (DPO)**: Start directly from `phi4:mini-kaitu` (V6) weights and train a small pair-preference dataset (Chosen vs Rejected) targeting only the specific flaws:
   - *Chosen*: Clean email ending `[Your Name]` / *Rejected*: Signed `Kaitu`.
   - *Chosen*: `git pull --rebase origin main` / *Rejected*: `git push -f`.
   - *Chosen*: Direct natural explanation / *Rejected*: Trailing `Answer: ...` header.
3. **Or Scale to an 8B Model**: If you need $\ge 85\%$ accuracy across deep scientific reasoning and multi-turn coding, migrate the dataset to **Qwen 2.5 7B/14B** or **Llama 3.1 8B**, which have inherently higher capacity to absorb complex rules without forgetting.
