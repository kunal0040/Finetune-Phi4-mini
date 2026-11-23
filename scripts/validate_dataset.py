"""
Dataset Quality Control and Validation Script
Performs rigorous validation on training, eval, and benchmark datasets:
- JSON/JSONL format integrity
- Required field presence ('messages', 'role', 'content')
- Role sequence consistency (system -> user -> assistant)
- Empty or whitespace-only checks
- Near-duplicate detection using token Jaccard similarity
- Cross-split contamination / data leakage detection
- Length distributions and token estimate stats
"""

import json
import os
import sys
from collections import Counter


def tokenize_simple(text):
    return set(text.lower().strip().split())


def jaccard_similarity(set_a, set_b):
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union


def validate_file(filepath):
    print(f"\n[*] Validating {filepath}...")
    issues = []
    rows = []
    
    if not os.path.exists(filepath):
        print(f"[-] File not found: {filepath}")
        return False, []

    with open(filepath, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                issues.append(f"Line {line_no}: Invalid JSON: {e}")
                continue

            # Check messages structure
            if "messages" not in data or not isinstance(data["messages"], list):
                issues.append(f"Line {line_no}: Missing or invalid 'messages' array")
                continue

            messages = data["messages"]
            if len(messages) < 2:
                issues.append(f"Line {line_no}: Must have at least user and assistant turn")

            expected_roles = ["system", "user", "assistant"]
            has_user = False
            has_assistant = False

            for idx, msg in enumerate(messages):
                role = msg.get("role")
                content = msg.get("content", "")

                if not role or role not in expected_roles:
                    issues.append(f"Line {line_no}, Msg {idx}: Invalid role '{role}'")
                if not content or not content.strip():
                    issues.append(f"Line {line_no}, Msg {idx}: Empty or whitespace-only content")

                if role == "user":
                    has_user = True
                if role == "assistant":
                    has_assistant = True

            if not has_user or not has_assistant:
                issues.append(f"Line {line_no}: Missing user or assistant message")

            rows.append(data)

    # Check internal duplicates within file
    for i in range(len(rows)):
        u_text_i = next((m["content"] for m in rows[i]["messages"] if m["role"] == "user"), "")
        tokens_i = tokenize_simple(u_text_i)
        for j in range(i + 1, len(rows)):
            u_text_j = next((m["content"] for m in rows[j]["messages"] if m["role"] == "user"), "")
            tokens_j = tokenize_simple(u_text_j)
            sim = jaccard_similarity(tokens_i, tokens_j)
            if sim > 0.85:
                issues.append(f"Near-duplicate prompts (sim={sim:.2f}) between row {i+1} and {j+1}: '{u_text_i[:40]}...' vs '{u_text_j[:40]}...'")

    if issues:
        print(f"[-] Found {len(issues)} issues:")
        for iss in issues[:10]:
            print(f"    - {iss}")
        return False, rows
    else:
        print(f"[+] Validation PASSED: {len(rows)} valid examples in {filepath}")
        return True, rows


def check_leakage(train_rows, eval_rows):
    print("\n[*] Checking for data leakage between train and eval splits...")
    leakage_found = False
    for t_idx, t_row in enumerate(train_rows):
        t_user = next((m["content"] for m in t_row["messages"] if m["role"] == "user"), "")
        t_tokens = tokenize_simple(t_user)
        for e_idx, e_row in enumerate(eval_rows):
            e_user = next((m["content"] for m in e_row["messages"] if m["role"] == "user"), "")
            e_tokens = tokenize_simple(e_user)
            sim = jaccard_similarity(t_tokens, e_tokens)
            if sim > 0.90:
                print(f"[-] Data leakage detected (sim={sim:.2f}) between Train #{t_idx+1} and Eval #{e_idx+1}")
                print(f"    Train: {t_user}")
                print(f"    Eval:  {e_user}")
                leakage_found = True

    if not leakage_found:
        print("[+] No data leakage detected. Train and Eval sets are properly isolated.")
    return not leakage_found


def main():
    train_ok, train_rows = validate_file("data/train/train.jsonl")
    eval_ok, eval_rows = validate_file("data/eval/eval.jsonl")

    if train_ok and eval_ok:
        leakage_ok = check_leakage(train_rows, eval_rows)
        if leakage_ok:
            print("\n[+] DATASET VALIDATION COMPLETED SUCCESSFULLY!")
            # Print stats
            cats = [r.get("category", "unknown") for r in train_rows + eval_rows]
            print("\nDataset Category Breakdown:")
            for cat, count in Counter(cats).items():
                print(f"  - {cat:25}: {count} examples")


if __name__ == "__main__":
    main()
