#!/usr/bin/env python3
"""Split the combined TM3-007/008 ASC capture into analysis inputs."""

from __future__ import annotations

import re
from pathlib import Path


SOURCE = Path("input/can_20260831113240开关门采集.asc")
TM3_007 = Path("input/can_20260831113240_TM3-007_开锁开门完整上电采集.asc")
TM3_008 = Path("input/can_20260831123400_TM3-008_关门落锁完整下电采集.asc")

TM3_007_START = 0.0
TM3_007_END = 130.0
TM3_008_END = 792.6812
TM3_008_START = TM3_008_END - 600.0

FRAME_RE = re.compile(r"^(\d+\.\d+)(\s+.*)$")


def header(label: str, capture_date: str, source_start: float, source_end: float) -> list[str]:
    return [
        f"date {capture_date}\n",
        "base hex timestamps absolute\n",
        "// version 7.0.0\n",
        f"// Derived analysis input: {label}\n",
        f"// Source: {SOURCE.name}\n",
        f"// Source interval: {source_start:.6f} s to {source_end:.6f} s\n",
        "// Output timestamps rebased to 0.000000 s\n",
    ]


def write_segment(
    target: Path, label: str, capture_date: str, start: float, end: float
) -> tuple[int, float, float]:
    count = 0
    first_source_time = float("nan")
    last_source_time = float("nan")
    with SOURCE.open("r", encoding="utf-8", errors="strict") as src, target.open(
        "w", encoding="utf-8", newline=""
    ) as dst:
        dst.writelines(header(label, capture_date, start, end))
        for line in src:
            match = FRAME_RE.match(line)
            if not match:
                continue
            source_time = float(match.group(1))
            if source_time < start or source_time > end:
                continue
            rebased = source_time - start
            dst.write(f"{rebased:.6f}{match.group(2)}\n")
            if count == 0:
                first_source_time = source_time
            last_source_time = source_time
            count += 1
        dst.write("End Triggerblock\n")
    return count, first_source_time, last_source_time


def main() -> None:
    results = [
        (
            TM3_007,
            write_segment(
                TM3_007,
                "TM3-007",
                "Mon Aug 31 11:32:40 AM 2026",
                TM3_007_START,
                TM3_007_END,
            ),
        ),
        (
            TM3_008,
            write_segment(
                TM3_008,
                "TM3-008",
                "Mon Aug 31 12:34:00 PM 2026",
                TM3_008_START,
                TM3_008_END,
            ),
        ),
    ]
    for path, (count, first_time, last_time) in results:
        print(f"{path}: {count} frames, source {first_time:.6f}..{last_time:.6f} s")


if __name__ == "__main__":
    main()
