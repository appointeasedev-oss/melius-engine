import os
import random
import requests
import time

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Priority order: first model is primary, others are fallbacks
MODELS = [
    "arcee-ai/trinity-large-preview:free",
    "openrouter/pony-alpha"
]

# Multiple keys for quota / failure fallback
OPENROUTER_KEYS = [
    os.getenv("OPENROUTER_KEY_1"),
    os.getenv("OPENROUTER_KEY_2"),
    os.getenv("OPENROUTER_KEY_3"),
    os.getenv("OPENROUTER_KEY_4"),
    os.getenv("OPENROUTER_KEY_5"),
]

def call_llm(messages):
    keys = [k for k in OPENROUTER_KEYS if k]
    if not keys:
        raise RuntimeError("No OpenRouter API keys available")

    last_error = None

    # Try every model × every key until success
    for model in MODELS:
        random.shuffle(keys)
        for api_key in keys:
            try:
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0
                }

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/melius-engine",
                    "X-Title": "melius-engine"
                }

                response = requests.post(
                    OPENROUTER_URL,
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                if response.status_code != 200:
                    last_error = response.text
                    continue

                data = response.json()

                if "choices" not in data or not data["choices"]:
                    last_error = f"Invalid response format: {data}"
                    continue

                content = data["choices"][0]["message"]["content"]
                if not content:
                    last_error = "Empty LLM response"
                    continue

                return content.strip()

            except Exception as e:
                last_error = str(e)
                time.sleep(1)

    raise RuntimeError(f"All OpenRouter models and keys failed. Last error: {last_error}")
