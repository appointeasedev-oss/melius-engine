def read_files(paths):
    data = {}
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data[path] = f.read()
        except Exception as e:
            data[path] = f"ERROR: {str(e)}"
    return data
