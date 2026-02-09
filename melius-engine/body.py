import os
import json
import random
from datetime import datetime

from sense import sense_repo
from eyes import read_files
from hands import write_files
from llm_router import call_llm
from zson import parse, dump, ZSONError

MEMORY_PATH = "melius-engine/memory/chat_memory.json"
LOG_DIR = "melius-engine/log"

os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def load_memory():
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_memory(mem):
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2)

def strict_llm(messages, required_keys):
    raw = call_llm(messages)
    data = parse(raw)
    for k in required_keys:
        if k not in data:
            raise ZSONError(f"Missing key: {k}")
    return data

def run():
    memory = load_memory()

    # STEP 1: SENSE
    files = sense_repo()
    memory.append({
        "role": "system",
        "content": dump({"external_files": files})
    })

    # STEP 2: ASK WHAT TO READ
    read_request = strict_llm(
        memory + [{
            "role": "system",
            "content": (
                "Reply STRICTLY in JSON.\n"
                "Schema:\n"
                "{ \"read_files\": [\"path/file\"] }\n"
                "No extra text."
            )
        }],
        ["read_files"]
    )

    # STEP 3: READ FILES
    file_data = read_files(read_request["read_files"])

    # STEP 4: ASK FOR IMPROVEMENT
    improve_payload = {
        "instruction": (
            "Improve code quality, structure, safety.\n"
            "Rules:\n"
            "- Return FULL code\n"
            "- You may add new files\n"
            "- STRICT JSON ONLY\n"
            "- Schema: { \"files\": { \"path\": \"code\" } }"
        ),
        "files": file_data
    }

    improved = strict_llm(
        memory + [{
            "role": "system",
            "content": dump(improve_payload)
        }],
        ["files"]
    )

    # STEP 5: WRITE FILES
    write_files(improved["files"])

    # STEP 6: SUMMARY
    summary = strict_llm(
        memory + [{
            "role": "system",
            "content": (
                "Describe improvements made.\n"
                "STRICT JSON ONLY.\n"
                "Schema: { \"summary\": \"text\" }"
            )
        }],
        ["summary"]
    )

    # STEP 7: LOG
    improvement_id = random.randint(1000000, 9999999)
    log_path = f"{LOG_DIR}/log_{improvement_id}.json"

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump({
            "id": improvement_id,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": summary["summary"]
        }, f, indent=2)

    memory.append({"role": "assistant", "content": dump(summary)})
    save_memory(memory)

if __name__ == "__main__":
    run()
