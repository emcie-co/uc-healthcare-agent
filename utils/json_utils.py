import json
from pathlib import Path
from typing import Dict, Any, List

def _load_data(path: Path) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise TypeError("Expected a list of dictionaries")
    return data

def _update_data(path: Path, new_data:List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(new_data, file, indent=4)
    return new_data