import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

# Set seeds for reproducible results
np.random.seed(42)
random.seed(42)

# Number of rows (events) to generate
n_rows: int = 8000

# Simulated date range
start_date: datetime = datetime(2024, 1, 1)
end_date: datetime = datetime(2024, 6, 30)
date_range_days: int = (end_date - start_date).days

# Production lines
lines: List[str] = ["BodyShop", "PaintShop", "FinalAssembly"]

# Stations per line
stations_per_line: Dict[str, List[str]] = {
    "BodyShop": ["BS_Weld_01", "BS_Weld_02", "BS_Trans_01", "BS_QC_01"],
    "PaintShop": ["PS_Prep_01", "PS_Paint_01", "PS_Oven_01", "PS_QC_01"],
    "FinalAssembly": ["FA_Conv_01", "FA_Station_01", "FA_Station_02", "FA_QC_01"],
}

# Fake robot IDs
robots: List[str] = [f"R{str(i).zfill(3)}" for i in range(1, 31)]

# Failure codes and categories
failure_codes: List[str] = ["E01", "E02", "E03", "E04", "E05", "E06"]
failure_categories: Dict[str, str] = {
    "E01": "mechanical",
    "E02": "electrical",
    "E03": "programming",
    "E04": "sensor",
    "E05": "material_supply",
    "E06": "other",
}


def random_timestamp() -> datetime:
    """Generate a random timestamp within the defined date range."""
    day_offset: int = random.randint(0, date_range_days)
    base_date: datetime = start_date + timedelta(days=day_offset)
    hour: int = random.randint(0, 23)
    minute: int = random.randint(0, 59)
    return base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)


def get_shift(hour: int) -> str:
    """Return the shift (morning/afternoon/night) given an hour (0–23)."""
    if 6 <= hour < 14:
        return "morning"
    elif 14 <= hour < 22:
        return "afternoon"
    else:
        return "night"


rows: List[Dict[str, Any]] = []

for i in range(n_rows):
    event_id: int = i + 1
    ts_start: datetime = random_timestamp()

    # Simulate duration using an exponential distribution (many short stops, few long ones)
    raw_duration: float = float(np.random.exponential(scale=25))
    # Clamp between 1 and 240 minutes
    duration: float = max(1.0, min(240.0, raw_duration))

    ts_end: datetime = ts_start + timedelta(minutes=duration)

    line: str = random.choice(lines)
    station: str = random.choice(stations_per_line[line])
    robot_id: str = random.choice(robots)

    # Different probabilities per failure code
    f_code: str = random.choices(
        failure_codes,
        weights=[0.25, 0.20, 0.20, 0.15, 0.15, 0.05],
    )[0]
    f_cat: str = failure_categories[f_code]

    shift: str = get_shift(ts_start.hour)

    # Approximate number of lost pieces as a function of duration
    raw_pieces: float = float(np.random.normal(loc=duration / 3, scale=2))
    pieces_lost: int = int(max(0.0, raw_pieces))

    # Small biases to make the dataset more realistic:
    # - slightly longer downtime at night
    # - slightly longer downtime in BodyShop
    if shift == "night":
        duration *= 1.1
    if line == "BodyShop":
        duration *= 1.05

    row: Dict[str, Any] = {
        "event_id": event_id,
        "timestamp_start": ts_start.isoformat(),
        "timestamp_end": ts_end.isoformat(),
        "line_id": line,
        "station_id": station,
        "robot_id": robot_id,
        "failure_code": f_code,
        "failure_category": f_cat,
        "downtime_minutes": round(duration, 1),
        "shift": shift,
        "pieces_lost": pieces_lost,
        "day_of_week": ts_start.strftime("%A"),
    }

    rows.append(row)

# Build DataFrame from all simulated rows
df = pd.DataFrame(rows)

# Save to CSV in the current folder
output_path: str = "downtime_events.csv"
df.to_csv(output_path, index=False)

print(f"File generated: {output_path}")
print(df.head())


