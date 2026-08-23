import sys
import re
import cantools


def load_dbc(dbc_file):
    """
    加载DBC。
    当前DBC存在部分严格校验问题，所以使用 strict=False。
    """
    return cantools.database.load_file(
        dbc_file,
        database_format="dbc",
        strict=False
    )


def parse_can_id(text):
    """
    CAN ID按十六进制解析。

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
    尝试解析常见ASC CAN数据行。

    返回：
        {
            "time": 65.1234,
            "can_id": 0x102,
            "dlc": 8,
            "data": bytes(...)
        }

    解析失败返回 None。

    兼容类似：

        65.123400 1 102 Rx d 8 01 00 00 00 00 00 00 00

    或：

        65.123400 1 102x Rx d 8 ...

    这里只处理标准数据帧，不处理远程帧等。
    """

    line = line.strip()

    if not line:
        return None

    parts = line.split()

    if len(parts) < 7:
        return None

    try:
        timestamp = float(parts[0])
    except ValueError:
        return None

    #
    # 找 CAN ID
    #
    # 常见ASC格式：
    #
    # time channel id Rx d dlc data...
    #
    can_id_text = parts[2]

    #
    # 去掉可能的扩展帧标志 x
    #
    if can_id_text.lower().endswith("x"):
        can_id_text = can_id_text[:-1]

    try:
        can_id = int(can_id_text, 16)
    except ValueError:
        return None

    #
    # 找 "d"
    #
    try:
        d_index = parts.index("d")
    except ValueError:
        try:
            d_index = parts.index("D")
        except ValueError:
            return None

    if d_index + 1 >= len(parts):
        return None

    try:
        dlc = int(parts[d_index + 1])
    except ValueError:
        return None

    data_start = d_index + 2
    data_end = data_start + dlc

    if data_end > len(parts):
        return None

    data_values = []

    try:
        for item in parts[data_start:data_end]:
            data_values.append(
                int(item, 16)
            )
    except ValueError:
        return None

    return {
        "time": timestamp,
        "can_id": can_id,
        "dlc": dlc,
        "data": bytes(data_values)
    }


def format_value(value):
    """
    cantools 对枚举值可能返回 NamedSignalValue。
    统一转换为字符串。
    """
    return str(value)


def trace_signal(
        asc_file,
        message,
        signal_name,
        start_time,
        end_time,
        only_changes=True):

    signal_names = {
        signal.name
        for signal in message.signals
    }

    if signal_name not in signal_names:
        raise ValueError(
            f"DBC Message {message.name} 中不存在 Signal: "
            f"{signal_name}"
        )

    frame_count = 0
    decode_count = 0
    output_count = 0

    previous_value = None
    first_value = True

    print()
    print("=" * 120)
    print("ASC / DBC Signal 时间序列")
    print("=" * 120)

    print(f"CAN ID       : 0x{message.frame_id:03X}")
    print(f"Message Name : {message.name}")
    print(f"Signal       : {signal_name}")
    print(
        f"时间范围     : "
        f"{start_time:.3f} ～ {end_time:.3f} 秒"
    )
    print(
        f"输出模式     : "
        f"{'仅状态变化' if only_changes else '全部帧'}"
    )

    print()

    print(
        f"{'TIME(s)':>12}  "
        f"{'RAW DATA':<28}  "
        f"{'VALUE'}"
    )

    print("-" * 120)

    with open(
            asc_file,
            "r",
            encoding="utf-8",
            errors="ignore") as f:

        for line in f:

            frame = parse_asc_line(line)

            if frame is None:
                continue

            timestamp = frame["time"]

            #
            # ASC通常按时间排序。
            # 超出结束时间后可直接停止。
            #
            if timestamp < start_time:
                continue

            if timestamp > end_time:
                break

            if frame["can_id"] != message.frame_id:
                continue

            frame_count += 1

            data = frame["data"]

            #
            # 长度与DBC不一致时先跳过。
            #
            if len(data) != message.length:
                continue

            try:
                decoded = message.decode(
                    data,
                    decode_choices=True,
                    scaling=True
                )

            except Exception:
                continue

            decode_count += 1

            if signal_name not in decoded:
                continue

            value = decoded[signal_name]

            changed = (
                first_value
                or value != previous_value
            )

            if only_changes and not changed:
                previous_value = value
                first_value = False
                continue

            raw_text = " ".join(
                f"{b:02X}"
                for b in data
            )

            print(
                f"{timestamp:12.6f}  "
                f"{raw_text:<28}  "
                f"{format_value(value)}"
            )

            output_count += 1
            previous_value = value
            first_value = False

    print("-" * 120)

    print()
    print(f"匹配到该ID帧数 : {frame_count}")
    print(f"成功解码帧数   : {decode_count}")
    print(f"实际输出行数   : {output_count}")


def main():

    #
    # 参数：
    #
    # 1 ASC文件
    # 2 DBC文件
    # 3 CAN ID
    # 4 Signal名称
    # 5 起始时间
    # 6 结束时间
    # 7 可选：all
    #
    #
    # 默认：
    # 只输出Signal变化
    #
    # 如果最后增加 all：
    # 输出全部帧
    #

    if len(sys.argv) not in (7, 8):

        print("用法：")
        print()

        print(
            "python src\\asc_dbc_signal_trace.py "
            "<ASC文件> "
            "<DBC文件> "
            "<CAN_ID> "
            "<Signal名称> "
            "<开始时间> "
            "<结束时间> "
            "[all]"
        )

        print()
        print("例如：")
        print()

        print(
            "python src\\asc_dbc_signal_trace.py "
            "data\\test.asc "
            "data\\tesla_model3_ONYX.dbc.txt "
            "102 "
            "VCLEFT_frontLatchStatus "
            "40 "
            "75"
        )

        print()
        print(
            "最后增加 all，表示输出全部解码帧："
        )

        print(
            "python src\\asc_dbc_signal_trace.py "
            "data\\test.asc "
            "data\\tesla_model3_ONYX.dbc.txt "
            "102 "
            "VCLEFT_frontLatchStatus "
            "40 "
            "75 "
            "all"
        )

        return

    asc_file = sys.argv[1]
    dbc_file = sys.argv[2]

    can_id = parse_can_id(
        sys.argv[3]
    )

    signal_name = sys.argv[4]

    start_time = float(
        sys.argv[5]
    )

    end_time = float(
        sys.argv[6]
    )

    only_changes = True

    if len(sys.argv) == 8:
        if sys.argv[7].lower() == "all":
            only_changes = False

    if end_time <= start_time:
        raise ValueError(
            "结束时间必须大于开始时间"
        )

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

    trace_signal(
        asc_file,
        message,
        signal_name,
        start_time,
        end_time,
        only_changes
    )


if __name__ == "__main__":
    main()