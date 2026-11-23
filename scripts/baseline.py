"""
Baseline Evaluation Runner & Metric Analyzer
Loads and analyzes the baseline results for original phi4-mini:latest
Evaluates response quality, latency, failure modes, and constraint compliance.
"""

import json
import os
import re
from pathlib import Path


def analyze_results(json_path, label):
    print(f"\n[*] Analyzing baseline: {label} ({json_path})...")
    if not os.path.exists(json_path):
        print(f"[-] File not found: {json_path}")
        return None

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_prompts = len(data)
    total_time = sum(item.get("time_seconds", 0) for item in data)
    avg_latency = round(total_time / total_prompts, 2) if total_prompts else 0

    waiting_count = 0
    refusal_count = 0
    empty_count = 0
    word_counts = []

    for item in data:
        resp = item.get("response", "") or ""
        words = len(resp.split())
        word_counts.append(words)

        # Silence / Waiting pattern
        if "waiting for your message" in resp.lower():
            waiting_count += 1

        # Refusal patterns
        if any(phrase in resp.lower() for phrase in [
            "sorry, i can't assist", "i can't assist with that",
            "i'm afraid i can't", "i'm sorry, but i can't", "sorry, i can't comply"
        ]):
            refusal_count += 1

        if not resp.strip():
            empty_count += 1

    avg_words = round(sum(word_counts) / len(word_counts), 1) if word_counts else 0

    metrics = {
        "dataset_label": label,
        "total_test_cases": total_prompts,
        "avg_latency_seconds": avg_latency,
        "avg_response_words": avg_words,
        "waiting_for_message_rate": f"{waiting_count}/{total_prompts} ({round(waiting_count/total_prompts*100, 1)}%)",
        "refusal_rate": f"{refusal_count}/{total_prompts} ({round(refusal_count/total_prompts*100, 1)}%)",
        "empty_rate": f"{empty_count}/{total_prompts} ({round(empty_count/total_prompts*100, 1)}%)",
    }

    print(json.dumps(metrics, indent=2))
    return metrics


def main():
    os.makedirs("results/baseline", exist_ok=True)
    general_metrics = analyze_results("results/baseline/phi4-mini_general_baseline.json", "phi4-mini General Prompts")
    situations_metrics = analyze_results("results/baseline/phi4-mini_situations_baseline.json", "phi4-mini Situations Prompts")

    summary = {
        "model": "phi4-mini:latest (Original Baseline)",
        "general": general_metrics,
        "situations": situations_metrics,
    }

    out_path = "results/baseline/baseline_metrics_summary.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\n[+] Baseline metrics written to {out_path}")


if __name__ == "__main__":
    main()
