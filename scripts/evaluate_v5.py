"""
evaluate_v5.py - Comprehensive Evaluation of Kaitu V5 (300 prompts)
"""

import json
import re

with open("results/benchmarks/kaitu_v5_300.json", "r", encoding="utf-8") as f:
    v5 = json.load(f)

print(f"Total evaluated prompts: {len(v5)}")

# Identity stats
kaitu_count = sum(1 for item in v5 if "kaitu" in item["response"].lower())
kunal_count = sum(1 for item in v5 if "kunal" in item["response"].lower())
phi_mentions = sum(1 for item in v5 if re.search(r"\b(phi|microsoft)\b", item["response"], re.I))
ai_boilerplate = sum(1 for item in v5 if any(s in item["response"].lower() for s in ["as an ai", "i'm just a language model", "as a language model"]))
lengths = [item.get("eval_count", len(item["response"].split())) for item in v5]
avg_len = sum(lengths) / len(lengths)
empty_count = sum(1 for item in v5 if not item["response"].strip())

print(f"Mentions Kaitu: {kaitu_count}")
print(f"Mentions Kunal: {kunal_count}")
print(f"Mentions Phi / Microsoft: {phi_mentions}")
print(f"Generic 'As an AI' boilerplate: {ai_boilerplate}")
print(f"Avg tokens/eval count: {avg_len:.1f}")
print(f"Empty responses: {empty_count}")

# Check key target prompts
targets = [
    1, 4, 7, 33, 36, 44, 45, 46, 50, 58, 60,
    67, 71, 73, 76, 78, 86, 88, 89, 105,
    125, 126, 129, 131, 132, 141, 147, 154, 167, 179,
    201, 226, 251, 252, 276
]

print("\n" + "="*70)
print(" KEY BENCHMARK PROMPT SPOTLIGHT ")
print("="*70)

by_id = {x["id"]: x for x in v5}
for tid in targets:
    if tid in by_id:
        item = by_id[tid]
        print(f"\n[ID #{item['id']} - {item.get('category')}]")
        print(f"PROMPT: {item['prompt']}")
        print(f"RESPONSE:\n{item['response']}")
        print("-" * 50)
