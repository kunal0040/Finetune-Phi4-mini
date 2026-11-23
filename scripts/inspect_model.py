"""
Model & Environment Inspection Script for Kaitu Fine-Tuning
Inspects Ollama service, installed models, GPU VRAM, RAM, and storage.
"""

import json
import os
import shutil
import subprocess
import sys
import requests


def check_ollama(base_url="http://localhost:11434"):
    print(f"[*] Checking Ollama at {base_url}...")
    try:
        resp = requests.get(f"{base_url}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            print(f"[+] Ollama is running. Found {len(models)} models.")
            return True, models
    except Exception as e:
        print(f"[-] Ollama HTTP API check failed: {e}")
    
    # Try CLI fallback
    try:
        res = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        print("[+] Ollama CLI is accessible:")
        print(res.stdout.strip())
        return True, "CLI_ONLY"
    except Exception as e:
        print(f"[-] Ollama CLI check failed: {e}")
        return False, []


def inspect_phi4():
    print("[*] Inspecting phi4-mini model via Ollama CLI...")
    info = {}
    try:
        res = subprocess.run(["ollama", "show", "phi4-mini:latest"], capture_output=True, text=True)
        info["details"] = res.stdout.strip()
        print(res.stdout.strip())
    except Exception as e:
        info["details_error"] = str(e)
    
    try:
        res = subprocess.run(["ollama", "show", "--modelfile", "phi4-mini:latest"], capture_output=True, text=True)
        info["modelfile"] = res.stdout.strip()
    except Exception as e:
        info["modelfile_error"] = str(e)

    return info


def check_hardware():
    print("\n[*] Checking Hardware Resources...")
    hw = {}
    # Disk space
    for drive in ["C:", "D:"]:
        try:
            total, used, free = shutil.disk_usage(f"{drive}\\")
            hw[f"disk_{drive}"] = {
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
            }
            print(f"  Drive {drive} - Free: {hw[f'disk_{drive}']['free_gb']} GB")
        except Exception:
            pass

    # GPU
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.free,memory.used,driver_version", "--format=csv,noheader,nounits"],
            capture_output=True, text=True
        )
        if res.returncode == 0:
            name, total, free, used, driver = [x.strip() for x in res.stdout.strip().split(",")]
            hw["gpu"] = {
                "name": name,
                "vram_total_mib": int(total),
                "vram_free_mib": int(free),
                "vram_used_mib": int(used),
                "driver": driver,
            }
            print(f"  GPU: {name} | Total VRAM: {total} MiB | Free VRAM: {free} MiB | Used: {used} MiB")
    except Exception as e:
        hw["gpu_error"] = str(e)
        print(f"  [-] Failed to query GPU: {e}")

    return hw


def main():
    report = {
        "hardware": check_hardware(),
    }
    ollama_ok, models = check_ollama()
    report["ollama_running"] = ollama_ok
    report["phi4_info"] = inspect_phi4()

    os.makedirs("results/baseline", exist_ok=True)
    report_path = "results/baseline/environment_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n[+] Full inspection report written to {report_path}")


if __name__ == "__main__":
    main()
