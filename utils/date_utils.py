
from datetime import datetime
from typing import List, TypedDict

class AvailabilityItem(TypedDict):
    date: str
    times: List[str]
    
def _sort_datetime(availability: List[AvailabilityItem]) -> List[AvailabilityItem]:
    """Sorts availability list by date, then by time within each date."""
    # First, sort the main list by date and first available time
    sorted_availability = sorted(
        availability, 
        key=lambda x: (
            datetime.strptime(x["date"], "%Y-%m-%d"), 
            datetime.strptime(x["times"][0], "%H:%M") if x["times"] else datetime.max
        )
    )
    # Then, ensure times within each date are sorted
    for entry in sorted_availability:
        entry["times"].sort(key=lambda t: datetime.strptime(t, "%H:%M"))

    return sorted_availability

def _sorted_datetimes(availabilities: List[AvailabilityItem]) -> List[AvailabilityItem]:
    """Sorts availability list by date and time."""
    
    for entry in availabilities:
        entry["times"].sort(key=lambda t: datetime.strptime(t, "%H:%M"))
    sorted_slots = sorted(availabilities, key=lambda slots: datetime.strptime(slots["date"], "%Y-%m-%d"))
    
    return sorted_slots

def _format_datetime(date_input: datetime) -> List[str]:
    _date = date_input.strftime("%Y-%m-%d")
    _time = date_input.strftime("%H:%M")

    return [_date, _time]

# data = [
#     {
#         "date": "2025-03-30",
#         "times": ["10:30", "11:30", "12:30"]
#     },
#     {
#         "date": "2025-03-31",
#         "times": ["14:30", "15:30", "16:30"]
#     },
#     {
#         "date": "2025-04-01",
#         "times": ["09:30", "10:30", "11:30", "12:30"]
#     },
#     {
#         "date": "2025-04-02",
#         "times": ["16:30", "17:30", "18:30", "19:30"]
#     },
#     {
#         "date": "2025-04-03",
#         "times": ["09:30", "10:30", "11:30", "12:30"]
#     },
#     {
#         "date": "2025-04-04",
#         "times": ["10:30", "11:30", "12:30"]
#     }
# ]

# print(_sorted_datetimes(data))