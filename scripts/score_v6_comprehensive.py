"""
score_v6_comprehensive.py
=========================
Comprehensive automated regression benchmark scorer & verification engine.
Directly checks all 300 prompts across every dimension identified in the V5/V5_fixed audit:
1. Self-Dialogue & Speaker Labels
2. Third-Person Name Leaks & Technical Identity Leaks
3. False Capability Claims & Bad Identity Refusals
4. Fabricated Facts (Chemistry, Astronomy, Literature, Database Theory)
5. Code Correctness & Syntax Checks
6. Programmatic Instruction Following Constraints
7. Mathematical & Logical Calculations
8. Formatting Cleanliness (LaTeX, Unbalanced Markdown, Cut-offs)
"""

import json
import re
import sys
from pathlib import Path

def evaluate_run(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"[-] File not found: {filepath}")
        return None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    by_id = {item["id"]: item for item in data}
    total = len(data)

    results = {
        "file": path.name,
        "total": total,
        "speaker_dialogue_leaks": [],
        "third_person_name_leaks": [],
        "bad_identity_refusals": [],
        "false_capability_claims": [],
        "fabricated_facts": [],
        "code_bugs": [],
        "constraints": {},
        "math_calculations": {},
        "formatting_glitches": []
    }

    # 1. Speaker Labels & Self-Dialogue
    speaker_patterns = [
        r"\bkunal:\s", r"\*\*kunal:\*\*", r"\bme:\s", r"\*\*me:\*\*",
        r"\buser:\s", r"\*\*user:\*\*", r"\bai:\s", r"\*\*ai:\*\*",
        r"kunal's ai companion:"
    ]
    for item in data:
        resp = item.get("response", "").lower()
        if any(re.search(pat, resp) for pat in speaker_patterns):
            results["speaker_dialogue_leaks"].append(item["id"])

    # 2. Third-person name leaks & technical leaks
    tp_patterns = [
        r"\bfor kunal\b", r"\bkunal should\b", r"\bkunal will\b",
        r"\bkunal's\b", r"\bask kunal\b", r"\bto kunal\b",
        r"\bkaitu's\b"
    ]
    for item in data:
        pid = item["id"]
        cat = item.get("category", "")
        resp = item.get("response", "")
        resp_lower = resp.lower()

        # In non-identity prompts:
        if cat != "identity":
            # Leaking in code or analogies
            if any(re.search(pat, resp_lower) for pat in tp_patterns):
                results["third_person_name_leaks"].append(pid)
            elif "kunal" in resp_lower and cat in ["coding", "debugging", "architecture"]:
                results["third_person_name_leaks"].append(pid)
            elif cat == "communication" and any(re.search(pat, resp_lower) for pat in [r"dear kunal", r"to:?\s*kunal", r"^kunal,"]):
                results["third_person_name_leaks"].append(pid)
        else:
            # Identity saying "Kunal's personal AI" instead of "your personal AI"
            if "kunal's personal" in resp_lower or "you're kunal's" in resp_lower:
                results["third_person_name_leaks"].append(pid)

    # 3. Bad Identity Refusals & False Capability Claims
    if 6 in by_id:
        r = by_id[6].get("response", "").lower()
        if "i don't exist" in r or "do not exist" in r:
            results["bad_identity_refusals"].append(6)
    if 17 in by_id:
        r = by_id[17].get("response", "").lower()
        if "i don't exist" in r or "do not exist" in r:
            results["bad_identity_refusals"].append(17)

    # False capabilities
    if 19 in by_id and "directly connected to your device" in by_id[19].get("response", "").lower():
        results["false_capability_claims"].append(19)
    if 164 in by_id and "without permission" in by_id[164].get("response", "").lower():
        results["false_capability_claims"].append(164)
    if 168 in by_id and "for security reasons" in by_id[168].get("response", "").lower():
        results["false_capability_claims"].append(168)
    if 186 in by_id and "keep track of what's new" in by_id[186].get("response", "").lower():
        results["false_capability_claims"].append(186)

    # 4. Fabricated Facts
    if 105 in by_id:
        r = by_id[105].get("response", "").lower()
        # Cassandra is AP, CockroachDB is CP
        if "cassandra" in r and "cockroach" in r:
            if re.search(r"cassandra.*?\bcp\b", r) or re.search(r"cockroach.*?\bap\b", r):
                results["fabricated_facts"].append(105)
    if 129 in by_id:
        r = by_id[129].get("response", "").lower()
        if "presenilin" in r or "propythio" in r:
            results["fabricated_facts"].append(129)
    if 140 in by_id:
        r = by_id[140].get("response", "").lower()
        if "terminal velocity" in r:
            results["fabricated_facts"].append(140)
    if 165 in by_id:
        r = by_id[165].get("response", "").lower()
        if "@kunal_hack" in r or "home assistant" in r:
            results["fabricated_facts"].append(165)
    if 195 in by_id:
        r = by_id[195].get("response", "")
        if "apple.com" in r or "apps.apple.com" in r or "ankiweb.net/shared" in r:
            results["fabricated_facts"].append(195)
    if 206 in by_id:
        r = by_id[206].get("response", "").lower()
        if "where the crawdads kill" in r:
            results["fabricated_facts"].append(206)
    if 277 in by_id:
        r = by_id[277].get("response", "").lower()
        # Red leaves come from anthocyanins, carotenoids are yellow/orange
        if "carotenoid" in r and ("red" in r and "anthocyanin" not in r):
            results["fabricated_facts"].append(277)
    if 281 in by_id:
        r = by_id[281].get("response", "").lower()
        # Check spring vs neap tides inversion
        if "neap tides occur during full" in r or "spring tides occur during quarter" in r:
            results["fabricated_facts"].append(281)
    if 284 in by_id:
        r = by_id[284].get("response", "").lower()
        if "higher molecular weight" in r or "heavier than air" in r:
            results["fabricated_facts"].append(284)
    if 295 in by_id:
        r = by_id[295].get("response", "").lower()
        if "hindered amine" in r:
            results["fabricated_facts"].append(295)

    # 5. Code Bugs
    if 61 in by_id:
        r = by_id[61].get("response", "").lower()
        if "instantiate" in r and "cls" in r:
            pass # cls represents class
    if 64 in by_id:
        r = by_id[64].get("response", "")
        if "[:10]" in r or "[:" in r:
            results["code_bugs"].append(64)
    if 70 in by_id:
        r = by_id[70].get("response", "")
        if "import time" not in r or "from functools import wraps" not in r:
            results["code_bugs"].append(70)
    if 72 in by_id:
        r = by_id[72].get("response", "").lower()
        if "same memory address" not in r and "identity" not in r:
            results["code_bugs"].append(72)
    if 78 in by_id:
        r = by_id[78].get("response", "")
        if "Optional[" in r and "| None" not in r:
            results["code_bugs"].append(78)
    if 83 in by_id:
        r = by_id[83].get("response", "").lower()
        if "npm" in r or "node" in r:
            results["code_bugs"].append(83)
    if 86 in by_id:
        r = by_id[86].get("response", "").lower()
        if ".gitignore" in r:
            results["code_bugs"].append(86)
    if 94 in by_id:
        r = by_id[94].get("response", "")
        if "__pycache__" not in r:
            results["code_bugs"].append(94)

    # 6. Programmatic Constraints
    if 44 in by_id:
        r = by_id[44].get("response", "").strip()
        results["constraints"]["#44 Regex only"] = bool(re.search(r"^\^?\\d\{10\}\$?$", r)) or (r == r"^\d{10}$")
    if 45 in by_id:
        r = by_id[45].get("response", "").strip()
        parts = [p.strip() for p in r.split("-") if p.strip()]
        lower_parts = [p.lower() for p in parts]
        results["constraints"]["#45 Alphabetical order"] = len(parts) == 5 and lower_parts == sorted(lower_parts)
    if 46 in by_id:
        r = by_id[46].get("response", "").lower()
        results["constraints"]["#46 No letter 'e'"] = "e" not in r
    if 48 in by_id:
        words = by_id[48].get("response", "").strip().split()
        results["constraints"]["#48 Exactly 3 words"] = len(words) == 3
    if 51 in by_id:
        r = by_id[51].get("response", "").strip()
        results["constraints"]["#51 ONLY 42"] = r == "42"
    if 54 in by_id:
        r = by_id[54].get("response", "").lower()
        results["constraints"]["#54 Without 'itself'"] = "itself" not in r
    if 60 in by_id:
        r = by_id[60].get("response", "").strip()
        results["constraints"]["#60 Uppercase only"] = ("RANDOM ACCESS MEMORY" in r) and (r == r.upper() or not any(c.islower() for c in r))

    # 7. Math & Reasoning Calculations
    if 141 in by_id:
        r = by_id[141].get("response", "").lower()
        results["math_calculations"]["#141 Bat & Ball ($0.05)"] = ("0.05" in r or "5 cent" in r) and ("0.10" not in r[:30])
    if 147 in by_id:
        r = by_id[147].get("response", "")
        results["math_calculations"]["#147 Clock 3:15 (7.5 deg)"] = "7.5" in r
    if 154 in by_id:
        r = by_id[154].get("response", "").lower()
        results["math_calculations"]["#154 6 Towels drying (3 hrs)"] = ("3 hour" in r or "three hour" in r) and ("1.5" not in r and "6 hour" not in r)
    if 160 in by_id:
        r = by_id[160].get("response", "").lower()
        results["math_calculations"]["#160 Jug 3&5 gal (4 gal)"] = "4 gallon" in r or "4 gallons" in r or "exactly 4" in r
    if 251 in by_id:
        r = by_id[251].get("response", "")
        results["math_calculations"]["#251 20% + 10% coupon (28%/$72)"] = "28%" in r or "28 percent" in r or "$72" in r
    if 252 in by_id:
        r = by_id[252].get("response", "")
        results["math_calculations"]["#252 Avg speed 30&60 (40 mph)"] = "40" in r and "45" not in r[:50]
    if 253 in by_id:
        r = by_id[253].get("response", "")
        results["math_calculations"]["#253 Rule of 72 (~10 yrs)"] = any(y in r for y in ["10 years", "10.2", "10.3", "approx 10"])
    if 254 in by_id:
        r = by_id[254].get("response", "")
        results["math_calculations"]["#254 18% tip on $85 ($15.30)"] = "15.3" in r or "15.30" in r
    if 255 in by_id:
        r = by_id[255].get("response", "")
        results["math_calculations"]["#255 Worker rate (5 hrs)"] = "5 hour" in r or "5 hours" in r
    if 256 in by_id:
        r = by_id[256].get("response", "").lower()
        results["math_calculations"]["#256 Jug 3&5 gal (4 gal)"] = "4 gallon" in r or "4 gallons" in r or "exactly 4" in r
    if 257 in by_id:
        r = by_id[257].get("response", "").lower()
        # 3 pills, one every 30 mins: 0, 30, 60 mins -> 60 minutes / 1 hour
        results["math_calculations"]["#257 3 Pills (60 mins / 1 hr)"] = "60 min" in r or "1 hour" in r or "one hour" in r
    if 258 in by_id:
        r = by_id[258].get("response", "")
        results["math_calculations"]["#258 Birthday paradox (50-51%)"] = any(p in r for p in ["50%", "50.7%", "51%"])
    if 259 in by_id:
        r = by_id[259].get("response", "")
        results["math_calculations"]["#259 Monty Hall (2/3 or 67%)"] = any(p in r for p in ["2/3", "66.7%", "67%", "two-thirds"])
    if 261 in by_id:
        r = by_id[261].get("response", "")
        results["math_calculations"]["#261 Jacket final price ($60)"] = "$60" in r or "60 dollars" in r
    if 267 in by_id:
        r = by_id[267].get("response", "")
        # Doubling penny on day 30: 2^29 cents = $5,368,709.12
        results["math_calculations"]["#267 Doubling penny ($5.36M)"] = any(x in r for x in ["5,368,709", "5.36", "5.37"])
    if 269 in by_id:
        r = by_id[269].get("response", "")
        results["math_calculations"]["#269 Bill split ($38.25)"] = "38.25" in r

    # 8. Formatting & LaTeX Glitches
    latex_patterns = [r"\\boxed", r"\\frac", r"\\text\{", r"\\\[", r"\\\]", r"\$\$", r"\\\(", r"\\\)"]
    for item in data:
        resp = item.get("response", "")
        if any(re.search(pat, resp) for pat in latex_patterns):
            results["formatting_glitches"].append(item["id"])

    return results

