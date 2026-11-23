"""
download_v7_gguf.py
===================
Streams kaitu-v7-q4_k_m.gguf (~2.49 GB) directly to D:/Ollama/kaitu-v7-q4_k_m.gguf
"""

import sys
import time
import urllib.request
from pathlib import Path

URL = "https://kkb-production.jupyter-proxy.kaggle.net/k/372973706/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwidHlwIjoiSldUIn0..zDGKgaNDqBKpf2Ij4sJxUA.o6RYkuk36NhjtfAinKMt3uj8JATZqfTGCTpgNpYB1EjQ0qysQdS5GZPlo95T2ixvtbd-mshYkZi7St5Msx8ZJpBEaGtOP7jGpGx-IKUMlAmH_eWdDY2Sx4kanDa6iBDl6GSmk2gs-_wcLVEwo5XlvX5bLRVh3sEv108VKHbSFury16Wcm3Vr6Pxc2fEMrOATG9mIfqmOTnBeZTel3REoVh3Yurl6nj2zhRueh-ZPHC1Ck5umIJmoXBUy9G3G2cdu.feaCWtQ3mXFNyhgyKVLg1Q/proxy/files/kaitu-v7-q4_k_m.gguf"
TARGET = Path("D:/Ollama/kaitu-v7-q4_k_m.gguf")
TMP_TARGET = Path("D:/Ollama/kaitu-v7-q4_k_m.gguf.tmp")

def download():
    print(f"[*] Starting download from Kaggle proxy to {TARGET}...")
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    
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
    download()
