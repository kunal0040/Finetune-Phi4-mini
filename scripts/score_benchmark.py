"""
score_benchmark.py
==================
Automated regression scorer for Kaitu benchmarks.
Evaluates benchmark JSON files programmatically across:
1. Self-Dialogue / Speaker Labels (Kunal:, User:, Me:, AI:)
2. Third-person name leaks and technical name leaks
3. Raw LaTeX / Math formatting garbage (\\boxed, \\frac, $$, \\[, \\text)
4. Programmatic constraint passes (ONLY 42, 3 words, no 'e', RAM uppercase, regex, alphabetical)
5. Numeric accuracy on mathematical & practical reasoning puzzles
6. Generates a comparative scorecard.
"""

import json
import os
import re
import sys
from pathlib import Path

def score_file(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"[-] File not found: {filepath}")
        return None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_prompts = len(data)
    by_id = {x.get("id"): x for x in data}

    # 1. Speaker Labels / Self-dialogue
    speaker_patterns = [
        r"\bkunal:\s", r"\*\*kunal:\*\*", r"\bme:\s", r"\*\*me:\*\*",
        r"\buser:\s", r"\*\*user:\*\*", r"\bai:\s", r"\*\*ai:\*\*",
        r"kunal's ai companion:"
    ]
    self_dialogue_count = 0
    dialogue_ids = []
    for item in data:
        resp = item.get("response", "").lower()
        if any(re.search(pat, resp) for pat in speaker_patterns):
            self_dialogue_count += 1
            dialogue_ids.append(item.get("id"))

    # 2. Name leaks: "Kunal" in 3rd person or in technical/code/emails
    third_person_patterns = [
        r"\bfor kunal\b", r"\bkunal should\b", r"\bkunal will\b",
        r"\bkunal's\b", r"\bask kunal\b", r"\bto kunal\b"
    ]
    name_leak_count = 0
    name_leak_ids = []
    for item in data:
        pid = item.get("id")
        cat = item.get("category", "")
        resp = item.get("response", "").lower()
        
        # In non-identity prompts, check for third-person usage or technical code leaks
        if cat != "identity":
            if any(re.search(pat, resp) for pat in third_person_patterns) or ("kunal" in resp and cat in ["coding", "debugging", "architecture"]):
                name_leak_count += 1
                name_leak_ids.append(pid)

    # 3. Raw LaTeX / Math formatting glitches
    latex_patterns = [r"\\boxed", r"\\frac", r"\\text\{", r"\\\[", r"\\\]", r"\$\$"]
    latex_glitch_count = 0
    latex_ids = []
    for item in data:
        resp = item.get("response", "")
        if any(re.search(pat, resp) for pat in latex_patterns):
            latex_glitch_count += 1
            latex_ids.append(item.get("id"))

    # 4. Programmatic Constraint Checks
    constraint_results = {}
    
    # ID #44: Regex only for 10-digit phone
    if 44 in by_id:
        r = by_id[44].get("response", "").strip()
        constraint_results["#44 (10-digit regex only)"] = bool(re.search(r"^\^?\\d\{10\}\$?$", r)) or (r == r"^\d{10}$")

    # ID #45: Alphabetical 5 languages with hyphens
    if 45 in by_id:
        r = by_id[45].get("response", "").strip()
        parts = [p.strip() for p in r.split("-") if p.strip()]
        lower_parts = [p.lower() for p in parts]
        constraint_results["#45 (Alphabetical order)"] = len(parts) == 5 and lower_parts == sorted(lower_parts)

    # ID #46: No letter 'e'
    if 46 in by_id:
        r = by_id[46].get("response", "").lower()
        constraint_results["#46 (No letter 'e')"] = "e" not in r

    # ID #48: Exactly 3 words
    if 48 in by_id:
        words = by_id[48].get("response", "").strip().split()
        constraint_results["#48 (Exactly 3 words)"] = len(words) == 3

    # ID #51: ONLY 42
    if 51 in by_id:
        r = by_id[51].get("response", "").strip()
        constraint_results["#51 (ONLY 42)"] = r == "42"

    # ID #54: Without word 'itself'
    if 54 in by_id:
        r = by_id[54].get("response", "").lower()
        constraint_results["#54 (Without 'itself')"] = "itself" not in r

    # ID #60: RAM uppercase only
    if 60 in by_id:
        r = by_id[60].get("response", "").strip()
        constraint_results["#60 (RAM uppercase only)"] = ("RANDOM ACCESS MEMORY" in r) and (r == r.upper() or not any(c.islower() for c in r))

    # 5. Numeric / Mathematical Reasoning Checks
    math_results = {}

    # ID #141: Bat and ball ($0.05 or 5 cents)
    if 141 in by_id:
        r = by_id[141].get("response", "").lower()
        math_results["#141 (Bat & Ball: $0.05)"] = ("0.05" in r or "5 cent" in r) and ("0.10" not in r[:30])

    # ID #147: Clock 3:15 (7.5 degrees)
    if 147 in by_id:
        r = by_id[147].get("response", "")
        math_results["#147 (Clock 3:15: 7.5 deg)"] = "7.5" in r

    # ID #154: 6 towels drying in sun (3 hours)
    if 154 in by_id:
        r = by_id[154].get("response", "").lower()
        math_results["#154 (Towels: 3 hours)"] = ("3 hour" in r or "three hour" in r) and ("1.5" not in r and "6 hour" not in r)

    # ID #251: 20% discount + 10% coupon = 28%
    if 251 in by_id:
        r = by_id[251].get("response", "")
        math_results["#251 (20% + 10% = 28%)"] = "28%" in r or "28 percent" in r or "$72" in r

    # ID #252: Average speed 30 mph + 60 mph = 40 mph
    if 252 in by_id:
        r = by_id[252].get("response", "")
        math_results["#252 (Avg speed: 40 mph)"] = "40" in r and "45" not in r[:50]

    # ID #253: $1000 at 7% compound = ~10 years
    if 253 in by_id:
        r = by_id[253].get("response", "")
        math_results["#253 (Rule of 72: ~10 years)"] = any(y in r for y in ["10 years", "10.2", "10.3", "approx 10"])

    # ID #254: 18% tip on $85 = $15.30
    if 254 in by_id:
        r = by_id[254].get("response", "")
        math_results["#254 (18% tip on $85: $15.30)"] = "15.3" in r or "15.30" in r

    # ID #255: 5 workers 5 birdhouses in 5 hours -> 1 worker = 5 hours
    if 255 in by_id:
        r = by_id[255].get("response", "")
        math_results["#255 (Worker rate: 5 hours)"] = "5 hour" in r or "5 hours" in r

    # ID #258: Birthday paradox (23 people: ~50.7% / 51%)
    if 258 in by_id:
        r = by_id[258].get("response", "")
        math_results["#258 (Birthday: ~50-51%)"] = any(p in r for p in ["50%", "50.7%", "51%"])

    # ID #259: Monty Hall (2/3 or 66.7%)
    if 259 in by_id:
        r = by_id[259].get("response", "")
        math_results["#259 (Monty Hall: 2/3 or 67%)"] = any(p in r for p in ["2/3", "66.7%", "67%", "two-thirds"])

    # ID #261: Jacket $50 + 50% markup - 20% sale = $60
    if 261 in by_id:
        r = by_id[261].get("response", "")
        math_results["#261 (Jacket final price: $60)"] = "$60" in r or "60 dollars" in r

    # ID #269: $114.75 split 3 ways = $38.25
    if 269 in by_id:
        r = by_id[269].get("response", "")
        math_results["#269 (Bill split: $38.25)"] = "38.25" in r

    return {
        "filename": path.name,
        "total_prompts": total_prompts,
        "self_dialogue_count": self_dialogue_count,
        "name_leak_count": name_leak_count,
        "latex_glitch_count": latex_glitch_count,
        "constraint_results": constraint_results,
        "math_results": math_results
    }

