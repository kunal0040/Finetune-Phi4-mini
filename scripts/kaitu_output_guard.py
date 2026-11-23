"""
kaitu_output_guard.py
=====================
Output Checker & Safety Guard for Kaitu (Add-on #2 & #3).
Validates model outputs against:
1. Roleplay leaks & self-dialogue labels ('Kunal:', 'User:', 'Me:', 'AI:')
2. Third-person name leaks ('Kunal's car', 'for Kunal', 'to Kunal' outside greetings/sign-offs)
3. Bad identity responses ('I don't exist', 'I don't exist anymore')
4. False capability claims ('connected to your device', 'without permission')
5. Raw LaTeX artifacts (\\boxed, \\frac, \\[, \\], \\(, \\))
6. Unbalanced code fences (missing closing ```)
7. Python code syntax validation (ast.parse)
"""

import ast
import re

class KaituOutputGuard:
    def __init__(self):
        self.speaker_patterns = [
            r"\bkunal:\s", r"\*\*kunal:\*\*", r"\bme:\s", r"\*\*me:\*\*",
            r"\buser:\s", r"\*\*user:\*\*", r"\bai:\s", r"\*\*ai:\*\*",
            r"kunal's ai companion:"
        ]
        self.third_person_patterns = [
            r"\bfor kunal\b", r"\bkunal should\b", r"\bkunal will\b",
            r"\bkunal's\b", r"\bask kunal\b", r"\bto kunal\b",
            r"\bkaitu's\b"
        ]
        self.bad_refusals = [
            "i don't exist", "i do not exist", "i don't exist anymore"
        ]
        self.false_capabilities = [
            "directly connected to your device",
            "without permission",
            "for security reasons, i don't access your accounts",
            "keep track of what's new"
        ]
        self.latex_patterns = [
            r"\\boxed", r"\\frac", r"\\text\{", r"\\\[", r"\\\]", r"\$\$", r"\\\(", r"\\\)"
        ]

    def validate(self, text: str, category: str = "general") -> dict:
        issues = []
        text_lower = text.lower()

        # 1. Self-Dialogue / Roleplay tags
        for pat in self.speaker_patterns:
            if re.search(pat, text_lower):
                issues.append(f"Self-dialogue label found: {pat}")

        # 2. Third-Person Name Leaks
        for pat in self.third_person_patterns:
            if re.search(pat, text_lower):
                issues.append(f"Third-person name leak found: {pat}")

        # 3. Bad Refusals
        for ref in self.bad_refusals:
            if ref in text_lower:
                issues.append(f"Bad refusal hallucination: '{ref}'")

        # 4. False Capabilities
        for cap in self.false_capabilities:
            if cap in text_lower:
                issues.append(f"False capability claim: '{cap}'")

        # 5. Raw LaTeX Formatting
        for lat in self.latex_patterns:
            if re.search(lat, text):
                issues.append(f"Raw LaTeX formatting found: {lat}")

        # 6. Unbalanced Code Fences
        fence_count = text.count("```")
        if fence_count % 2 != 0:
            issues.append(f"Unbalanced code block fences (count: {fence_count})")

        # 7. Python Syntax Validation if Python code block present
        python_blocks = re.findall(r"```python\s*(.*?)```", text, re.DOTALL)
        for i, code in enumerate(python_blocks):
            try:
                ast.parse(code)
            except SyntaxError as e:
                issues.append(f"Python syntax error in code block #{i+1}: {e.msg} at line {e.lineno}")

        passed = len(issues) == 0
        return {
            "passed": passed,
            "issues": issues,
            "cleaned_text": self.clean(text) if not passed else text
        }

    def clean(self, text: str) -> str:
        """Applies rule-based regex cleaning for minor artifacts."""
        cleaned = text
        # Strip trailing unclosed backticks
        if cleaned.endswith("```") and cleaned.count("```") % 2 != 0:
            cleaned = cleaned[:-3].rstrip()
        # Clean stray markdown markers
        cleaned = re.sub(r"\*\*$", "", cleaned).rstrip()
        # Convert simple LaTeX wrappers
        cleaned = re.sub(r"\\\((.*?)\\\)", r"\1", cleaned)
        cleaned = re.sub(r"\\\[(.*?)\\\]", r"\1", cleaned)
        return cleaned

if __name__ == "__main__":
    guard = KaituOutputGuard()
    sample = "Kunal's car drove 60 miles at 30 mph. Total speed is \\( 40 \\) mph."
    res = guard.validate(sample)
    print("Sample Validation:", res)
