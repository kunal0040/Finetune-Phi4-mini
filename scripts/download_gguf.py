import sys
import os
import requests
from tqdm import tqdm

def download_file(url, target_path):
    print(f"Downloading to {target_path}...")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, stream=True, headers=headers, timeout=60)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    print(f"Total size: {total_size / (1024 * 1024):.2f} MB")

    temp_path = target_path + ".tmp"
    with open(temp_path, "wb") as f, tqdm(
        desc="kaitu-phi4-mini-q4_k_m.gguf",
        total=total_size,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=1024 * 1024): # 1 MB chunks
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))

    if os.path.exists(target_path):
        os.remove(target_path)
    os.rename(temp_path, target_path)
    print(f"SUCCESS: Saved {target_path} ({os.path.getsize(target_path)} bytes)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_gguf.py <URL> [target_path]")
        sys.exit(1)
    url = sys.argv[1]
    if len(sys.argv) >= 3:
        target = sys.argv[2]
    else:
        target = os.path.join(os.getcwd(), "kaitu-phi4-mini-q4_k_m.gguf")
    os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)
    download_file(url, target)
