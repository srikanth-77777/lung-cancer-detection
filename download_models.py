"""
================================================================
Model Weight Downloader — runs before app startup on Render
================================================================
Downloads .pth model weights from cloud storage (HuggingFace Hub
or Google Drive) if they are not already present on disk.

Set these environment variables in Render dashboard:
  MODEL_URL_1  = direct download URL for best_ResNet50_v5.pth
  MODEL_URL_2  = direct download URL for resnet50_chest_ct_95acc_final.pth
  EFF_WEIGHTS  = local path to save model 1 (default: ./best_ResNet50_v5.pth)
  DENSE_WEIGHTS= local path to save model 2 (default: ./resnet50_chest_ct_95acc_final.pth)
================================================================
"""

import os
import requests

def download_file(url: str, dest_path: str):
    """Download a file from a URL with progress logging."""
    if os.path.exists(dest_path):
        print(f"[SKIP] Already exists: {dest_path}")
        return

    print(f"[DOWNLOAD] Fetching model from:\n  {url}")
    print(f"[DOWNLOAD] Saving to: {dest_path}")

    os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)

    response = requests.get(url, stream=True, timeout=300)
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))
    downloaded = 0
    chunk_size = 8 * 1024 * 1024  # 8 MB chunks

    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(f"  ... {pct:.1f}% ({downloaded // (1024*1024)} MB / {total // (1024*1024)} MB)")

    print(f"[SUCCESS] Downloaded: {dest_path}")


def ensure_models():
    """
    Call this at application startup to ensure both model
    weight files are present on disk.
    """
    model_url_1   = os.getenv("MODEL_URL_1", "")
    model_url_2   = os.getenv("MODEL_URL_2", "")
    eff_weights   = os.getenv("EFF_WEIGHTS", "best_ResNet50_v5.pth")
    dense_weights = os.getenv("DENSE_WEIGHTS", "resnet50_chest_ct_95acc_final.pth")

    if not model_url_1 or not model_url_2:
        print("[WARNING] MODEL_URL_1 / MODEL_URL_2 not set. "
              "Assuming model files already exist locally.")
        return

    download_file(model_url_1, eff_weights)
    download_file(model_url_2, dense_weights)


if __name__ == "__main__":
    ensure_models()
