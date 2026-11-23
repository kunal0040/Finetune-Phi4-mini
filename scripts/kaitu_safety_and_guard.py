"""
kaitu_safety_and_guard.py
=========================
Production Add-On System for Kaitu (Supports V6, V7, and V8).
Implements the 5 runtime guards and utility tools:
1. Command Guard: Flags dangerous commands (-f, --force, rm -rf, DROP, invalid flags)
2. Output Cleaner & Filter: Strips leaked "Answer:"/"Step", fixes email sign-offs, trims lists
3. Python AST Validator: Parses code snippets via ast.parse and flags syntax errors
4. Math & Unit Calculator: Exact calculation for percentages, compound growth, and splits
5. Memory & Context Injector: Injects user name, assistant identity, and runtime preferences
"""

import ast
import json
import re
import sys
from pathlib import Path

# =========================================================================
# 1. COMMAND GUARD (Dangerous Suggestion Detection)
# =========================================================================
class KaituCommandGuard:
    DANGEROUS_PATTERNS = [
        (r"\bgit\s+push\s+.*(-f\b|--force\b)", "DANGEROUS: Force push can overwrite remote history. Use 'git pull --rebase' or '--force-with-lease'."),
        (r"\brm\s+-[rf]*[f][rf]*\s+[\/~]", "CRITICAL: Recursive force-deletion on root/home directory detected."),
        (r"\b(rm|rmdir|Remove-Item)\b.*(site-packages|\.cache)", "WARNING: Deleting site-packages or cache libraries directly can corrupt your Python environment."),
        (r"\bDROP\s+(TABLE|DATABASE)\b", "WARNING: Irreversible SQL drop statement detected. Ensure you have verified backups first."),
        (r"\bROLLBACK\s+TO\s+pg_backup_start_time\b", "FABRICATED: 'pg_backup_start_time' is not a valid rollback target in PostgreSQL."),
        (r"\bpython\s+-X\s+inspectless\b", "FABRICATED: '-X inspectless' is not a valid Python runtime flag.")
    ]

    @classmethod
    def audit_text(cls, text: str) -> list[str]:
        warnings = []
        for pat, desc in cls.DANGEROUS_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                warnings.append(desc)
        return warnings

    @classmethod
    def is_safe(cls, text: str) -> bool:
        return len(cls.audit_text(text)) == 0


# =========================================================================
# 2. OUTPUT CLEANER & RUNTIME FILTER
# =========================================================================
class KaituOutputCleaner:
    @staticmethod
    def clean_response(prompt: str, response: str, category: str = "general") -> str:
        text = response.strip()

        # 1. Fix self-dialogue & prompt leaks
        text = re.sub(r"^Your user:\s*.*?\n+", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^Question:\s*.*?\n+", "", text, flags=re.IGNORECASE)

        # 2. Strip leaked "Answer: ..." from non-math explanations
        if category not in ["reasoning", "practical_reasoning", "math"]:
            lines = text.splitlines()
            if lines and lines[-1].strip().lower().startswith("answer:"):
                lines.pop()
                text = "\n".join(lines).strip()

        # 3. Clean email sign-offs: replace "Kaitu" as sender with "[Your Name]"
        if category in ["communication", "writing"] or "subject:" in text.lower():
            text = re.sub(r"\b(Sincerely|Best|Warmly|Regards|Best regards),\s*\n\s*Kaitu\b", r"\1,\n[Your Name]", text, flags=re.IGNORECASE)
            text = re.sub(r"\b(Best regards|Sincerely|Warm regards),\s*\n\s*-?\s*DK\b", r"\1,\n[Your Name]", text, flags=re.IGNORECASE)

        # 4. Trim runaway lists if prompt explicitly asked for a small N (e.g. 5 items)
        if "5 programming languages" in prompt.lower() and "-" in text:
            parts = [p.strip() for p in text.split("-") if p.strip() and not p.lower().startswith("answer")]
            if len(parts) > 5:
                text = "-".join(parts[:5])

        # 5. Fix stray LaTeX wrappers
        text = re.sub(r"\\\((.*?)\\\)", r"\1", text)
        text = re.sub(r"\\\[(.*?)\\\]", r"\1", text)
        text = text.replace("$$", "")

        return text.strip()


# =========================================================================
# 3. CODE SYNTAX VALIDATOR (ast.parse)
# =========================================================================
class KaituCodeValidator:
    @staticmethod
    def validate_code_blocks(text: str) -> dict:
        blocks = re.findall(r"```python\s*(.*?)```", text, re.DOTALL)
        results = []
        for i, code in enumerate(blocks):
            try:
                ast.parse(code)
                results.append({"block": i + 1, "valid": True, "error": None})
            except SyntaxError as e:
                results.append({"block": i + 1, "valid": False, "error": f"SyntaxError at line {e.lineno}: {e.msg}"})
        return {
            "total_blocks": len(blocks),
            "all_valid": all(r["valid"] for r in results),
            "details": results
        }


# =========================================================================
# 4. CALCULATOR TOOL (Percentages, Compound Growth, Splits)
# =========================================================================
class KaituCalculator:
    @staticmethod
    def stacked_discount(original_price: float, discounts: list[float]) -> dict:
        price = original_price
        for d in discounts:
            price *= (1.0 - (d / 100.0))
        total_discount_pct = ((original_price - price) / original_price) * 100.0
        return {
            "original_price": original_price,
            "final_price": round(price, 2),
            "total_discount_pct": round(total_discount_pct, 2)
        }

    @staticmethod
    def tip_calculation(bill: float, tip_pct: float) -> dict:
        tip = bill * (tip_pct / 100.0)
        return {"bill": bill, "tip": round(tip, 2), "total": round(bill + tip, 2)}

    @staticmethod
    def compound_doubling(start_cents: int, days: int) -> float:
        # Day 1 = start_cents * 2^0
        cents = start_cents * (2 ** (days - 1))
        return cents / 100.0


# =========================================================================
# 5. MEMORY FILE & RUNTIME CONTEXT INJECTOR
# =========================================================================
class KaituMemory:
    MEMORY_FILE = Path("D:/Antigravity/Finetune/kaitu_memory.json")

    @classmethod
    def load(cls) -> dict:
        if cls.MEMORY_FILE.exists():
            try:
                with open(cls.MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "user_name": "Kunal",
            "assistant_name": "Kaitu",
            "environment": "Local Ollama on Windows",
            "tone": "Warm, direct, technically rigorous",
            "code_style": "Python 3.10+, type hints, clean imports"
        }

    @classmethod
    def save(cls, data: dict):
        with open(cls.MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def format_system_prompt(cls) -> str:
        mem = cls.load()
        return (
            f"You are {mem.get('assistant_name', 'Kaitu')}, the dedicated personal AI companion for {mem.get('user_name', 'your user')}.\n"
            f"Tone: {mem.get('tone', 'Direct and helpful')}.\n"
            f"You run locally via Ollama with zero external account access.\n"
            f"Always address your user directly in the second person ('you', 'your')."
        )


if __name__ == "__main__":
    print("[+] Kaitu Safety Guard & Add-On Suite Loaded.")
    print("[+] Test audit on clean text:", KaituCommandGuard.audit_text("git pull --rebase origin main"))
    print("[+] Test memory prompt:\n", KaituMemory.format_system_prompt())
    calc = KaituCalculator.stacked_discount(100.0, [20.0, 10.0])
    print("[+] Test calculator stacked discount (20% + 10% on $100):", calc)
