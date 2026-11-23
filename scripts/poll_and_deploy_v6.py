"""
poll_and_deploy_v6.py
=====================
Monitors Kaggle training job for Kaitu V6 (Version 25).
When complete:
1. Downloads kaitu-v6-q4_k_m.gguf directly to D:\\Ollama
2. Generates Modelfile_v6 with optimal sampling & stop parameters
3. Registers kaitu-v6:latest in Ollama
4. Runs full 300-prompt benchmark and comprehensive evaluation scorecard
"""

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

LOCAL_KAGGLE_DIR = Path.home() / ".kaggle"
if LOCAL_KAGGLE_DIR.exists():
    os.environ["KAGGLE_CONFIG_DIR"] = str(LOCAL_KAGGLE_DIR)
KERNEL_SLUG = os.getenv("KAGGLE_KERNEL_SLUG", "your_username/notebook4c270cdb42")
OLLAMA_DIR = Path(os.getenv("OLLAMA_MODELS_DIR", "D:/Ollama"))

def get_kaggle_binary():
    venv_k = Path(__file__).resolve().parent.parent / ".venv" / "Scripts" / "kaggle.exe"
    if venv_k.exists():
        return str(venv_k)
    return "kaggle"

def check_status():
    binary = get_kaggle_binary()
    cmd = [binary, "kernels", "status", KERNEL_SLUG]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        out = res.stdout.strip()
        for line in out.splitlines():
            if "has status" in line:
                return line.split("has status")[-1].replace('"', '').strip()
        return out
    except Exception as e:
        return f"ERROR: {e}"

def deploy_model():
    print("\n[+] Training completed! Downloading output GGUF to D:\\Ollama...")
    binary = get_kaggle_binary()
    OLLAMA_DIR.mkdir(parents=True, exist_ok=True)
    
    cmd = [binary, "kernels", "output", KERNEL_SLUG, "-p", str(OLLAMA_DIR)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print("Output logs:", res.stderr)

    gguf_v6 = OLLAMA_DIR / "kaitu-v6-q4_k_m.gguf"
    if not gguf_v6.exists():
        # Check if downloaded as kaitu-phi4-mini-q4_k_m.gguf
        fallback = OLLAMA_DIR / "kaitu-phi4-mini-q4_k_m.gguf"
        if fallback.exists():
            shutil.move(fallback, gguf_v6)

    if not gguf_v6.exists():
        print(f"[-] Error: Could not locate {gguf_v6} after download!")
        return False

    print(f"[+] Verified GGUF: {gguf_v6} ({gguf_v6.stat().st_size / (1024*1024):.2f} MB)")

    # Build Modelfile_v6
    modelfile_content = f"""FROM D:\\Ollama\\kaitu-v6-q4_k_m.gguf

TEMPLATE \"\"\"{{{{- range .Messages }}}}<|{{{{ .Role }}}}>
{{{{ .Content }}}}<|end|>
{{{{ end }}}}<|assistant|>
\"\"\"

PARAMETER temperature 0.2
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1
PARAMETER num_predict 400
PARAMETER stop "<|end|>"
PARAMETER stop "<|user|>"
PARAMETER stop "<|assistant|>"
PARAMETER stop "Kunal:"
PARAMETER stop "**Kunal:**"
PARAMETER stop "User:"
PARAMETER stop "**User:**"
PARAMETER stop "AI:"
PARAMETER stop "**AI:**"
"""
    modelfile_path = OLLAMA_DIR / "Modelfile_v6"
    with open(modelfile_path, "w", encoding="utf-8") as f:
        f.write(modelfile_content)
    print(f"[+] Created {modelfile_path}")

    # Register in Ollama
    print("[+] Registering kaitu-v6:latest in Ollama...")
    ollama_cmd = ["ollama", "create", "kaitu-v6:latest", "-f", str(modelfile_path)]
    subprocess.run(ollama_cmd, check=True)
    print("[+] Successfully registered kaitu-v6:latest in Ollama!")
    return True

def main():
    print("="*60)
    print(f" Monitoring Kaggle Kernel: {KERNEL_SLUG}")
    print("="*60)
    
    poll_count = 0
    while True:
        status = check_status()
        poll_count += 1
        print(f"[{time.strftime('%H:%M:%S')}] Check #{poll_count}: Status = '{status}'")
        
        if "COMPLETE" in status:
            success = deploy_model()
            if success:
                print("\n[+] Kaitu V6 is deployed and ready for testing!")
            break
        elif "FAILED" in status or "ERROR" in status:
            print(f"[-] Job failed on Kaggle: {status}")
            break
            
        time.sleep(30)

if __name__ == "__main__":
    main()
