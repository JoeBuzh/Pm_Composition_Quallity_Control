# -*- encoding: utf-8 -*-
'''
@Filename    : utils.py
@Datetime    : 2020/06/20 14:23:30
@Author      : Joe-Bu
@version     : 1.0
'''

import os
import sys
import xlrd
import json
from datetime import datetime

import numpy as np
import pandas as pd

from cfg import duration, paths, mapping, PM, SNA, OCEC


def get_env():
    '''
        获取当前运行环境，mac or linux.
    '''
    return sys.platform.__str__()


def checkdir(path):
    '''
        目录检查.
        存在则返回，不存在创建后返回.
    '''
    if not os.path.exists(path):
        os.makedirs(path)

    assert os.path.exists(path)

    return path


def get_all_stations(filename: str) -> list:
    '''
        获取所有组分观测站点id列表.
    '''
    assert os.path.exists(filename)

    with open(filename, 'r') as jsonfile:
        id_map = json.load(jsonfile)

    id_list = [int(k) for k, _ in id_map.items()]

    return id_list


def parse_time(dt, formats: str):
    '''
        解析文件中时间
    '''
    return datetime.strptime(dt, formats)


def read_data(filename):
    '''
        读取数据，三类数据格式一致.
    '''
    assert os.path.exists(filename)

    data = pd.read_csv(
        filename, 
        sep=',', 
        encoding='utf-8', 
        header=0)
    data['time'] = data['time'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d:%H"))
    data1 = data[['time', 'stationcode'] + PM + SNA + OCEC]
    data1.replace(-999.0, np.nan, inplace=True)
    # print(data1)
    # print(data1.sample())

    return data1