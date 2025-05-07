
from datetime import datetime
from typing import List, Optional, TypedDict

class SlotItem(TypedDict):
    date: str
    time: Optional[str]
    times: Optional[List[str]]

def _sort_datetime(slots: List[SlotItem]) -> List[SlotItem]:
    """Sorts availability list by date, then by time within each date."""
    sorted_items = sorted(
        slots,
        key=lambda x: (
            datetime.strptime(x["date"], "%Y-%m-%d"),
            datetime.strptime(
                # prioritize: times[0] if present, else time, else max
                x["times"][0], "%H:%M"
            ) if "times" in x and x["times"]
            else datetime.strptime(
                x["time"], "%H:%M"
            ) if "time" in x and x["time"]
            else datetime.max
        )
    )
    # If 'times' is present, sort its list too
    for entry in sorted_items:
        if "times" in entry and isinstance(entry["times"], list):
            entry["times"].sort(key=lambda t: datetime.strptime(t, "%H:%M"))
    return sorted_items


def _format_datetime(date_input: datetime) -> List[str]:
    _date = date_input.strftime("%Y-%m-%d")
    _time = date_input.strftime("%H:%M")

    return [_date, _time]