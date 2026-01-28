import os


def config_path():
    return os.path.join(os.path.expanduser("~"), ".config", "gtw", "config")


def load_default_cmd():
    if os.environ.get("GTW_CMD"):
        return os.environ.get("GTW_CMD").strip()
    path = config_path()
    if not os.path.exists(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                return line
    except OSError:
        return ""
    return ""
