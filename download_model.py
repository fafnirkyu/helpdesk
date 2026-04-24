# download_model.py (Now in your root folder)
import os
import requests

# This ensures it always goes to /app/models inside Docker
MODEL_URL = "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
SAVE_PATH = os.path.join(os.getcwd(), "models", "llama-3.2-3b-instruct.Q4_K_M.gguf")

def download():
    if os.path.exists(SAVE_PATH):
        print(f"✅ Model already exists at {SAVE_PATH}")
        return

    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    print("⏳ Downloading model to root models/ folder...")
    # ... rest of your download logic ...