# save as gemini_quickstart.py
import os
import sys
import json
import google.genai as genai   # alias; see docs for exact import name
# if import fails, try: from google import genai OR import google.generativeai as genai

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("Set GEMINI_API_KEY in your environment first.")
    sys.exit(1)

# Configure client (name depends on SDK version — quickstart shows the exact call)
genai.configure(api_key=API_KEY)

def ask_gemini(prompt_text, model="gemini-2.5-flash", max_tokens=400):
    """
    Simple wrapper to call Gemini and return text.
    Adjust the model name if your account has access to other family names.
    """
    # The exact method name varies slightly between SDK versions; check quickstart.
    response = genai.generate_text(
        model=model,
        prompt=prompt_text,
        max_output_tokens=max_tokens
    )
    # response format may be a dict/object; adjust per SDK. Here's a safe parse:
    if hasattr(response, "text"):
        return response.text
    try:
        return response["output"][0]["content"][0]["text"]
    except Exception:
        # fallback to printing raw response for debugging
        return str(response)

if __name__ == "__main__":
    system_msg = (
        "You are a concise shopping assistant. "
        "When given a list of store->product->price rows, return the cheapest match "
        "and one-sentence reasoning in JSON: {store, product, price, reason}."
    )
    user_query = (
        "Products: Coca-Cola 12-pack\n"
        "Data:\n"
        "Walmart: Coca-Cola 12-pack - $5.99\n"
        "Target: Coca-Cola 12-pack - $6.49\n"
        "Costco: Coca-Cola 12-pack - $5.49\n\n"
        "Answer in JSON."
    )

    prompt = f"SYSTEM: {system_msg}\n\nUSER: {user_query}"
    out = ask_gemini(prompt)
    print("=== GEMINI RESPONSE ===")
    print(out)
