# structures/persistence.py
import json
from pathlib import Path

DATA_PATH = Path("data.json")

def save_data(obj: dict):
    # Écriture atomique : écrire dans un fichier temporaire puis renommer
    tmp = DATA_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    tmp.replace(DATA_PATH)

def load_data() -> dict:
    if not DATA_PATH.exists():
        return {}
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)
