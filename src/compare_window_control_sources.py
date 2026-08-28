"""比较物理按钮与 App 通风两份 ASC，寻找共同的车窗执行过程候选。"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cantools

from analyze_driver_window_button import rank_motion_activity, raw_id_trace
from analyze_window_vent import collect
from extract_scripted_signals import parse_steps


def build_motion_windows(steps):
    """从关键动作到其后的第一个稳定状态记录建立执行窗口。"""
    windows = []
    for index, step in enumerate(steps):
        if not step.is_action or "松开" in step.title:
            continue
        stable = next((item for item in steps[index + 1:] if "稳定状态" in item.title), None)
        if stable is None or stable.time <= step.time:
            continue
        if "下降" in step.title or "打开" in step.title:
            direction = "打开/下降"
        elif "上升" in step.title or "关闭" in step.title:
            direction = "关闭/上升"
        else:
            direction = "未知"
        windows.append((step.time, stable.time, direction))
    return windows


def message_info(database, frame_id):
    try:
        message = database.get_message_by_frame_id(frame_id)
        return message.name, "DBC已定义"
    except KeyError:
        return "—", "DBC未收录"


def compare_rows(physical_rows, app_rows, database):
    physical = {(row["frame_id"], row["bit"]): row for row in physical_rows}
    app = {(row["frame_id"], row["bit"]): row for row in app_rows}
    common = []
    for key in physical.keys() & app.keys():
        p_row, a_row = physical[key], app[key]
        name, dbc_status = message_info(database, key[0])
        common.append({
            "score": min(p_row["score"], a_row["score"]),
            "frame_id": key[0], "bit": key[1], "byte": key[1] // 8,
            "bit_in_byte": key[1] % 8, "message": name, "dbc_status": dbc_status,
            "physical_hits": p_row["hits"], "physical_enrichment": p_row["enrichment"],
            "physical_inside": p_row["inside"], "physical_outside": p_row["outside"],
            "app_hits": a_row["hits"], "app_enrichment": a_row["enrichment"],
            "app_inside": a_row["inside"], "app_outside": a_row["outside"],
        })
    common.sort(key=lambda row: (-row["score"], row["frame_id"], row["bit"]))
    grouped = {}
    for row in common:
        group = grouped.setdefault(row["frame_id"], {
            "frame_id": row["frame_id"], "message": row["message"],
            "dbc_status": row["dbc_status"], "score": row["score"],
            "best_bit": row["bit"], "common_bits": 0,
            "physical_hits": row["physical_hits"], "app_hits": row["app_hits"],
            "physical_enrichment": row["physical_enrichment"],
            "app_enrichment": row["app_enrichment"],
        })
        group["common_bits"] += 1
    groups = sorted(grouped.values(), key=lambda row: (-row["score"], row["frame_id"]))
    return common, groups


def write_csv(path, rows):
    columns = ["rank", "score", "can_id", "message", "dbc_status", "byte", "bit_in_byte",
               "physical_hits", "physical_enrichment", "physical_inside", "physical_outside",
               "app_hits", "app_enrichment", "app_inside", "app_outside"]
    with path.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=columns)
        writer.writeheader()
        for rank, row in enumerate(rows, 1):
            writer.writerow({"rank": rank, "score": f'{row["score"]:.3f}',
                             "can_id": f'0x{row["frame_id"]:X}', "message": row["message"],
                             "dbc_status": row["dbc_status"], "byte": row["byte"],
                             "bit_in_byte": row["bit_in_byte"], "physical_hits": row["physical_hits"],
                             "physical_enrichment": f'{row["physical_enrichment"]:.3f}',
                             "physical_inside": row["physical_inside"], "physical_outside": row["physical_outside"],
                             "app_hits": row["app_hits"], "app_enrichment": f'{row["app_enrichment"]:.3f}',
                             "app_inside": row["app_inside"], "app_outside": row["app_outside"]})


def trace_summary(stats):
    frame_count, dlcs, first, changes = stats
    return frame_count, ", ".join(str(dlc) for dlc in dlcs), first, changes


def write_report(path, args, physical_windows, app_windows, physical_count, app_count,
                 common, groups, physical_1fa, app_1fa):
    lines = [
        "# 物理按钮与 App 通风交叉分析报告", "",
        f"- 物理按钮脚本：`{args.physical_script}`", f"- 物理按钮 ASC：`{args.physical_asc}`",
        f"- App 通风脚本：`{args.app_script}`", f"- App 通风 ASC：`{args.app_asc}`",
        f"- DBC：`{args.dbc}`", f"- 物理 ASC 帧数：{physical_count:,}", f"- App ASC 帧数：{app_count:,}", "",
        "## 分析原则", "",
        "物理按钮和 App 是不同的请求入口，但共同使用车窗执行机构。仅保留在两份 ASC 的运动窗口内均显著富集的 `CAN ID + bit`。", "",
        "## 运动窗口", "", "### 物理按钮", "", "| 方向 | 开始(s) | 结束(s) |", "|---|---:|---:|",
    ]
    for start, end, direction in physical_windows:
        lines.append(f"| {direction} | {start:g} | {end:g} |")
    lines.extend(["", "### App 通风", "", "| 方向 | 开始(s) | 结束(s) |", "|---|---:|---:|"])
    for start, end, direction in app_windows:
        lines.append(f"| {direction} | {start:g} | {end:g} |")
    lines.extend([
        "", "## 共同执行过程候选 CAN ID", "",
        "| 排名 | CAN ID | DBC Message | DBC状态 | 最佳Byte.Bit | 共同bit数 | 物理命中/富集 | App命中/富集 |",
        "|---:|---:|---|---|---:|---:|---:|---:|",
    ])
    for rank, row in enumerate(groups, 1):
        lines.append(
            f'| {rank} | 0x{row["frame_id"]:X} | {row["message"]} | {row["dbc_status"]} | '
            f'B{row["best_bit"]//8}.b{row["best_bit"]%8} | {row["common_bits"]} | '
            f'{row["physical_hits"]}/{len(physical_windows)}，{row["physical_enrichment"]:.1f}× | '
            f'{row["app_hits"]}/{len(app_windows)}，{row["app_enrichment"]:.1f}× |'
        )
    lines.extend([
        "", "## 共同 bit 明细", "",
        "| 排名 | CAN ID | Byte.Bit | 物理窗口内/外翻转 | 物理富集 | App窗口内/外翻转 | App富集 |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for rank, row in enumerate(common, 1):
        lines.append(
            f'| {rank} | 0x{row["frame_id"]:X} | B{row["byte"]}.b{row["bit_in_byte"]} | '
            f'{row["physical_inside"]}/{row["physical_outside"]} | {row["physical_enrichment"]:.1f}× | '
            f'{row["app_inside"]}/{row["app_outside"]} | {row["app_enrichment"]:.1f}× |'
        )
    lines.extend([
        "", "## 0x1FA 对照", "",
        "| 数据 | 初始Payload | 变化次数 | 变化时间与方向 |", "|---|---|---:|---|",
    ])
    for label, stats in (("物理按钮", physical_1fa), ("App通风", app_1fa)):
        _, _, first, changes = trace_summary(stats)
        initial = "—" if first is None else first[1].hex(" ").upper()
        detail = "；".join(f'{time:.4f}s {before.hex(" ").upper()}→{after.hex(" ").upper()}'
                          for time, before, after in changes) or "无"
        lines.append(f"| {label} | {initial} | {len(changes)} | {detail} |")
    lines.extend([
        "", "## 结论边界", "",
        "- `0x545`、`0x2C2` 是当前最值得继续做字段轨迹分析的共同执行过程候选。",
        "- `0x2B4` 虽然共同响应，但 DBC 将其定义为 `PCS_dcdcBusStatus`，优先视为车窗电机负载的伴随电源变化。",
        "- 共同活动不能自动区分真实数据、计数器与校验和，下一步仍需组合 8/10/12/16 bit 字段并检查升降方向。",
        "- `0x1FA` 在 App 数据中完整跟随四次通风/关闭，但在物理数据中只跟随部分过程，因此只能作为汇总状态待验证。", "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8-sig")


def main() -> int:
    parser = argparse.ArgumentParser(description="比较物理按钮与 App 通风的共同车窗执行过程候选")
    parser.add_argument("physical_script", type=Path)
    parser.add_argument("physical_asc", type=Path)
    parser.add_argument("app_script", type=Path)
    parser.add_argument("app_asc", type=Path)
    parser.add_argument("dbc", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()
    for source in (args.physical_script, args.physical_asc, args.app_script, args.app_asc, args.dbc):
        if not source.is_file():
            raise FileNotFoundError(f"输入文件不存在：{source}")
    database = cantools.database.load_file(args.dbc, database_format="dbc", strict=False)
    physical_windows = build_motion_windows(parse_steps(args.physical_script))
    app_windows = build_motion_windows(parse_steps(args.app_script))
    physical_series, physical_count = collect(args.physical_asc, [])
    app_series, app_count = collect(args.app_asc, [])
    physical_rows, _ = rank_motion_activity(physical_series, physical_windows)
    app_rows, _ = rank_motion_activity(app_series, app_windows)
    common, groups = compare_rows(physical_rows, app_rows, database)
    physical_1fa = raw_id_trace(args.physical_asc, 0x1FA)
    app_1fa = raw_id_trace(args.app_asc, 0x1FA)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = args.output_dir / "驾驶窗物理按钮_vs_App通风_交叉分析报告.md"
    csv_path = args.output_dir / "驾驶窗物理按钮_vs_App通风_共同bit明细.csv"
    write_report(report, args, physical_windows, app_windows, physical_count, app_count,
                 common, groups, physical_1fa, app_1fa)
    write_csv(csv_path, common)
    print(f"物理候选bit：{len(physical_rows)}，App候选bit：{len(app_rows)}，共同bit：{len(common)}，共同ID：{len(groups)}")
    print(f"报告：{report}\n明细：{csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
