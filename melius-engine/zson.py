import json

class ZSONError(Exception):
    pass

def parse(raw: str):
    try:
        return json.loads(raw)
    except Exception as e:
        raise ZSONError(f"Invalid ZSON: {e}")

def dump(data):
    return json.dumps(data, indent=2, ensure_ascii=False)
