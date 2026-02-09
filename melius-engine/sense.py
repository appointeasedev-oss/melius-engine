import os

ENGINE_DIR = "melius-engine"

def sense_repo():
    result = []
    for root, _, files in os.walk("."):
        if root.startswith(f"./{ENGINE_DIR}"):
            continue
        for f in files:
            result.append(os.path.join(root, f).lstrip("./"))
    return result
