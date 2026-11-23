"""
Benchmark Fine-Tuned Model against Baseline Prompts.
Runs all prompts from the baseline benchmark against kaitu-phi4-mini,
records latency, token outputs, and responses, and writes output files.
"""

import json
import os
import time
import requests
from tqdm import tqdm

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "kaitu-phi4-mini"

def run_benchmark(input_json, output_json, label):
    print(f"\n[*] Running benchmark: {label} ({len(input_json)} prompts)...")
    results = []

    for item in tqdm(input_json, desc=label):
        q = item["question"]
        t0 = time.time()
        try:
            r = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "messages": [{"role": "user", "content": q}],
                    "stream": False,
                    "options": {"temperature": 0.3, "top_p": 0.8}
                },
                timeout=60
            )
            elapsed = round(time.time() - t0, 3)
            data = r.json()
            resp = data.get("message", {}).get("content", "").strip()
            eval_count = data.get("eval_count", 0)
            eval_duration = data.get("eval_duration", 0)
            tok_per_sec = round(eval_count / (eval_duration / 1e9), 1) if eval_duration > 0 else 0
        except Exception as e:
            elapsed = round(time.time() - t0, 3)
            resp = f"ERROR: {e}"
            tok_per_sec = 0

        results.append({
            "question": q,
            "response": resp,
            "time_seconds": elapsed,
            "tokens_per_second": tok_per_sec
        })

    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"[+] Saved {len(results)} results to {output_json}")
    return results

def main():
    with open("results/baseline/phi4-mini_general_baseline.json", "r", encoding="utf-8") as f:
        gen_data = json.load(f)

    with open("results/baseline/phi4-mini_situations_baseline.json", "r", encoding="utf-8") as f:
        sit_data = json.load(f)

    gen_out = "results/finetuned/kaitu_general_finetuned.json"
    sit_out = "results/finetuned/kaitu_situations_finetuned.json"

    run_benchmark(gen_data, gen_out, "General Prompts")
    run_benchmark(sit_data, sit_out, "Situational Prompts")

if __name__ == "__main__":
    main()
