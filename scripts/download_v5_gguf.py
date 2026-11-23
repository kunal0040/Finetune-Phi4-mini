"""
download_v5_gguf.py
===================
Downloads kaitu-phi4-mini-q4_k_m.gguf (2.49 GB) directly to D:/Ollama/kaitu-v5-q4_k_m.gguf
"""

import sys
import time
import urllib.request
from pathlib import Path

URL = "https://kkb-production.jupyter-proxy.kaggle.net/k/372723406/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwidHlwIjoiSldUIn0..DQbCgbxD75BOoJHzIhemhw.p7-AmQ-pJDAAJlrHBYocajunicEQCdILeYFCkootWKkPWfYi2GxslGM8yi9JmLGfncGblk-ewhkokpn2YLMalXH8S8PRylGGS6dozPIVA23e4ohuGOdLKipS7LI6U-l1nU9e9TIT1ENxbDApkFutqhgXhmyn9unbBT8FCPrggQQZl6Td7x8JATW3opvaKrGGNLzYhM6QZmxhu8gzH-x3uy_gJTMe2YI5JgBYOnRaSRFlVefTqaJlcrRKw1IwPRKP.GeX7aRZ0blpbM6s5IEA_Aw/proxy/files/kaitu-phi4-mini-q4_k_m.gguf"
TARGET = Path("D:/Ollama/kaitu-v5-q4_k_m.gguf")
TMP_TARGET = Path("D:/Ollama/kaitu-v5-q4_k_m.gguf.tmp")

def download():
    print(f"[*] Starting download from Kaggle proxy to {TARGET}...")
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    
    t0 = time.time()
    downloaded = 0
    chunk_size = 10 * 1024 * 1024 # 10 MB chunks
    
    with urllib.request.urlopen(req) as resp, open(TMP_TARGET, "wb") as f:
        total = int(resp.getheader("Content-Length", 2493840288))
        print(f"[+] Total size: {total / (1024**3):.2f} GB ({total} bytes)")
        
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            pct = (downloaded / total) * 100
            elapsed = time.time() - t0
            speed = (downloaded / (1024 * 1024)) / (elapsed if elapsed > 0 else 1)
            print(f"[{elapsed:.1f}s] Downloaded {downloaded / (1024**2):.1f} MB / {total / (1024**2):.1f} MB ({pct:.1f}%) @ {speed:.1f} MB/s", flush=True)

    print("[*] Finalizing file...")
    if TARGET.exists():
        TARGET.unlink()
    TMP_TARGET.rename(TARGET)
    print(f"[+] Download complete: {TARGET} ({TARGET.stat().st_size} bytes)")

if __name__ == "__main__":
    download()
