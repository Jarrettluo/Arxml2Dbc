# encoding: utf-8
"""
@version: 1.0
@author: Jarrett
@file: convert
@time: 2022/3/18 16:04
"""
import cantools
import os
import pandas as pd
import numpy as np


header_item_types = {
    'node_name': [str],
    'node_comment': [str],
    'node_dbc_specifics': ['DbcSpecifics', np.nan],
    'node_autosar_specifics': ['AutosarNodeSpecifics', np.nan],
    'frame_id': [int],
    'msg_name': [str],
    'msg_length': [int],
    'header_byte_order': ["big_endian", "little_endian", np.nan],
    'unused_bit_pattern': [np.nan, int],  # 默認整型
    'msg_comment': [str, np.nan],
    'cycle_time': [int, np.nan],  # 這個很關鍵，既要轉成int又要判斷非空
    'is_extended_frame': [bool, np.nan],  # 判斷是否是布爾
    'is_fd': [bool, np.nan],
    'bus_name': [str, np.nan],
    'strict': [bool, np.nan],
    'protocol': [str, np.nan],
    'name': [str],
    'start': [int],
    'length': [int],
    'byte_order': ["little_endian", "big_endian", np.nan],
    'is_signed': [bool, np.nan],
    'initial': [int, np.nan],
    'invalid': [int, np.nan],
    'scale': [float, np.nan],
    'offset': [float, np.nan],
    'minimum': [float, np.nan],
    'maximum': [float, np.nan],
    'unit': [str, np.nan],
    'signal_comment': [str, np.nan],
    'is_multiplexer': [bool, np.nan],
    'is_float': [bool, np.nan]
}

NUMBER_ITEMS = {
    'int': ['frame_id', 'msg_length', 'start', 'length'],
    'float': ['scale', 'offset', 'minimum', 'maximum']
}


def csv_convert_dbc(source_file_path: str = None,
                    out_file_path: str = None) -> None:
    """ csv 文件转换为dbc文件

    特定格式的csv文件转换为dbc文件

    :param source_file_path: str -> csv 文件路径
    :param out_file_path: str ->  输出dbc文件路径
    :return: None -> 返回None
    """
    origin_database = pd.read_csv(source_file_path)
    if origin_database.empty:
        return

    # 判断第一行是否满足
    if set(origin_database.head(0)) < set(header_item_types.keys()):
        return

    # 超大数据限制，比如超过多少行就不能转
    if len(origin_database) > 9999:
        return

    # 对数据进行int型转换, 对数据进行float型转换
    for item in dict_convert_list(NUMBER_ITEMS):
        origin_database[item] = origin_database[item].apply(pd.to_numeric, errors='coerce')
    # 数值转换以后，清空转换为空的数据
    origin_database.dropna(
        subset=dict_convert_list(NUMBER_ITEMS), axis=0,
        how='any', inplace=True)

    if origin_database.empty:
        return
    print(origin_database)
    # 数值型转换为浮点数和整数，强制类型转换，只转必须的int和float型
    for k, v in NUMBER_ITEMS.items():
        origin_database[v] = origin_database[v].astype(k)

    # 按照设定的条件进行筛选
    for item_type, item_value in header_item_types.items():
        origin_database = origin_database[origin_database[item_type].isin(item_value)]
    # 筛选以后，清空转换为空的数据
    if origin_database.empty:
        return

    # 按照node名字进行分组
    grouped_nodes = origin_database.groupby(["node_name"]).groups
    nodes = []
    messages = []
    print(origin_database)
    # 开始提取node信息
    for key_node, value_node in grouped_nodes.items():
        # 开始提取msg信息
        grouped_message = origin_database.loc[value_node].groupby(["msg_name", "frame_id"]).groups
        for i, j in grouped_message.items():
            print(i)
            signals = []
            for aa, bb in origin_database.loc[j].iterrows():
                print(aa)
                signal = cantools.database.can.signal.Signal(name=bb["name"],
                                                             start=int(bb["start"]),
                                                             length=int(bb["length"]),
                                                             byte_order=bb['byte_order'],
                                                             is_signed=bb["is_signed"],
                                                             initial=bb["initial"],
                                                             invalid=bb["invalid"],
                                                             scale=bb["scale"],
                                                             offset=bb["offset"],
                                                             minimum=bb["minimum"],
                                                             maximum=bb["maximum"],
                                                             unit=bb["unit"],
                                                             signal_comment=bb["signal_comment"],
                                                             is_multiplexer=bb["is_multiplexer"],
                                                             is_float=bb["is_float"]
                                                             )
                signals.append(signal)
            message_header = origin_database.loc[j].iloc[0]
            message = cantools.database.can.message.Message(frame_id=int(message_header["frame_id"]),
                                                            name=message_header["msg_name"],
                                                            length=message_header["msg_length"],
                                                            header_byte_order=message_header["header_byte_order"],
                                                            unused_bit_pattern=message_header["unused_bit_pattern"],
                                                            comment=message_header["msg_comment"],
                                                            cycle_time=message_header["cycle_time"],
                                                            is_extended_frame=message_header["is_extended_frame"],
                                                            is_fd=message_header["is_fd"],
                                                            bus_name=message_header["bus_name"],
                                                            strict=message_header["strict"],
                                                            protocol=message_header["protocol"],
                                                            signals=signals,
                                                            )
            messages.append(message)

        node = cantools.database.can.node.Node(name=key_node, comment=message_header["node_comment"])
        nodes.append(node)

    db = cantools.database.can.database.Database(messages=messages,
                                                 nodes=nodes,
                                                 dbc_specific=message_header["node_dbc_specific"],
                                                 autosar_specific=message_header["node_autosar_specific"])

    print(out_file_path)
    cantools.database.dump_file(db, out_file_path)


def dict_convert_list(array: dict,
                      repeat: bool = False) -> list:
    """ 列表型字典转换为列表

    :param array: -> dict,
    :param repeat: -> bool,
    :return: -> bool
    """
    if isinstance(array, dict) is False or dict == {} or isinstance(repeat, bool) is False:
        return []
    if repeat:
        return [i for k in array.values() for i in k]
    else:
        return list({i for k in array.values() for i in k})


def convert(csv_file_path, dbc_file_path):
    """将arxml文件转换为dbc文件

    输入文件路径，使用cantoos 将arxml文件转换为dbc文件。

    :param arxml_file_path: str -> arxml文件所在路径
    :param dbc_file_path: str -> dbc文件所在路径
    :return: boolean -> 转换的结果
    """
    print(csv_file_path)
    print(dbc_file_path)
    print("+++++++++++++++++++++++++++++++++++++++++++")
    if not os.path.exists(csv_file_path):
        return {'state': False, 'msg': "文件不存在！"}
    try:
        csv_convert_dbc(csv_file_path, dbc_file_path)
    except Exception as e:
        return {'state': False, 'msg': "转换失败！" + e.__repr__()}
    print(csv_file_path + dbc_file_path)
    return {'state': True, 'msg': "转换成功!"}


if __name__ == "__main__":
    print("=======")
    dbc_file_path = "out.dbc"

    csv_file_path = "temp.csv"
    print(convert(csv_file_path, dbc_file_path))
