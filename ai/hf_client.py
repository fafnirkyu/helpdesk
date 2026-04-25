import threading
import os
import json
import re
import time
from llama_cpp import Llama # Critical: pip install llama-cpp-python
from tests.debug_logger import log_ai_request, log_ai_response

# Thread-safe Singleton for the Model
_MODEL_LOCK = threading.Lock()
_LLM_INSTANCE = None

def get_cpp_client():
    global _LLM_INSTANCE
    with _MODEL_LOCK:
        if _LLM_INSTANCE is None:
            # Look for model in a 'models' folder
            model_path = os.getenv("MODEL_PATH", "models/llama-3.2-3b-instruct.Q4_K_M.gguf")
            
            if not os.path.exists(model_path):
                print(f"Model not found at {model_path}. Fallback to keyword mode.")
                return None
                
            print(f"Loading Llama-CPP Model: {model_path}...")
            _LLM_INSTANCE = Llama(
                model_path=model_path,
                n_ctx=1024,      # Context window size
                n_threads=2,     # Adjust based on Railway CPU cores
                verbose=False    # Keeps logs clean
            )
    return _LLM_INSTANCE

def hf_generate(prompt: str, max_tokens: int = 300) -> str:
    llm = get_cpp_client()
    if not llm:
        return "ERROR: Model not loaded"

    start = time.time()
    log_ai_request(prompt, "llama-cpp", max_tokens)
    
    try:
        # Generate response
        output = llm(
            f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
            max_tokens=max_tokens,
            stop=["<|eot_id|>", "user:", "\n\n\n"],
            echo=False
        )
        
        text = output["choices"][0]["text"].strip()
        log_ai_response(text, time.time() - start, True)
        return text
    except Exception as e:
        log_ai_response(f"ERROR: {e}", time.time() - start, False)
        return f"ERROR: {e}"

def classify_with_llm_detailed(message: str, examples: list) -> dict:
    # This remains mostly the same, but now calls hf_generate (which uses CPP)
    context = "\n".join([f"- {e['instruction']} => {e['response']}" for e in examples])

    prompt = f"""Use the following examples to classify the new ticket.
Context:
{context}

Ticket: "{message}"
Return ONLY a JSON object with: category, subcategory, summary, response."""

    raw = hf_generate(prompt)
    try:
        match = re.search(r"\{.*\}", raw, re.S)
        return json.loads(match.group(0)) if match else {"category": "OTHER", "response": "Manual review needed."}
    except:
        return {"category": "OTHER", "response": "Parsing error."}