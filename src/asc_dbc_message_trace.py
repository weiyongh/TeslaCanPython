import sys
import cantools


def load_dbc(dbc_file):
    """
    加载DBC。
    当前DBC存在部分严格校验问题，因此使用 strict=False。
    """
    return cantools.database.load_file(
        dbc_file,
        database_format="dbc",
        strict=False
    )


def parse_can_id(text):
    """
    CAN ID统一按十六进制解析。

    支持：
        102
        0x102
    """
    text = text.strip()

    if text.lower().startswith("0x"):
        text = text[2:]

    return int(text, 16)


def parse_asc_line(line):
    """
    解析常见Vector ASC CAN数据行。

    例如：
        65.123400 1 102 Rx d 8 01 00 00 00 00 00 00 00

    返回：
        {
            "time": 65.1234,
            "can_id": 0x102,
            "dlc": 8,
            "data": bytes(...)
        }

    解析失败返回 None。
    """

    line = line.strip()

    if not line:
        return None

    parts = line.split()

    if len(parts) < 7:
        return None

    # --------------------------------------------------
    # 时间
    # --------------------------------------------------

    try:
        timestamp = float(parts[0])
    except ValueError:
        return None

    # --------------------------------------------------
    # CAN ID
    # --------------------------------------------------

    can_id_text = parts[2]

    if can_id_text.lower().endswith("x"):
        can_id_text = can_id_text[:-1]

    try:
        can_id = int(can_id_text, 16)
    except ValueError:
        return None

    # --------------------------------------------------
    # 找数据帧标记 d
    # --------------------------------------------------

    d_index = -1

    for i, part in enumerate(parts):
        if part.lower() == "d":
            d_index = i
            break

    if d_index < 0:
        return None

    if d_index + 1 >= len(parts):
        return None

    # --------------------------------------------------
    # DLC
    # --------------------------------------------------

    try:
        dlc = int(parts[d_index + 1])
    except ValueError:
        return None

    # --------------------------------------------------
    # DATA
    # --------------------------------------------------

    data_start = d_index + 2
    data_end = data_start + dlc

    if data_end > len(parts):
        return None

    data_values = []

    try:
        for item in parts[data_start:data_end]:
            value = int(item, 16)

            if value < 0 or value > 255:
                return None

            data_values.append(value)

    except ValueError:
        return None

    return {
        "time": timestamp,
        "can_id": can_id,
        "dlc": dlc,
        "data": bytes(data_values)
    }


def format_raw_data(data):
    return " ".join(
        f"{b:02X}"
        for b in data
    )


def format_value(value):
    """
    cantools枚举值可能是 NamedSignalValue。
    统一转换成字符串。
    """
    return str(value)


def decode_message(message, data):
    """
    解码完整Message。

    返回：
        dict(signal_name -> value)

    解码失败返回None。
    """

    try:
        return message.decode(
            data,
            decode_choices=True,
            scaling=True
        )

    except Exception:
        return None


def get_changed_signals(previous, current):
    """
    比较前后两帧解码结果。

    返回：
        [
            (signal_name, old_value, new_value),
            ...
        ]
    """

    changes = []

    for signal_name, new_value in current.items():

        if signal_name not in previous:
            continue

        old_value = previous[signal_name]

        if old_value != new_value:

            changes.append(
                (
                    signal_name,
                    old_value,
                    new_value
                )
            )

    return changes


def print_initial_state(
        timestamp,
        decoded
):
    """
    输出窗口内第一帧的完整状态。

    它不是一次变化，而是观察窗口开始时的基准状态。
    """

    print()
    print("=" * 120)
    print(
        f"初始状态 @ {timestamp:.6f} 秒"
    )
    print("=" * 120)

    for signal_name, value in decoded.items():

        print(
            f"{signal_name:<42} = "
            f"{format_value(value)}"
        )


def print_event(
        event_number,
        timestamp,
        previous_timestamp,
        raw_data,
        changes
):
    """
    输出一次状态变化事件。
    """

    print()
    print("-" * 120)

    if previous_timestamp is None:
        delta = 0.0
    else:
        delta = timestamp - previous_timestamp

    print(
        f"[EVENT {event_number:03d}] "
        f"TIME = {timestamp:.6f} s"
        f"    ΔT = {delta:.6f} s"
    )

    print(
        f"RAW  = {format_raw_data(raw_data)}"
    )

    print()

    for signal_name, old_value, new_value in changes:

        print(
            f"  {signal_name:<40} "
            f"{format_value(old_value)}"
            f"  ->  "
            f"{format_value(new_value)}"
        )


