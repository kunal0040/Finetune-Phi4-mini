"""
Automated Kaggle Cloud Training Dispatcher & Poller for Kaitu.
Pushes the training job to Kaggle GPU cloud, monitors execution,
downloads the resulting .gguf model, and imports it into Ollama.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Configure Kaggle directory locally within workspace to avoid Windows sandbox permission issues
LOCAL_KAGGLE_DIR = Path("D:/Antigravity/Finetune/.kaggle").resolve()
os.environ["KAGGLE_CONFIG_DIR"] = str(LOCAL_KAGGLE_DIR)


def get_kaggle_binary():
    venv_kaggle = Path("D:/Antigravity/Finetune/.venv/Scripts/kaggle.exe")
    if venv_kaggle.exists():
        return str(venv_kaggle)
    which_kaggle = shutil.which("kaggle")
    if which_kaggle:
        return which_kaggle
    return "kaggle"


def check_kaggle_cli():
    print("[*] Checking Kaggle CLI availability...")
    binary = get_kaggle_binary()
    try:
        res = subprocess.run([binary, "--version"], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[+] Kaggle CLI found: {res.stdout.strip()}")
            return True
        else:
            print(f"[-] Kaggle CLI check returned error: {res.stderr}")
    except Exception as e:
        print(f"[-] Could not run Kaggle CLI ({binary}): {e}")
    return False


def setup_credentials(username=None, key=None):
    LOCAL_KAGGLE_DIR.mkdir(parents=True, exist_ok=True)
    kaggle_json = LOCAL_KAGGLE_DIR / "kaggle.json"
    root_kaggle_json = Path("D:/Antigravity/Finetune/kaggle.json")

    # If user placed kaggle.json in workspace root, copy it to .kaggle
    if root_kaggle_json.exists() and not kaggle_json.exists():
        shutil.copy(root_kaggle_json, kaggle_json)

    # Check environment variables
    env_user = os.environ.get("KAGGLE_USERNAME")
    env_key = os.environ.get("KAGGLE_KEY")

    if env_user and env_key:
        print(f"[+] Using Kaggle credentials from environment for user: {env_user}")
        return env_user

    if kaggle_json.exists():
        try:
            with open(kaggle_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                user = data.get("username")
                if user:
                    print(f"[+] Found Kaggle credentials in {kaggle_json} for user: {user}")
                    return user
        except Exception as e:
            print(f"[-] Error reading {kaggle_json}: {e}")

    if username and key:
        print(f"[*] Saving credentials to {kaggle_json}...")
        with open(kaggle_json, "w", encoding="utf-8") as f:
            json.dump({"username": username, "key": key}, f)
        print(f"[+] Credentials written for user: {username}")
        return username

    print("\n[-] Missing Kaggle API Credentials!")
    print("To dispatch the cloud GPU job automatically, Kaggle requires your API key.")
    print("Steps to obtain it:")
    print("  1. Log into https://www.kaggle.com")
    print("  2. Go to 'Account Settings' -> 'API' -> Click 'Create New Token'")
    print("  3. Save the downloaded 'kaggle.json' into: D:\\Antigravity\\Finetune\\.kaggle\\kaggle.json")
    print("     (or run this script with --username <user> --key <key>)\n")
    return None


def dispatch_job(username, kernel_slug="kaitu-phi4-mini-qlora"):
    print("\n[*] Packaging Kaggle kernel...")
    from scripts.build_kaggle_kernel import generate_kaggle_kernel
    generate_kaggle_kernel(username=username)

    kernel_id = f"{username}/{kernel_slug}"
    binary = get_kaggle_binary()
    print(f"[*] Dispatching kernel '{kernel_id}' to Kaggle GPU cloud...")
    try:
        res = subprocess.run([binary, "kernels", "push", "-p", "kaggle_job"], capture_output=True, text=True, check=True)
        print(res.stdout.strip())
        print(f"[+] Job successfully dispatched: https://www.kaggle.com/code/{kernel_id}")
        return kernel_id
    except subprocess.CalledProcessError as e:
        print(f"[-] Failed to push kernel: {e.stderr or e.stdout}")
        return None


def monitor_job(kernel_id, poll_interval=60):
    print(f"\n[*] Monitoring training job '{kernel_id}' on Kaggle GPU...")
    start_time = time.time()
    binary = get_kaggle_binary()

    while True:
        try:
            res = subprocess.run([binary, "kernels", "status", kernel_id], capture_output=True, text=True)
            status_text = res.stdout.strip()
            elapsed_min = round((time.time() - start_time) / 60, 1)
            print(f"  [{elapsed_min}m elapsed] Status: {status_text}")

            status_lower = status_text.lower()
            if "complete" in status_lower:
                print("\n[+] Cloud training and GGUF quantization completed successfully!")
                return True
            elif "error" in status_lower or "failed" in status_lower:
                print(f"\n[-] Job failed on Kaggle with status: {status_text}")
                return False
            elif "cancel" in status_lower:
                print(f"\n[-] Job was cancelled: {status_text}")
                return False

        except Exception as e:
            print(f"[-] Polling error: {e}")

        time.sleep(poll_interval)


def download_artifacts(kernel_id, dest_dir="."):
    print(f"\n[*] Downloading resulting artifacts from {kernel_id} to {dest_dir}...")
    binary = get_kaggle_binary()
    try:
        res = subprocess.run([binary, "kernels", "output", kernel_id, "-p", dest_dir], capture_output=True, text=True, check=True)
        print(res.stdout.strip())
        print("[+] Output files downloaded.")
    except subprocess.CalledProcessError as e:
        print(f"[-] Download error: {e.stderr or e.stdout}")
        return False

    gguf_files = list(Path(dest_dir).glob("*.gguf"))
    if gguf_files:
        print(f"[+] Found GGUF model: {gguf_files[0]}")
        return str(gguf_files[0])
    else:
        print("[-] Warning: No .gguf file found in downloaded artifacts.")
        return None


def register_in_ollama(gguf_path, model_name="kaitu-phi4-mini"):
    print(f"\n[*] Registering {model_name} in Ollama using {gguf_path}...")
    from scripts.export_model import generate_ollama_modelfile
    generate_ollama_modelfile(gguf_path_or_base=gguf_path, modelfile_path="Modelfile")

    try:
        res = subprocess.run(["ollama", "create", model_name, "-f", "Modelfile"], capture_output=True, text=True, check=True)
        print(res.stdout.strip())
        print(f"[+] Model '{model_name}' successfully created and registered in Ollama!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] Ollama registration failed: {e.stderr or e.stdout}")
        return False


def main():
    parser = argparse.ArgumentParser(description="End-to-End Kaggle Cloud Training Automation for Kaitu")
    parser.add_argument("--username", help="Kaggle username")
    parser.add_argument("--key", help="Kaggle API key")
    parser.add_argument("--poll-interval", type=int, default=60, help="Status polling interval in seconds")
    parser.add_argument("--skip-train", action="store_true", help="Skip training and download existing kernel output")
    args = parser.parse_args()

    if not check_kaggle_cli():
        sys.exit(1)

    username = setup_credentials(args.username, args.key)
    if not username:
        sys.exit(1)

    kernel_id = f"{username}/kaitu-phi4-mini-qlora"

    if not args.skip_train:
        dispatched_id = dispatch_job(username)
        if not dispatched_id:
            sys.exit(1)

        success = monitor_job(dispatched_id, poll_interval=args.poll_interval)
        if not success:
            print("[-] Exiting due to training failure.")
            sys.exit(1)

    gguf_path = download_artifacts(kernel_id)
    if gguf_path:
        register_in_ollama(gguf_path)
        print("\n=======================================================")
        print("ALL AUTOMATION STAGES COMPLETED SUCCESSFULLY!")
        print("You can now test the model in Ollama: ollama run kaitu-phi4-mini")
        print("=======================================================")


if __name__ == "__main__":
    main()
