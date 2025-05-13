from typing import Any, Dict, List, Optional


def find_entity(data: List[Dict[str,Any]], role: str, key: str, value: str) -> Optional[Dict[str,Any]]:
    return next((entry[role] for entry in data if entry[role][key] == value), None)

def match_availability(availabilities: List[Dict[str,Any]], _date: str, _time: str) -> Optional[Dict[str, Any]]:
    return next((entry for entry in availabilities if entry["date"] == _date and _time in entry["times"]), None)

def match_slot(availabilities: List[Dict[str,Any]], _date: str, _time: str) -> Optional[Dict[str, Any]]:
    return next((entry for entry in availabilities if entry["date"] == _date and entry["times"] == _time), None)

def remove_time_from_availability(availabilities: List[Dict[str,Any]], slot: Dict[str,Any], _time: str)->None:
    if slot["times"] and len(slot["times"]) > 1:
        slot["times"].remove(_time)
    else:
        availabilities.remove(slot)
    return None