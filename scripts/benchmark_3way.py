"""
3-Way Model Benchmark Runner for Ollama.
Evaluates 200 curated real-life prompts across three models:
1. phi4-mini:latest (OG Baseline)
2. kaitu-v1:latest (Fine-Tuned V1 - Version #14)
3. kaitu-phi4-mini:latest (Fine-Tuned V2 - Version #15)

Features:
- Incremental autosave after each response (crash-proof)
- Resume capability: skips already evaluated prompts
- Real-time latency, token count, and tokens/sec profiling
"""

import json
import os
import sys
import time
import argparse
import requests
from tqdm import tqdm

OLLAMA_URL = "http://localhost:11434/api/chat"

def run_benchmark(model_name, prompts, output_path, limit=None, fresh=False):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Load existing results if resuming
    results = []
    completed_ids = set()
    if os.path.exists(output_path) and not fresh:
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                results = json.load(f)
            completed_ids = {r["id"] for r in results if "id" in r and r.get("response")}
            print(f"[*] Resuming {model_name}: Found {len(completed_ids)} already completed prompts.")
        except Exception as e:
            print(f"[!] Warning reading existing results: {e}. Starting fresh.")
            results = []
            completed_ids = set()

    prompts_to_run = [p for p in prompts if p["id"] not in completed_ids]
    if limit is not None:
        prompts_to_run = prompts_to_run[:limit]

    print(f"\n=======================================================")
    print(f" Running Benchmark for: {model_name}")
    print(f" Total prompts to evaluate: {len(prompts_to_run)} (Total dataset: {len(prompts)})")
    print(f" Output target: {output_path}")
    print(f"=======================================================\n")

    for item in tqdm(prompts_to_run, desc=f"Evaluating {model_name}"):
        pid = item["id"]
        cat = item.get("category", "general")
        prompt = item["prompt"]
        
        t0 = time.time()
        err_msg = None
        resp_text = ""
        eval_count = 0
        eval_duration = 0
        tok_per_sec = 0.0

        try:
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "keep_alive": -1,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.8
                }
            }
            # Robust retry with 180s timeout
            for attempt in range(2):
                try:
                    r = requests.post(OLLAMA_URL, json=payload, timeout=180)
                    break
                except requests.exceptions.Timeout:
                    if attempt == 1:
                        raise
                    time.sleep(2)
            elapsed = round(time.time() - t0, 3)
            
            if r.status_code == 200:
                data = r.json()
                resp_text = data.get("message", {}).get("content", "").strip()
                eval_count = data.get("eval_count", 0)
                eval_duration = data.get("eval_duration", 0)
                if eval_duration > 0:
                    tok_per_sec = round(eval_count / (eval_duration / 1e9), 1)
            else:
                elapsed = round(time.time() - t0, 3)
                err_msg = f"HTTP {r.status_code}: {r.text}"
                resp_text = f"ERROR: {err_msg}"
        except Exception as e:
            elapsed = round(time.time() - t0, 3)
            err_msg = str(e)
            resp_text = f"ERROR: {err_msg}"

        result_entry = {
            "id": pid,
            "category": cat,
            "prompt": prompt,
            "response": resp_text,
            "time_seconds": elapsed,
            "eval_count": eval_count,
            "tokens_per_second": tok_per_sec,
            "error": err_msg
        }

        results.append(result_entry)

        # Autosave after each prompt to ensure zero progress loss
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"[+] Successfully finished {len(results)} prompts for {model_name} -> {output_path}")
    return results

def main():
    parser = argparse.ArgumentParser(description="Run 3-way Phi benchmark on Ollama")
    parser.add_argument("--model", type=str, help="Specific model name (or 'all')", default="all")
    parser.add_argument("--prompts", type=str, default="data/benchmarks/eval_200_prompts.json")
    parser.add_argument("--output", type=str, default=None, help="Custom output json path")
    parser.add_argument("--fresh", action="store_true", help="Overwrite existing output without resuming")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of prompts")
    args = parser.parse_args()

    with open(args.prompts, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    model_configs = [
        {
            "name": "phi4-mini:latest",
            "output": "results/benchmarks/phi4_mini_og_200.json"
        },
        {
            "name": "kaitu-v1:latest",
            "output": "results/benchmarks/kaitu_v1_200.json"
        },
        {
            "name": "kaitu-phi4-mini:latest",
            "output": "results/benchmarks/kaitu_v2_200.json"
        },
        {
            "name": "kaitu-v3:latest",
            "output": "results/benchmarks/kaitu_v3_200.json"
        },
        {
            "name": "kaitu-v4:latest",
            "output": "results/benchmarks/kaitu_v4_200.json"
        },
        {
            "name": "kaitu-v5:latest",
            "output": "results/benchmarks/kaitu_v5_300.json"
        }
    ]

    if args.model != "all":
        target_cfg = next((c for c in model_configs if c["name"] == args.model or args.model in c["name"]), None)
        if not target_cfg:
            target_cfg = {
                "name": args.model,
                "output": f"results/benchmarks/{args.model.replace(':', '_')}_200.json"
            }
        out_path = args.output if args.output else target_cfg["output"]
        run_benchmark(target_cfg["name"], prompts, out_path, limit=args.limit, fresh=args.fresh)
    else:
        for cfg in model_configs:
            run_benchmark(cfg["name"], prompts, cfg["output"], limit=args.limit, fresh=args.fresh)

if __name__ == "__main__":
    main()
