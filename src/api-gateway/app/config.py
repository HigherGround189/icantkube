import yaml
from pathlib import Path

CONFIG_PATH = Path("services.yaml")

def load_services() -> dict:
    if not CONFIG_PATH.exists():
        raise RuntimeError("services.yaml not found")

    with CONFIG_PATH.open() as f:
        data = yaml.safe_load(f)

    return data.get("services", {})
