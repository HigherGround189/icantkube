import os
import yaml
from pathlib import Path

CONFIG_PATH = Path("/config/services.yaml")

def load_apps() -> dict:
    if os.getenv("MODE") == "ci":
        return {}

    if not CONFIG_PATH.is_file():
        raise RuntimeError(f"{CONFIG_PATH} not found")

    with CONFIG_PATH.open("r") as f:
        data = yaml.safe_load(f) or {}

    return data.get("apps", {})
