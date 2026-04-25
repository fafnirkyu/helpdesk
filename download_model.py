import os
import requests

MODEL_URL = "https://huggingface.co/bartowski/SmolLM2-135M-Instruct-GGUF/resolve/main/SmolLM2-135M-Instruct-Q8_0.gguf"
SAVE_PATH = "models/smollm2-135m-instruct-q8_0.gguf"

def download():
    if os.path.exists(SAVE_PATH):
        print("Model already exists.")
        return

    os.makedirs("models", exist_ok=True)
    print("Downloading model (this takes a few minutes)...")
    with requests.get(MODEL_URL, stream=True) as r:
        r.raise_for_status()
        with open(SAVE_PATH, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print("✨ Download complete.")

if __name__ == "__main__":
    download()