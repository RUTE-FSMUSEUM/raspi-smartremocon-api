import json

def get(path):
    with open(path) as f:
        version_info = json.load(f)
    major, minor, suffix = version_info["MAJOR"], version_info["MINOR"], version_info["SUFFIX"]
    return f"v{major}.{minor}.{suffix}"