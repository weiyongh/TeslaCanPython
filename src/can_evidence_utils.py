"""Small, experiment-neutral CAN evidence primitives used by TM3 reports."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class TimedValue:
    time_s: float
    value: float


def latest_past_sample(samples: Sequence[TimedValue], event_time_s: float) -> TimedValue | None:
    """Return the latest sample at or before the event (never look forward)."""
    eligible = (sample for sample in samples if sample.time_s <= event_time_s)
    return max(eligible, key=lambda sample: sample.time_s, default=None)


def signal_age_s(event_time_s: float, sample: TimedValue | None) -> float | None:
    return None if sample is None else event_time_s - sample.time_s


def same_frame_pair(frame: Mapping[str, float], request_key: str, actual_key: str) -> tuple[float, float, float]:
    """Compare request and actual decoded from the same CAN frame."""
    request = float(frame[request_key])
    actual = float(frame[actual_key])
    return request, actual, actual - request


def pack_power_kw_same_frame(frame: Mapping[str, float], voltage_key: str, current_key: str) -> float:
    """Calculate Pack power only from voltage/current decoded from one frame."""
    return float(frame[voltage_key]) * float(frame[current_key]) / 1000.0


def continuous_windows(times_s: Iterable[float], max_gap_s: float) -> list[tuple[float, float, int]]:
    """Split ordered sample times at gaps larger than max_gap_s."""
    times = sorted(float(x) for x in times_s)
    if not times:
        return []
    windows: list[tuple[float, float, int]] = []
    start = previous = times[0]
    count = 1
    for current in times[1:]:
        if current - previous > max_gap_s:
            windows.append((start, previous, count))
            start, count = current, 1
        else:
            count += 1
        previous = current
    windows.append((start, previous, count))
    return windows


def dbc_field_readability(*, frame_count: int, decoded_count: int, invalid_count: int = 0,
                          dbc_dlc: int | None = None, asc_dlc: int | None = None) -> str:
    if frame_count == 0:
        return "NO_FRAME"
    if dbc_dlc is not None and asc_dlc is not None and asc_dlc < dbc_dlc:
        return "DLC_MISMATCH"
    if decoded_count == 0:
        return "UNREADABLE"
    if invalid_count:
        return "READABLE_WITH_INVALID"
    if decoded_count < frame_count:
        return "PARTIAL"
    return "READABLE"


def asc_integrity(path: Path, *, chunk_size: int = 1024 * 1024) -> dict[str, object]:
    digest = hashlib.sha256()
    size = 0
    line_count = 0
    last_byte = b""
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
            size += len(chunk)
            line_count += chunk.count(b"\n")
            last_byte = chunk[-1:]
    if size and last_byte != b"\n":
        line_count += 1
    return {
        "path": str(path), "size_bytes": size, "line_count": line_count,
        "sha256": digest.hexdigest(), "readable": True,
    }
