import time
import re
import unicodedata
import threading
from ai.rag import retrieve_examples
from ai.hf_client import classify_with_llm_detailed
from ai.schemas import HelpdeskTicket
from ai.sentiment import detect_sentiment

# Clean text for consistency
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    return text.strip()

# Thread-safe rate limiter for model calls
class RobustAnalyzer:
    def __init__(self):
        self.lock = threading.Lock()
        self.last_call = 0
        self.min_interval = 3.0
        self.consecutive_account = 0  # Track consecutive ACCOUNT classifications
    
    def wait(self):
        with self.lock:
            current_time = time.time()
            elapsed = current_time - self.last_call
            wait_time = self.min_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            self.last_call = time.time()

_analyzer = RobustAnalyzer()

# Main pipeline function
def full_ticket_analysis(ticket_text: str) -> dict:
    start = time.time()
    ticket_text = clean_text(ticket_text)
    
    try:
        # Rate limiting
        _analyzer.wait()

        # STEP 1: RAG Specialist finds similar cases
        examples = retrieve_examples(ticket_text, top_k=3)

        # STEP 2: Sentiment Specialist checks the mood
        sentiment = detect_sentiment(ticket_text)

        # STEP 3: LLM Specialist does the classification
        # We pass the message AND the examples. The prompt is built INSIDE this call.
        ai_result = classify_with_llm_detailed(ticket_text, examples=examples)

        # STEP 4: Business Logic (The Boss's final checks)
        corrected = _force_category_correction(ticket_text, ai_result)
        final_cat = _ensemble_decision(ticket_text, corrected["category"])
        
        # Merge all findings
        corrected["category"] = final_cat
        corrected["sentiment"] = sentiment

        # STEP 5: Production-grade validation
        validated = HelpdeskTicket(**corrected)
        final = validated.model_dump()

        return final

    except Exception as e:
        print(f"❌ AI analysis failed: {e}")
        return _keyword_fallback(ticket_text)
    finally:
        print(f"⏱️ Total time: {time.time() - start:.2f}s")
        
# Correction logic for common misclassifications
def _force_category_correction(original_text: str, ai_result: dict) -> dict:
    text_lower = original_text.lower()
    cat = ai_result.get("category", "").upper()

    # If refund/charge/payment words appear → BLLLING dominates ORDER
    if cat == "ORDER" and any(w in text_lower for w in ["refund", "payment", "charge", "invoice", "card"]):
        ai_result["category"] = "BILLING"

    # If words like 'promo', 'discount', 'coupon' appear → BILLING
    if any(w in text_lower for w in ["promo", "coupon", "discount", "code"]):
        ai_result["category"] = "BILLING"

    # If invalid card, declined, etc. → BILLING
    if any(w in text_lower for w in ["card", "declined", "payment failed", "invalid card"]):
        ai_result["category"] = "BILLING"

    # Refunds from cancelled orders → prefer BILLING
    if "refund" in text_lower and "order" in text_lower:
        ai_result["category"] = "BILLING"

    return ai_result
# Ensemble decision logic
def _ensemble_decision(text: str, ai_cat: str) -> str:
    text_lower = text.lower()
    keyword_cat = _get_expected_category(text_lower)

    if ai_cat != keyword_cat:
        # Bias toward billing in common edge cases
        if any(w in text_lower for w in ["refund", "charge", "promo", "card", "invoice"]):
            return "BILLING"
        # Bias toward order in delivery keywords
        if any(w in text_lower for w in ["order", "shipping", "package", "track"]):
            return "ORDER"
        # Bias toward account in login-related
        if any(w in text_lower for w in ["login", "password", "account", "email", "locked"]):
            return "ACCOUNT"
        return keyword_cat
    return ai_cat



# Keyword-level sanity check
def _get_expected_category(text_lower: str) -> str:
    if any(word in text_lower for word in ["order", "delivery", "shipping", "package", "track", "arrive", "damaged"]):
        return "ORDER"
    elif any(word in text_lower for word in ["charge", "payment", "bill", "refund", "price", "invoice", "money", "fee"]):
        return "BILLING"
    elif any(word in text_lower for word in ["subscription", "cancel", "renew", "membership", "plan"]):
        return "SUBSCRIPTION"
    elif any(word in text_lower for word in ["crash", "error", "technical", "bug", "slow", "website", "app", "loading"]):
        return "TECHNICAL"
    elif any(word in text_lower for word in ["login", "password", "account", "email", "username", "locked", "sign in"]):
        return "ACCOUNT"
    else:
        return "OTHER"


# Keyword-only fallback if LLM fails
def _keyword_fallback(ticket_text: str) -> dict:
    text_lower = ticket_text.lower()
    category = _get_expected_category(text_lower)
    
    responses = {
        "ACCOUNT": "I understand you're having account issues. Let me help you resolve this.",
        "ORDER": "I see you have an order-related concern. Let me look into this for you.",
        "BILLING": "I understand your billing concern. Let me check this for you.",
        "SUBSCRIPTION": "I can help with your subscription question.",
        "TECHNICAL": "I understand you're experiencing technical difficulties.",
        "OTHER": "Thank you for your message. I'll help you with this."
    }
    
    print(f"🔄 Using keyword fallback: {category}")
    
    return {
        "category": category,
        "subcategory": "general",
        "summary": f"User reported: {ticket_text[:80]}...",
        "response": responses.get(category, "Thank you for your message. We'll assist you shortly.")
    }
