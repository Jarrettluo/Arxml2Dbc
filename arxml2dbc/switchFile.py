# encoding: utf-8
"""
@version: 1.0
@author: Jarrett
@file: switchFile
@time: 2022/3/15 18:22
"""
import cantools
import os

# arxml_file_path = "../testData/Comfort.arxml"
# arxml_file_path = "../testData/PowerTrain.arxml"
arxml_file_path = "E:\\D--Python_Project\\Arxml2Dbc\\testData\\PowerTrain.arxml"

def convert(arxml_file_path, dbc_file_path):
    """将arxml文件转换为dbc文件

    输入文件路径，使用cantoos 将arxml文件转换为dbc文件。

    :param arxml_file_path: str -> arxml文件所在路径
    :param dbc_file_path: str -> dbc文件所在路径
    :return: boolean -> 转换的结果
    """
    if not os.path.exists(arxml_file_path):
        return {'state': False, 'msg': "文件不存在！"}
    try:
        db = cantools.database.load_file(arxml_file_path)
    except Exception as e:
        return {'state': False, 'msg': "转换失败！" + e.__repr__()}
    try:
        cantools.database.dump_file(db, dbc_file_path)
    except Exception as e:
        return {'state': False, 'msg': "转换失败！" + e.__repr__()}
    return {'state': False, 'msg': "转换成功!"}


if __name__ == "__main__":
    print(convert(arxml_file_path, "xxx.dbc"))