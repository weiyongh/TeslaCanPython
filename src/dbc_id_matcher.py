import sys
import re
import cantools


def load_dbc(dbc_file):
    return cantools.database.load_file(
        dbc_file,
        database_format="dbc",
        strict=False
    )


def load_id_stat(stat_file):
    result = []

    with open(
        stat_file,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        for line in f:
            line = line.strip()

            if not line:
                continue

            match = re.match(
                r"^([0-9A-Fa-f]+)\s+"
                r"(\d+)\s+"
                r"(\S+)",
                line
            )

            if not match:
                continue

            can_id_text = match.group(1)
            count_text = match.group(2)
            dlc_stat = match.group(3)

            can_id = int(can_id_text, 16)
            count = int(count_text)

            result.append({
                "can_id": can_id,
                "count": count,
                "dlc_stat": dlc_stat
            })

    return result


def build_dbc_message_map(db):
    return {
        message.frame_id: message
        for message in db.messages
    }


def analyze(dbc_file, stat_file):

    db = load_dbc(dbc_file)
    id_stats = load_id_stat(stat_file)

    dbc_messages = build_dbc_message_map(db)

    matched = []
    unmatched = []

    for stat in id_stats:

        can_id = stat["can_id"]
        message = dbc_messages.get(can_id)

        if message is not None:

            matched.append({
                "can_id": can_id,
                "count": stat["count"],
                "asc_dlc": stat["dlc_stat"],
                "dbc_dlc": message.length,
                "message_name": message.name
            })

        else:

            unmatched.append({
                "can_id": can_id,
                "count": stat["count"],
                "asc_dlc": stat["dlc_stat"]
            })

    return db, id_stats, matched, unmatched


def print_result(
    db,
    id_stats,
    matched,
    unmatched
):

    print()
    print("=" * 100)
    print("DBC / ASC CAN ID 匹配统计")
    print("=" * 100)

    print()
    print(f"[MATCHED] 已命中 ID：{len(matched)}")
    print("-" * 100)

    print(
        f"{'CAN_ID':<10}"
        f"{'DEC_ID':<10}"
        f"{'COUNT':<12}"
        f"{'ASC_DLC':<16}"
        f"{'DBC_DLC':<10}"
        f"{'MESSAGE_NAME'}"
    )

    print("-" * 100)

    for item in matched:

        print(
            f"{'0x' + format(item['can_id'], '03X'):<10}"
            f"{item['can_id']:<10}"
            f"{item['count']:<12}"
            f"{item['asc_dlc']:<16}"
            f"{item['dbc_dlc']:<10}"
            f"{item['message_name']}"
        )

    print()
    print(f"[UNMATCHED] 未命中 ID：{len(unmatched)}")
    print("-" * 70)

    print(
        f"{'CAN_ID':<10}"
        f"{'DEC_ID':<10}"
        f"{'COUNT':<12}"
        f"{'ASC_DLC'}"
    )

    print("-" * 70)

    for item in unmatched:

        print(
            f"{'0x' + format(item['can_id'], '03X'):<10}"
            f"{item['can_id']:<10}"
            f"{item['count']:<12}"
            f"{item['asc_dlc']}"
        )

    total = len(id_stats)
    matched_count = len(matched)
    unmatched_count = len(unmatched)

    rate = (
        matched_count / total * 100
        if total > 0
        else 0.0
    )

    print()
    print("=" * 100)
    print("统计汇总")
    print("-" * 100)

    print(f"DBC Message数量 : {len(db.messages)}")
    print(f"ASC CAN ID数量  : {total}")
    print(f"DBC命中数量     : {matched_count}")
    print(f"DBC未命中数量   : {unmatched_count}")
    print(f"DBC覆盖率       : {rate:.2f}%")

    print("=" * 100)


def main():

    if len(sys.argv) != 3:

        print("用法：")
        print(
            "python src\\dbc_id_matcher.py "
            "<DBC文件> "
            "<ID统计文件>"
        )

        print()
        print("例如：")
        print(
            "python src\\dbc_id_matcher.py "
            "data\\tesla_model3_ONYX.dbc.txt "
            "data\\IdStat1.txt"
        )

        return

    dbc_file = sys.argv[1]
    stat_file = sys.argv[2]

    db, id_stats, matched, unmatched = analyze(
        dbc_file,
        stat_file
    )

    print_result(
        db,
        id_stats,
        matched,
        unmatched
    )


if __name__ == "__main__":
    main()