def trace_message(
        asc_file,
        message,
        start_time,
        end_time
):

    frame_count = 0
    decode_count = 0
    event_count = 0

    previous_decoded = None
    previous_event_time = None

    print()
    print("=" * 120)
    print("ASC / DBC Message 全Signal状态时间线")
    print("=" * 120)

    print(
        f"CAN ID       : "
        f"0x{message.frame_id:03X}"
    )

    print(
        f"Message Name : "
        f"{message.name}"
    )

    print(
        f"DBC DLC      : "
        f"{message.length}"
    )

    print(
        f"Signal Count : "
        f"{len(message.signals)}"
    )

    print(
        f"时间范围     : "
        f"{start_time:.3f} ～ "
        f"{end_time:.3f} 秒"
    )

    print()

    with open(
        asc_file,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        for line in f:

            frame = parse_asc_line(line)

            if frame is None:
                continue

            timestamp = frame["time"]

            # --------------------------------------------------
            # 时间范围过滤
            # --------------------------------------------------

            if timestamp < start_time:
                continue

            if timestamp > end_time:
                break

            # --------------------------------------------------
            # CAN ID过滤
            # --------------------------------------------------

            if frame["can_id"] != message.frame_id:
                continue

            frame_count += 1

            data = frame["data"]

            # --------------------------------------------------
            # DLC检查
            # --------------------------------------------------

            if len(data) != message.length:
                continue

            # --------------------------------------------------
            # 完整Message解码
            # --------------------------------------------------

            decoded = decode_message(
                message,
                data
            )

            if decoded is None:
                continue

            decode_count += 1

            # --------------------------------------------------
            # 第一帧作为基准状态
            # --------------------------------------------------

            if previous_decoded is None:

                print_initial_state(
                    timestamp,
                    decoded
                )

                previous_decoded = decoded
                continue

            # --------------------------------------------------
            # 比较全部Signal
            # --------------------------------------------------

            changes = get_changed_signals(
                previous_decoded,
                decoded
            )

            # --------------------------------------------------
            # 只有发生变化才输出
            # --------------------------------------------------

            if changes:

                event_count += 1

                print_event(
                    event_count,
                    timestamp,
                    previous_event_time,
                    data,
                    changes
                )

                previous_event_time = timestamp

            # 注意：
            # 无论有没有变化，都必须更新上一帧。
            previous_decoded = decoded

    print()
    print("=" * 120)
    print("统计")
    print("=" * 120)

    print(
        f"匹配到该ID帧数 : "
        f"{frame_count}"
    )

    print(
        f"成功解码帧数   : "
        f"{decode_count}"
    )

    print(
        f"状态变化事件数 : "
        f"{event_count}"
    )

    print("=" * 120)


def main():

    #
    # 参数：
    #
    # 1 ASC文件
    # 2 DBC文件
    # 3 CAN ID
    # 4 开始时间
    # 5 结束时间
    #
    #
    # 例如：
    #
    # python src\asc_dbc_message_trace.py
    #        data\test.asc
    #        data\tesla_model3_ONYX.dbc.txt
    #        102
    #        30
    #        80
    #

    if len(sys.argv) != 6:

        print("用法：")
        print()

        print(
            "python src\\asc_dbc_message_trace.py "
            "<ASC文件> "
            "<DBC文件> "
            "<CAN_ID> "
            "<开始时间> "
            "<结束时间>"
        )

        print()
        print("例如：")
        print()

        print(
            "python src\\asc_dbc_message_trace.py "
            "data\\test.asc "
            "data\\tesla_model3_ONYX.dbc.txt "
            "102 "
            "30 "
            "80"
        )

        return

    asc_file = sys.argv[1]
    dbc_file = sys.argv[2]

    can_id = parse_can_id(
        sys.argv[3]
    )

    start_time = float(
        sys.argv[4]
    )

    end_time = float(
        sys.argv[5]
    )

    if end_time <= start_time:

        raise ValueError(
            "结束时间必须大于开始时间"
        )

    # --------------------------------------------------
    # DBC
    # --------------------------------------------------

    db = load_dbc(
        dbc_file
    )

    try:

        message = db.get_message_by_frame_id(
            can_id
        )

    except KeyError:

        print(
            f"DBC中找不到 CAN ID "
            f"0x{can_id:03X}"
        )

        return

    # --------------------------------------------------
    # 分析
    # --------------------------------------------------

    trace_message(
        asc_file,
        message,
        start_time,
        end_time
    )


if __name__ == "__main__":
    main()