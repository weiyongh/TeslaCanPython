"""从 ASC 中提取 DBC 已命名的 Window Signal，并与采集动作对应。

输出规格与 extract_scripted_signals.py 一致：Markdown 报告、CSV 明细，
以及（存在候选时）排名第一的 Message 全 Signal 变化追踪。
"""

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import cantools

from extract_scripted_signals import (
    Candidate,
    Sample,
    normalized_value,
    parse_asc_line,
    parse_steps,
    score_candidates,
    write_csv,
    write_message_trace,
    write_report,
)


WINDOW_PATTERN = re.compile(r"window", re.IGNORECASE)


def inspect_asc(asc_path: Path) -> tuple[int, dict[int, Counter[int]]]:
    """统计 ASC 总帧数及每个 ID 的实际 DLC。"""
    frame_count = 0
    dlcs: dict[int, Counter[int]] = defaultdict(Counter)
    with asc_path.open("r", encoding="utf-8", errors="ignore") as source:
        for line in source:
            parsed = parse_asc_line(line)
            if parsed is None:
                continue
            _, frame_id, data = parsed
            frame_count += 1
            dlcs[frame_id][len(data)] += 1
    return frame_count, dlcs


def prepare_window_messages(
    database: cantools.database.Database,
    observed_dlcs: dict[int, Counter[int]],
) -> tuple[dict[int, cantools.database.can.Message], list[dict[str, Any]]]:
    """选择含 Window Signal 的 Message，并修正明显错误的 DBC DLC。"""
    messages: dict[int, cantools.database.can.Message] = {}
    coverage: list[dict[str, Any]] = []
    for message in database.messages:
        window_signals = [signal.name for signal in message.signals if WINDOW_PATTERN.search(signal.name)]
        if not window_signals:
            continue
        declared_dlc = message.length
        required_dlc = max(
            ((signal.start + signal.length + 7) // 8 for signal in message.signals),
            default=declared_dlc,
        )
        observed = observed_dlcs.get(message.frame_id, Counter())
        observed_dlc = observed.most_common(1)[0][0] if observed else None
        # ONYX DBC 的 UI_vehicleControl2 声明为 2 字节，但 Window Signal 位于
        # 第 3 字节且实车 ASC 为 8 字节。只在实际观测支持时扩大长度。
        decode_dlc = max(declared_dlc, required_dlc)
        if observed_dlc is not None and observed_dlc >= required_dlc:
            decode_dlc = observed_dlc
        message.length = decode_dlc
        # cantools 在加载时会编译位解码器；修改长度后必须刷新，否则仍会使用
        # 原先错误的 2-byte 布局解释 UI_windowRequest。
        message.refresh(strict=False)
        messages[message.frame_id] = message
        coverage.append({
            "frame_id": message.frame_id,
            "message": message.name,
            "declared_dlc": declared_dlc,
            "required_dlc": required_dlc,
            "observed_dlc": observed_dlc,
            "decode_dlc": decode_dlc,
            "signals": window_signals,
        })
    return messages, coverage


def decode_window_signals(
    asc_path: Path,
    messages: dict[int, cantools.database.can.Message],
) -> tuple[dict[tuple[int, str], list[Sample]], int]:
    """只解码名称含 window 的 Signal，保留首次值及变化点。"""
    traces: dict[tuple[int, str], list[Sample]] = defaultdict(list)
    decoded_count = 0
    with asc_path.open("r", encoding="utf-8", errors="ignore") as source:
        for line in source:
            parsed = parse_asc_line(line)
            if parsed is None:
                continue
            timestamp, frame_id, data = parsed
            message = messages.get(frame_id)
            if message is None or len(data) != message.length:
                continue
            try:
                decoded = message.decode(
                    data,
                    decode_choices=True,
                    scaling=True,
                    allow_truncated=False,
                    allow_excess=True,
                )
            except (ValueError, cantools.database.errors.DecodeError):
                continue
            decoded_count += 1
            for signal_name, value in decoded.items():
                if not WINDOW_PATTERN.search(signal_name):
                    continue
                sample = Sample(timestamp, normalized_value(value))
                values = traces[(frame_id, signal_name)]
                if not values or values[-1].value != sample.value:
                    values.append(sample)
    return traces, decoded_count


def append_window_summary(
    report_path: Path,
    coverage: list[dict[str, Any]],
    traces: dict[tuple[int, str], list[Sample]],
) -> None:
    lines = [
        "", "## Window DBC 覆盖与解码说明", "",
        "仅分析 Signal 名称包含 `window`（忽略大小写）的 DBC 字段。",
        "当 DBC DLC 小于 Signal 所需长度、且 ASC 的实际 DLC 足够时，程序使用 ASC DLC 解码并在下表标记。", "",
        "| CAN ID | Message | DBC DLC | Signal所需DLC | ASC DLC | 解码DLC | Window Signal数 | 变化Signal数 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in coverage:
        changed = sum(
            len(samples) > 1
            for (frame_id, _), samples in traces.items()
            if frame_id == item["frame_id"]
        )
        observed = "—" if item["observed_dlc"] is None else str(item["observed_dlc"])
        lines.append(
            f'| 0x{item["frame_id"]:X} | {item["message"]} | {item["declared_dlc"]} | '
            f'{item["required_dlc"]} | {observed} | {item["decode_dlc"]} | '
            f'{len(item["signals"])} | {changed} |'
        )
    lines.extend(["", "### 未变化或仅有初始值的 Window Signal", ""])
    static = []
    for (frame_id, signal_name), samples in sorted(traces.items()):
        if len(samples) == 1:
            static.append(f"- `0x{frame_id:X}` / `{signal_name}`：`{samples[0].value}`")
    if static:
        lines.extend(static)
    else:
        lines.append("- 无。")
    lines.extend([
        "", "> DBC 未收录的 CAN ID（例如本次无 DBC 分析得到的 `0x1FA`）不会被强行命名，",
        "> 也不会混入本报告的 DBC Signal 候选排名。", "",
    ])
    with report_path.open("a", encoding="utf-8") as target:
        target.write("\n".join(lines))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="根据采集脚本，从 ASC 提取 ONYX DBC 中已命名的 Window Signal"
    )
    parser.add_argument("script", type=Path, help="标准采集脚本 txt 文件")
    parser.add_argument("asc", type=Path, help="原始 CAN ASC 文件")
    parser.add_argument("dbc", type=Path, help="DBC 文件（支持 .dbc 或 .dbc.txt）")
    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="输出目录")
    parser.add_argument("--tolerance", type=float, default=5.0, help="动作点前后匹配容差秒数")
    parser.add_argument("--top", type=int, default=10, help="最多输出候选 Signal 数")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    for path in (args.script, args.asc, args.dbc):
        if not path.is_file():
            raise FileNotFoundError(f"输入文件不存在：{path}")
    if args.tolerance <= 0 or args.top <= 0:
        raise ValueError("--tolerance 和 --top 必须大于 0")

    steps = parse_steps(args.script)
    actions = [step for step in steps if step.is_action]
    if not actions:
        raise ValueError("采集脚本中没有识别出关键动作")
    database = cantools.database.load_file(args.dbc, database_format="dbc", strict=False)
    frame_count, observed_dlcs = inspect_asc(args.asc)
    messages, coverage = prepare_window_messages(database, observed_dlcs)
    traces, decoded_count = decode_window_signals(args.asc, messages)
    candidates: list[Candidate] = score_candidates(
        traces, database, actions, args.tolerance, exclude_pattern=None
    )[: args.top]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = args.asc.stem
    report_path = args.output_dir / f"{stem}_Window关键步骤信号报告.md"
    csv_path = args.output_dir / f"{stem}_Window关键步骤信号明细.csv"
    write_report(
        report_path, args.script, args.asc, args.dbc, steps, candidates,
        args.tolerance, frame_count, decoded_count,
    )
    append_window_summary(report_path, coverage, traces)
    write_csv(csv_path, candidates)

    trace_path: Path | None = None
    if candidates:
        trace_message = database.get_message_by_frame_id(candidates[0].frame_id)
        trace_path = args.output_dir / (
            f"asc_dbc_window_trace_{stem}_0x{trace_message.frame_id:X}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        # 排除所有非 Window Signal，使追踪文件聚焦车窗字段。
        non_window_names = [
            re.escape(signal.name) for signal in trace_message.signals
            if not WINDOW_PATTERN.search(signal.name)
        ]
        exclude = re.compile("^(?:" + "|".join(non_window_names) + ")$") if non_window_names else None
        write_message_trace(
            trace_path, args.asc, trace_message,
            min(step.time for step in steps), max(step.time for step in steps), exclude,
        )

    print(f"采集步骤：{len(steps)}，关键动作：{len(actions)}")
    print(f"ASC 数据帧：{frame_count}，Window Message：{len(messages)}，成功解码帧：{decoded_count}")
    print(f"候选 Window Signal：{len(candidates)}")
    print(f"报告：{report_path}")
    print(f"明细：{csv_path}")
    if trace_path:
        print(f"Message追踪：{trace_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