def print_comparison():
    v4 = score_file("results/benchmarks/kaitu_v4_200.json")
    v5 = score_file("results/benchmarks/kaitu_v5_300.json")
    v5_fixed = score_file("results/benchmarks/kaitu_v5_fixed_300.json")

    has_fixed = v5_fixed is not None

    print("\n" + "="*105)
    print(" AUTOMATED REGRESSION BENCHMARK SCORECARD: V4 vs V5 vs V5 (Fixed Sampling) ")
    print("="*105)

    hdr = f"{'Metric':<38} | {'V4 (200 prompts)':<18} | {'V5 (Initial)':<18}"
    if has_fixed:
        hdr += f" | {'V5 (Fixed Sampling)':<20}"
    print(hdr)
    print("-" * 105)

    def row(label, val4, val5, val5_fix):
        s = f"{label:<38} | {val4:<18} | {val5:<18}"
        if has_fixed:
            s += f" | {val5_fix:<20}"
        print(s)

    row("Total Prompts Evaluated", str(v4['total_prompts']), str(v5['total_prompts']), str(v5_fixed['total_prompts']) if has_fixed else "-")
    row("Self-Dialogue / Speaker Labels", str(v4['self_dialogue_count']), str(v5['self_dialogue_count']), str(v5_fixed['self_dialogue_count']) if has_fixed else "-")
    row("Third-Person / Technical Name Leaks", str(v4['name_leak_count']), str(v5['name_leak_count']), str(v5_fixed['name_leak_count']) if has_fixed else "-")
    row("Raw LaTeX / Formatting Glitches", str(v4['latex_glitch_count']), str(v5['latex_glitch_count']), str(v5_fixed['latex_glitch_count']) if has_fixed else "-")

    print("\n--- PROGRAMMATIC CONSTRAINT CHECKS ---")
    keys_list = list(v4["constraint_results"].keys()) + list(v5["constraint_results"].keys())
    if has_fixed:
        keys_list += list(v5_fixed["constraint_results"].keys())
    all_constraints = sorted(set(keys_list))
    for c in all_constraints:
        v4_res = "PASS [OK]" if v4["constraint_results"].get(c) else "FAIL [X]"
        v5_res = "PASS [OK]" if v5["constraint_results"].get(c) else "FAIL [X]"
        v5_fix_res = "PASS [OK]" if has_fixed and v5_fixed["constraint_results"].get(c) else ("FAIL [X]" if has_fixed else "-")
        row(c, v4_res, v5_res, v5_fix_res)

    print("\n--- NUMERIC MATHEMATICAL & REASONING CHECKS ---")
    math_keys = list(v4["math_results"].keys()) + list(v5["math_results"].keys())
    if has_fixed:
        math_keys += list(v5_fixed["math_results"].keys())
    all_math = sorted(set(math_keys))
    for m in all_math:
        v4_res = "PASS [OK]" if v4["math_results"].get(m) else ("FAIL [X]" if m in v4["math_results"] else "N/A")
        v5_res = "PASS [OK]" if v5["math_results"].get(m) else "FAIL [X]"
        v5_fix_res = "PASS [OK]" if has_fixed and v5_fixed["math_results"].get(m) else ("FAIL [X]" if has_fixed else "-")
        row(m, v4_res, v5_res, v5_fix_res)
    print("="*105 + "\n")

if __name__ == "__main__":
    print_comparison()
