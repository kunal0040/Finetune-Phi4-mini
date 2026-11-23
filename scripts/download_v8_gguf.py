"""
download_v8_gguf.py
===================
Streams kaitu-v8-q4_k_m.gguf (~2.49 GB) directly to D:/Ollama/kaitu-v8-q4_k_m.gguf
Takes signed URL as first argument or uses embedded URL.
"""

import sys
import time
import urllib.request
from pathlib import Path

TARGET = Path("D:/Ollama/kaitu-v8-q4_k_m.gguf")
TMP_TARGET = Path("D:/Ollama/kaitu-v8-q4_k_m.gguf.tmp")

def download(url: str):
    print(f"[*] Starting download from Kaggle proxy to {TARGET}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    t0 = time.time()
    downloaded = 0
    chunk_size = 8 * 1024 * 1024 # 8 MB chunks
    
    with urllib.request.urlopen(req) as resp, open(TMP_TARGET, "wb") as f:
        total = int(resp.getheader("Content-Length", 2673868800))
        print(f"[+] Total size: {total / (1024**3):.2f} GB ({total} bytes)")
        
        last_log = t0
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            pct = (downloaded / total) * 100
            now = time.time()
            if now - last_log >= 2.0:
                elapsed = now - t0
                speed = (downloaded / (1024 * 1024)) / (elapsed if elapsed > 0 else 1)
                print(f"[{elapsed:.1f}s] Downloaded {downloaded / (1024**2):.1f} MB / {total / (1024**2):.1f} MB ({pct:.1f}%) @ {speed:.1f} MB/s", flush=True)
                last_log = now

    print("[*] Finalizing file...")
    if TARGET.exists():
        TARGET.unlink()
    TMP_TARGET.rename(TARGET)
    print(f"[+] Download complete: {TARGET} ({TARGET.stat().st_size} bytes)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        u = sys.argv[1]
    else:
        print("Usage: python download_v8_gguf.py <SIGNED_URL>")
        sys.exit(1)
    download(u)
