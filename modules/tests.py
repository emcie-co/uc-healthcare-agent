from typing import Any, Dict, List
from datetime import datetime


def get_data()->Dict[str,Any]:
    full_data:Dict[str, Any] = {
        "name": "John Doe",
        "items": [
            {"name": "item1", "price": 10.9},
            {"name": "item2", "price": 20.5},
            {"name": "item3", "price": 30.8},
        ],
        "address": "123 Main St, Springfield, IL 62701",
    }
    
    items:List[Dict[str, Any]]  = full_data["items"]
    item3 = next((entry for entry in items if entry["name"] == "item3"), None)
    
    return {
        "items": items,
        "item3": item3
    }
    
# slots, slot3 = get_data().values()
# slot3["price"] = 35.0
# print(slots)

today = datetime.today()
print(today)