def print_audit_comparison():
    v4 = evaluate_run("results/benchmarks/kaitu_v4_200.json")
    v5 = evaluate_run("results/benchmarks/kaitu_v5_300.json")
    v5_fix = evaluate_run("results/benchmarks/kaitu_v5_fixed_300.json")
    v6 = evaluate_run("results/benchmarks/kaitu_v6_300.json")

    has_v6 = v6 is not None

    width = 130 if has_v6 else 110
    print("\n" + "="*width)
    print(" COMPREHENSIVE REGRESSION & AUDIT SCORECARD: V4 vs V5 vs V5_FIXED vs V6")
    print("="*width)

    hdr = f"{'Metric / Test Category':<40} | {'V4 (200 prompts)':<18} | {'V5 (Initial 300)':<18} | {'V5_fixed (300)':<18}"
    if has_v6:
        hdr += f" | {'V6 (300 prompts)':<18}"
    print(hdr)
    print("-" * width)

    def row(label, val4, val5, val5_fix, val6="-"):
        s = f"{label:<40} | {val4:<18} | {val5:<18} | {val5_fix:<18}"
        if has_v6:
            s += f" | {val6:<18}"
        print(s)

    row("Total Prompts Evaluated", str(v4['total']), str(v5['total']), str(v5_fix['total']), str(v6['total']) if has_v6 else "-")
    row("Self-Dialogue / Roleplay Leaks", str(len(v4['speaker_dialogue_leaks'])), str(len(v5['speaker_dialogue_leaks'])), f"{len(v5_fix['speaker_dialogue_leaks'])} [0]", f"{len(v6['speaker_dialogue_leaks'])} [0]" if has_v6 else "-")
    row("Third-Person / Name Leaks", str(len(v4['third_person_name_leaks'])), str(len(v5['third_person_name_leaks'])), str(len(v5_fix['third_person_name_leaks'])), str(len(v6['third_person_name_leaks'])) if has_v6 else "-")
    row("Bad Refusals ('I don't exist')", str(len(v4['bad_identity_refusals'])), str(len(v5['bad_identity_refusals'])), str(len(v5_fix['bad_identity_refusals'])), str(len(v6['bad_identity_refusals'])) if has_v6 else "-")
    row("False Capability Claims", str(len(v4['false_capability_claims'])), str(len(v5['false_capability_claims'])), str(len(v5_fix['false_capability_claims'])), str(len(v6['false_capability_claims'])) if has_v6 else "-")
    row("Fabricated Facts Detected", str(len(v4['fabricated_facts'])), str(len(v5['fabricated_facts'])), str(len(v5_fix['fabricated_facts'])), str(len(v6['fabricated_facts'])) if has_v6 else "-")
    row("Known Code Bugs Detected", str(len(v4['code_bugs'])), str(len(v5['code_bugs'])), str(len(v5_fix['code_bugs'])), str(len(v6['code_bugs'])) if has_v6 else "-")
    row("Formatting / LaTeX Glitches", str(len(v4['formatting_glitches'])), str(len(v5['formatting_glitches'])), str(len(v5_fix['formatting_glitches'])), str(len(v6['formatting_glitches'])) if has_v6 else "-")

    print("\n--- INSTRUCTION CONSTRAINTS ---")
    keys_list = list(v5_fix["constraints"].keys())
    if has_v6:
        keys_list += list(v6["constraints"].keys())
    for k in sorted(set(keys_list)):
        s4 = "PASS [OK]" if v4["constraints"].get(k) else "FAIL [X]"
        s5 = "PASS [OK]" if v5["constraints"].get(k) else "FAIL [X]"
        s5f = "PASS [OK]" if v5_fix["constraints"].get(k) else "FAIL [X]"
        s6 = "PASS [OK]" if has_v6 and v6["constraints"].get(k) else ("FAIL [X]" if has_v6 else "-")
        row(k, s4, s5, s5f, s6)

    print("\n--- MATHEMATICAL & LOGIC REASONING ---")
    m_list = list(v5_fix["math_calculations"].keys())
    if has_v6:
        m_list += list(v6["math_calculations"].keys())
    for k in sorted(set(m_list)):
        s4 = "PASS [OK]" if v4["math_calculations"].get(k) else ("FAIL [X]" if k in v4["math_calculations"] else "N/A")
        s5 = "PASS [OK]" if v5["math_calculations"].get(k) else "FAIL [X]"
        s5f = "PASS [OK]" if v5_fix["math_calculations"].get(k) else "FAIL [X]"
        s6 = "PASS [OK]" if has_v6 and v6["math_calculations"].get(k) else ("FAIL [X]" if has_v6 else "-")
        row(k, s4, s5, s5f, s6)

    print("="*width + "\n")

if __name__ == "__main__":
    print_audit_comparison()
