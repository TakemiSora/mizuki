from datetime import datetime

def sint(txt: str | None) -> int | None:
    return int(txt) if txt else None

def siso(txt: str | None) -> datetime | None:
    return datetime.fromisoformat(txt) if txt else None