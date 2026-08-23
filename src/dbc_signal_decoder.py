import sys
import cantools


def load_dbc(dbc_file):
    """
    加载DBC。

    当前DBC存在部分Signal严格校验问题，
    所以继续使用 strict=False。
    """
    return cantools.database.load_file(
        dbc_file,
        database_format="dbc",
        strict=False
    )


def parse_can_id(text):
    """
    CAN ID统一按十六进制理解。

    支持：
        102
        0x102
        318
        0x318
    """

    text = text.strip()

    if text.lower().startswith("0x"):
        text = text[2:]

    return int(text, 16)


def parse_data(data_text):
    """
    将：

        "02 00 10 FF 00 00 00 00"

    转成 bytes。
    """

    text = (
        data_text
        .replace(",", " ")
        .replace("-", " ")
        .strip()
    )

    parts = text.split()

    result = []

    for part in parts:

        value = int(part, 16)

        if value < 0 or value > 255:
            raise ValueError(
                f"非法DATA字节：{part}"
            )

        result.append(value)

    return bytes(result)


def format_choices(signal):
    """
    将DBC枚举值整理成：
        1=OPENED, 2=CLOSED ...
    """

    if not signal.choices:
        return "-"

    items = []

    for value, name in signal.choices.items():
        items.append(
            f"{value}={name}"
        )

    return ", ".join(items)


def print_message_info(message):
    """
    输出Message及全部Signal定义。
    """

    print()
    print("=" * 110)
    print("DBC CAN Message Signal 定义")
    print("=" * 110)

    print(
        f"CAN ID       : 0x{message.frame_id:03X}"
    )

    print(
        f"Decimal ID   : {message.frame_id}"
    )

    print(
        f"Message Name : {message.name}"
    )

    print(
        f"DBC DLC      : {message.length}"
    )

    print(
        f"Signal Count : {len(message.signals)}"
    )

    print()

    print("-" * 110)

    print(
        f"{'SIGNAL_NAME':<38}"
        f"{'START':>7}"
        f"{'LEN':>7}"
        f"{'BYTE_ORDER':>16}"
        f"{'SIGNED':>9}"
        f"{'SCALE':>10}"
        f"{'UNIT':>10}"
    )

    print("-" * 110)

    for signal in message.signals:

        unit = (
            signal.unit
            if signal.unit
            else "-"
        )

        print(
            f"{signal.name:<38}"
            f"{signal.start:>7}"
            f"{signal.length:>7}"
            f"{signal.byte_order:>16}"
            f"{str(signal.is_signed):>9}"
            f"{str(signal.scale):>10}"
            f"{unit:>10}"
        )

        if signal.choices:

            print(
                "    Choices: "
                + format_choices(signal)
            )

    print("-" * 110)


def decode_data(message, data):
    """
    解码一帧CAN DATA。
    """

    print()
    print("=" * 110)
    print("CAN DATA 解码")
    print("=" * 110)

    print(
        "RAW DATA : "
        + " ".join(
            f"{b:02X}"
            for b in data
        )
    )

    print()


    #
    # DATA长度检查
    #

    if len(data) != message.length:

        print(
            f"警告：DATA长度={len(data)}，"
            f"DBC定义DLC={message.length}"
        )

        print(
            "当前DATA长度与DBC定义不一致，"
            "解码结果需要谨慎。"
        )

        print()


    try:

        decoded = message.decode(
            data,
            decode_choices=True,
            scaling=True,
            allow_truncated=False
        )

    except Exception as e:

        print(
            "DBC解码失败："
            + str(e)
        )

        return


    print(
        f"{'SIGNAL_NAME':<42}"
        f"{'VALUE'}"
    )

    print("-" * 110)


    for signal in message.signals:

        if signal.name not in decoded:
            continue

        value = decoded[
            signal.name
        ]

        print(
            f"{signal.name:<42}"
            f"{value}"
        )


def main():

    #
    # 用法1：
    #
    # python dbc_signal_decoder.py DBC 102
    #
    # 只显示Signal定义
    #
    #
    # 用法2：
    #
    # python dbc_signal_decoder.py DBC 102 "02 00 00 00 00 00 00 00"
    #
    # 显示Signal定义并解码DATA
    #

    if len(sys.argv) not in (3, 4):

        print("用法：")
        print()

        print(
            "1. 查看指定CAN ID的Signal定义："
        )

        print(
            "python src\\dbc_signal_decoder.py "
            "<DBC文件> "
            "<CAN_ID>"
        )

        print()

        print(
            "2. 解码一帧CAN DATA："
        )

        print(
            "python src\\dbc_signal_decoder.py "
            "<DBC文件> "
            "<CAN_ID> "
            "\"<DATA>\""
        )

        print()

        print("例如：")

        print(
            "python src\\dbc_signal_decoder.py "
            "data\\tesla_model3_ONYX.dbc.txt "
            "102"
        )

        print()

        print(
            "python src\\dbc_signal_decoder.py "
            "data\\tesla_model3_ONYX.dbc.txt "
            "102 "
            "\"02 00 00 00 00 00 00 00\""
        )

        return


    dbc_file = sys.argv[1]

    can_id = parse_can_id(
        sys.argv[2]
    )


    try:

        db = load_dbc(
            dbc_file
        )

        message = db.get_message_by_frame_id(
            can_id
        )


    except KeyError:

        print(
            f"DBC中没有找到 CAN ID "
            f"0x{can_id:03X}"
        )

        return


    except Exception as e:

        print(
            "DBC加载失败：",
            str(e)
        )

        return


    #
    # 先输出Signal定义
    #

    print_message_info(
        message
    )


    #
    # 如果提供DATA，则继续解码
    #

    if len(sys.argv) == 4:

        try:

            data = parse_data(
                sys.argv[3]
            )

            decode_data(
                message,
                data
            )

        except Exception as e:

            print(
                "DATA处理失败：",
                str(e)
            )


if __name__ == "__main__":
    main()