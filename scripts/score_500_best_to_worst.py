"""
score_500_best_to_worst.py
==========================
Ranks and evaluates all 500 benchmark answers for phi4:mini-kaitu (V6)
from Best (Rank #1) to Worst (Rank #500).
Assesses:
- Mathematical & logical correctness
- Code syntax validity (ast.parse)
- Constraint satisfaction
- Safety & lack of dangerous commands
- Identity & conversational quality
- Clean formatting
"""

import ast
import json
import re
import sys
from pathlib import Path

def score_prompt(item):
    pid = item["id"]
    cat = item.get("category", "general")
    prompt = item["prompt"]
    resp = item.get("response", "")
    resp_l = resp.lower()

    score = 80 # base baseline score
    reasons = []

    # 1. Critical Failures (-50 to -40)
    if "i don't exist" in resp_l:
        score -= 50
        reasons.append("Bad refusal ('I don't exist')")

    if any(pat in resp_l for pat in ["git push -f", "git push --force"]):
        score -= 40
        reasons.append("Recommends dangerous force push")

    if "rm -rf .python" in resp_l or "rm -rf ~/.cache" in resp_l or "rm -rf ~/envs" in resp_l:
        score -= 40
        reasons.append("Recommends destructive environment deletion")

    if "rollback to pg_backup_start_time" in resp_l:
        score -= 40
        reasons.append("Fabricated PostgreSQL rollback command")

    if "presenilin" in resp_l:
        score -= 40
        reasons.append("Fabricated onion tear enzyme")

    if "mechanical energy" in resp_l and cat == "science":
        score -= 30
        reasons.append("Wrong science: claimed microwaves use mechanical energy")

    # 2. Syntax & Code Validation
    if "```python" in resp:
        blocks = re.findall(r"```python\s*(.*?)```", resp, re.DOTALL)
        for code in blocks:
            try:
                ast.parse(code)
                score += 5
                reasons.append("Valid Python AST code block")
            except SyntaxError as e:
                score -= 35
                reasons.append(f"Python syntax error: {e.msg}")

    # 3. Math & Logic Verification
    if pid == 141 or pid == 356: # Bat and ball ($0.05)
        if ("0.05" in resp or "5 cent" in resp) and "0.10" not in resp[:30]:
            score += 15
            reasons.append("Correct Bat & Ball math ($0.05)")
        else:
            score -= 35
            reasons.append("Wrong Bat & Ball math")

    if pid == 147 or pid == 363: # Clock 3:15 (7.5 deg)
        if "7.5" in resp:
            score += 15
            reasons.append("Correct clock angle (7.5°)")
        else:
            score -= 25
            reasons.append("Wrong clock angle")

    if pid == 251: # 28% discount
        if "28%" in resp or "$72" in resp:
            score += 15
            reasons.append("Correct stacked discount (28% / $72)")
        else:
            score -= 25
            reasons.append("Wrong stacked discount")

    if pid == 252 or pid == 368: # Avg speed (40 mph)
        if "40" in resp and "45" not in resp[:40]:
            score += 15
            reasons.append("Correct average speed (40 mph)")
        else:
            score -= 25
            reasons.append("Wrong average speed")

    if pid == 254: # Tip on $85 ($15.30)
        if "15.3" in resp or "15.30" in resp:
            score += 15
            reasons.append("Correct tip calculation ($15.30)")

    if pid == 257: # 3 pills (60 min / 1 hr)
        if "60 min" in resp_l or "1 hour" in resp_l or "one hour" in resp_l:
            score += 15
            reasons.append("Correct pill timing (60 mins / 1 hour)")
        else:
            score -= 25
            reasons.append("Wrong pill timing")

    if pid == 259: # Monty Hall (2/3 or 67%)
        if "2/3" in resp or "67%" in resp or "66.7%" in resp:
            score += 15
            reasons.append("Correct Monty Hall probability (2/3)")

    if pid == 267: # Doubling penny (~$5.37M)
        if "5,368,709" in resp or "5.37" in resp or "5.36" in resp:
            score += 15
            reasons.append("Correct doubling penny calculation")

    # 4. Instruction Following & Constraints
    if pid == 44: # Regex only
        if bool(re.search(r"^\^?\\d\{10\}\$?$", resp.strip())) or resp.strip() == r"^\d{10}$":
            score += 15
            reasons.append("Perfect regex constraint satisfaction")
        else:
            score -= 10

    if pid == 45: # 5 programming languages
        parts = [p.strip() for p in re.split(r"[-–—\n]", resp) if p.strip()]
        if len(parts) > 15:
            score -= 30
            reasons.append("Runaway list degeneration")
        elif len(parts) == 5:
            score += 10
            reasons.append("Exact 5-item list count")

    if pid == 48: # Exactly 3 words
        words = resp.strip().split()
        if len(words) == 3:
            score += 15
            reasons.append("Exact 3-word count constraint")
        else:
            score -= 10
            reasons.append(f"Failed 3-word count ({len(words)} words)")

    if pid == 51: # ONLY 42
        if resp.strip() == "42":
            score += 15
            reasons.append("Exact ONLY 42 constraint")
        else:
            score -= 10

    # 5. Tone & Cleanliness
    if "kunal:" in resp_l or "**kunal:**" in resp_l or "user:" in resp_l:
        score -= 20
        reasons.append("Self-dialogue speaker label leak")

    if "your name is kaitu" in resp_l or "you're kaitu, my creator" in resp_l:
        score -= 25
        reasons.append("Role confusion: flipped user and assistant")

    if cat != "reasoning" and re.search(r"\nAnswer:\s*", resp):
        score -= 10
        reasons.append("Format leak: trailing 'Answer:' in non-math")

    # Bound score between 0 and 100
    score = max(0, min(100, score))

    if score >= 90:
        tier = "Tier S (Flawless)"
    elif score >= 75:
        tier = "Tier A (Solid)"
    elif score >= 55:
        tier = "Tier B (Minor Blemishes)"
    elif score >= 35:
        tier = "Tier C (Flawed)"
    else:
        tier = "Tier F (Failed)"

    return {
        "id": pid,
        "category": cat,
        "prompt": prompt,
        "response": resp,
        "score": score,
        "tier": tier,
        "reasons": reasons
    }

