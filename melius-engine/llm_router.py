import os
import random
import requests
import time
from datetime import datetime

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Model priority: try in order
MODELS = [
    "arcee-ai/trinity-large-preview:free",
    "openrouter/pony-alpha"
]

# Multiple keys for fallback
OPENROUTER_KEYS = [
    os.getenv("OPENROUTER_KEY_1"),
    os.getenv("OPENROUTER_KEY_2"),
    os.getenv("OPENROUTER_KEY_3"),
    os.getenv("OPENROUTER_KEY_4"),
    os.getenv("OPENROUTER_KEY_5"),
]

# Safety limits
REQUEST_TIMEOUT = 60        # per request
MAX_TOTAL_TIME = 180        # total seconds allowed for all attempts

def _log(msg):
    ts = datetime.utcnow().isoformat()
    print(f"[LLM {ts}] {msg}", flush=True)

def call_llm(messages):
    keys = [k for k in OPENROUTER_KEYS if k]
    if not keys:
        raise RuntimeError("No OpenRouter API keys available")

    start_time = time.time()
    last_error = None

    _log(f"Starting LLM call | models={MODELS} | keys={len(keys)}")

    for model in MODELS:
        random.shuffle(keys)
        for api_key in keys:

            elapsed = time.time() - start_time
            if elapsed > MAX_TOTAL_TIME:
                raise RuntimeError(
                    f"LLM aborted after {MAX_TOTAL_TIME}s. "
                    f"Last error: {last_error}"
                )

            _log(f"Trying model='{model}' with key ending ...{api_key[-4:]}")

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
                    timeout=REQUEST_TIMEOUT
                )

                if response.status_code != 200:
                    last_error = f"{response.status_code}: {response.text}"
                    _log(f"Failed ({last_error})")
                    continue

                data = response.json()

                if "choices" not in data or not data["choices"]:
                    last_error = f"Invalid response format: {data}"
                    _log("Invalid response structure")
                    continue

                content = data["choices"][0]["message"]["content"]

                if not content or not content.strip():
                    last_error = "Empty response content"
                    _log("Empty response")
                    continue

                _log(f"Success with model='{model}'")
                return content.strip()

            except requests.exceptions.Timeout:
                last_error = "Request timeout"
                _log("Request timed out")
            except Exception as e:
                last_error = str(e)
                _log(f"Exception: {last_error}")

            time.sleep(1)

    raise RuntimeError(
        f"All models and keys failed. Last error: {last_error}"
    )
