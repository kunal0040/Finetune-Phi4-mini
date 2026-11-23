"""
poll_and_deploy_v5.py
=====================
Monitors Kaggle notebook Version #23 on kunalbh04/notebook4c270cdb42.
When COMPLETE:
1. Downloads GGUF model via Kaggle CLI.
2. Deploys to Ollama as kaitu-v5:latest.
3. Runs full 300-prompt benchmark.
"""

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

def get_kaggle_binary():
    venv_k = Path(__file__).resolve().parent.parent / ".venv" / "Scripts" / "kaggle.exe"
    if venv_k.exists():
        return str(venv_k)
    return "kaggle"

LOCAL_KAGGLE_DIR = Path.home() / ".kaggle"
if LOCAL_KAGGLE_DIR.exists():
    os.environ["KAGGLE_CONFIG_DIR"] = str(LOCAL_KAGGLE_DIR)
KERNEL_SLUG = os.getenv("KAGGLE_KERNEL_SLUG", "your_username/notebook4c270cdb42")

def check_status():
    try:
        res = subprocess.run([get_kaggle_binary(), "kernels", "status", KERNEL_SLUG], capture_output=True, text=True, timeout=45)
        return res.stdout.strip()
    except Exception as e:
        print(f"[*] Transient check exception: {e}")
        return ""

def download_and_deploy():
    download_dir = Path("D:/Ollama/v5_download")
    download_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n[+] Downloading output artifacts from Kaggle...")
    res = subprocess.run([get_kaggle_binary(), "kernels", "output", KERNEL_SLUG, "-p", str(download_dir)], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr)
        
    # Search for GGUF
    gguf_files = list(download_dir.glob("*.gguf"))
    if not gguf_files:
        print("[-] Error: No .gguf file found in download directory!")
        return False
        
    src_gguf = gguf_files[0]
    target_gguf = Path("D:/Ollama/kaitu-v5-q4_k_m.gguf")
    print(f"[+] Moving {src_gguf} to {target_gguf} ({src_gguf.stat().st_size} bytes)...")
    shutil.copy2(src_gguf, target_gguf)
    
    # Write Modelfile_v5
    modelfile_path = Path("D:/Ollama/Modelfile_v5")
    modelfile_content = f"""FROM D:\\Ollama\\kaitu-v5-q4_k_m.gguf

TEMPLATE \"\"\"<|user|>
{{{{ .Prompt }}}}<|end|>
<|assistant|>
{{{{ .Response }}}}<|end|>\"\"\"

PARAMETER stop "<|user|>"
PARAMETER stop "<|assistant|>"
PARAMETER stop "<|end|>"
PARAMETER stop "<|endoftext|>"
PARAMETER temperature 0.35
PARAMETER top_p 0.85
PARAMETER repeat_penalty 1.15
PARAMETER num_predict 2048
"""
    with open(modelfile_path, "w", encoding="utf-8") as f:
        f.write(modelfile_content)
        
    print(f"[+] Modelfile_v5 written at {modelfile_path}")
    
    # Ollama create
    print("[+] Creating Ollama model 'kaitu-v5:latest'...")
    res = subprocess.run(["ollama", "create", "kaitu-v5:latest", "-f", str(modelfile_path)], capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print(f"[-] Ollama create failed: {res.stderr}")
        return False
        
    print("[+] Successfully registered kaitu-v5:latest in Ollama!")
    
    # Launch 300 benchmark
    print("\n[+] Launching 300-prompt benchmark for kaitu-v5:latest...")
    cmd = [
        sys.executable,
        "scripts/benchmark_3way.py",
        "--model", "kaitu-v5:latest",
        "--prompts", "data/benchmarks/eval_300_prompts.json"
    ]
    subprocess.run(cmd, check=True)
    print("\n[+] 300-prompt benchmark completed successfully! Results in results/benchmarks/kaitu_v5_300.json")
    return True

def main():
    print("[*] Starting Kaggle Version #23 monitor & deployment service...")
    start_time = time.time()
    last_status = None
    
    while True:
        status_line = check_status()
        if status_line != last_status:
            print(f"[{time.strftime('%H:%M:%S')}] Status update: {status_line}")
            last_status = status_line
            
        if "KernelWorkerStatus.COMPLETE" in status_line or "status \"complete\"" in status_line.lower():
            elapsed = time.time() - start_time
            print(f"[+] Kaggle Version #23 completed in {elapsed/60:.1f} minutes!")
            success = download_and_deploy()
            if success:
                print("\n=======================================================")
                print(" KAITU V5 DEPLOYMENT & 300 BENCHMARK 100% COMPLETE! ")
                print("=======================================================\n")
            sys.exit(0)
            
        elif "KernelWorkerStatus.ERROR" in status_line or "KernelWorkerStatus.FAILED" in status_line:
            print(f"[-] Kaggle worker failed: {status_line}")
            sys.exit(1)
            
        time.sleep(30)

if __name__ == "__main__":
    main()