def rank_all_500():
    res_path = Path("results/benchmarks/kaitu_v6_500.json")
    if not res_path.exists():
        print(f"[-] Benchmark file not found: {res_path}")
        return

    with open(res_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"[*] Evaluating and ranking all {len(data)} prompts...")
    evaluated = [score_prompt(item) for item in data]

    # Sort descending by score, then by id
    ranked = sorted(evaluated, key=lambda x: (-x["score"], x["id"]))

    tier_counts = {}
    for r in ranked:
        t = r["tier"]
        tier_counts[t] = tier_counts.get(t, 0) + 1

    print("\n" + "="*80)
    print(" PHI4:MINI-KAITU (V6) 500-PROMPT BENCHMARK RANKING REPORT")
    print("="*80)
    print(f"Total Evaluated: {len(ranked)} prompts\n")

    print("--- QUALITY TIER BREAKDOWN ---")
    for t in ["Tier S (Flawless)", "Tier A (Solid)", "Tier B (Minor Blemishes)", "Tier C (Flawed)", "Tier F (Failed)"]:
        cnt = tier_counts.get(t, 0)
        pct = (cnt / len(ranked)) * 100 if ranked else 0
        print(f"{t:<26} : {cnt:>4} prompts ({pct:>5.1f}%)")

    # Category Average Scores
    cat_scores = {}
    for r in ranked:
        c = r["category"]
        cat_scores.setdefault(c, []).append(r["score"])

    print("\n--- CATEGORY PERFORMANCE SUMMARY ---")
    print(f"{'Category':<24} | {'Count':<8} | {'Avg Score':<10} | {'Status':<15}")
    print("-" * 65)
    for c, scs in sorted(cat_scores.items(), key=lambda x: -sum(x[1])/len(x[1])):
        avg = sum(scs) / len(scs)
        st = "EXCELLENT" if avg >= 85 else ("GOOD" if avg >= 75 else "FAIR")
        print(f"{c:<24} | {len(scs):<8} | {avg:>6.1f}/100 | {st:<15}")

    print("\n--- TOP 10 BEST PROMPTS (Rank #1 - #10) ---")
    for idx, r in enumerate(ranked[:10], 1):
        print(f"Rank #{idx:<2} [ID #{r['id']:<3}] ({r['category']}) Score: {r['score']}/100")
        print(f"Prompt: {r['prompt'][:85]}...")
        print(f"Strength: {', '.join(r['reasons'][:2])}\n")

    print("\n--- BOTTOM 10 WORST PROMPTS (Rank #491 - #500) ---")
    for idx, r in enumerate(ranked[-10:], len(ranked)-9):
        print(f"Rank #{idx:<3} [ID #{r['id']:<3}] ({r['category']}) Score: {r['score']}/100")
        print(f"Prompt: {r['prompt'][:85]}...")
        print(f"Flaw / Reason: {', '.join(r['reasons']) if r['reasons'] else 'Low compliance'}\n")

    # Save full ranking to json
    out_rank = Path("results/benchmarks/v6_500_ranked_best_to_worst.json")
    with open(out_rank, "w", encoding="utf-8") as f:
        json.dump(ranked, f, indent=2, ensure_ascii=False)
    print(f"[+] Full 500 ranked results exported to: {out_rank}")
    print("="*80 + "\n")

if __name__ == "__main__":
    rank_all_500()
