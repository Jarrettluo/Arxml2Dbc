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

dbc_file_path = "xxx.dbc"
output_file_path = "out.dbc"

csv_file_path = "temp.csv"

""""
                 frame_id: int,
                 name: str,
                 length: int,
"""
valid_info = {
    "frame_id": int,
    "msg_name": str,
    "msg_length": int,
}


def convert():
    # db = cantools.database.load_file(dbc_file_path)
    # print(db)
    # print(db.nodes)
    # print(db.messages)
    # # print(db.signals)
    # print(type(db))

    """
                     name: str,
                 start: int,
                 length: int,
    :return:
    """

    signal = cantools.database.can.signal.Signal(name="luojiarui", start=12, length=10)
    signal2 = cantools.database.can.signal.Signal(name="luojiarui2", start=32, length=3)
    signal3 = cantools.database.can.signal.Signal(name="luojiarui3", start=45, length=1)

    """
                     frame_id: int,
                 name: str,
                 length: int,
                 signals: List[Signal],
    """
    msg = cantools.database.can.message.Message(frame_id=123, name="ljr", length=8, signals=[signal, signal2, signal3])

    print(msg)

    xx = cantools.database.can.database.Database(messages=[msg])
    print(xx)

    cantools.database.dump_file(xx, output_file_path)


def origin():
    db = cantools.database.load_file(dbc_file_path)
    print(db)
    print(db.nodes)
    print(db.messages)
    # print(db.signals)
    print(type(db))


def readCsv():
    origin_database = pd.read_csv(csv_file_path)
    # 超大数据限制，比如超过多少行就不能转

    # 清洗数据，必须满足要求的数据

    grouped_nodes = origin_database.groupby(["node_name"]).groups
    nodes = []
    messages = []
    # 开始提取node信息
    for key_node, value_node in grouped_nodes.items():
        # 开始提取msg信息
        grouped_message = origin_database.loc[value_node].groupby(["msg_name", "frame_id"]).groups
        for i, j in grouped_message.items():
            signals = []
            for aa, bb in origin_database.loc[j].iterrows():
                signal = cantools.database.can.signal.Signal(name=bb["name"],
                                                             start=int(bb["start"]),
                                                             length=int(bb["length"])
                                                             )
                signals.append(signal)
            message_header = origin_database.loc[j].iloc[0]
            message = cantools.database.can.message.Message(frame_id=int(message_header["frame_id"]),
                                                            name=message_header["msg_name"],
                                                            length=message_header["msg_length"],
                                                            signals=signals,
                                                            )
            messages.append(message)

        node = cantools.database.can.node.Node(name=key_node)
        nodes.append(node)

    db = cantools.database.can.database.Database(messages=messages, nodes=nodes)
    cantools.database.dump_file(db, output_file_path)


if __name__ == "__main__":
    print("=======")
    # convert()
    # origin()
    readCsv()
    #
    # for x,y in {'ABSdata': [0, 1], 'ABSdata2': [2], 'ABSdata3': [3]}.items():
    #     print(x)
    #     print(y)
