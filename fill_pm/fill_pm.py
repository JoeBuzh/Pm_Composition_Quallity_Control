# -*- encoding: utf-8 -*-
'''
@Filename    : fill_pm.py
@Datetime    : 2020/06/05 16:58:50
@Author      : Joe-Bu
@version     : 1.0
'''

import os
import sys
import xlrd
from datetime import datetime, timedelta

import folium
import numpy as np
import pandas as pd
from rtree import index

PM = ['PM10', 'PM25']
IONIC = ['F-','Cl-','NO3-','SO42-','Ca2+','Na+','K+','NH4+','Mg2+']
OCEC = ['OC','EC']
METAL = [
    'Hg','Br','As','Si','Se','Te','V','Ca','Ti','Ba','Sc','Pd','Co','Mo','K',
    'Fe','Pb','TI','Cu','Al','Cr','Cs','Ag','Zn','Sb','Sn','Mn','Cd','Ni','Ga'
]


def read_txt(filename: str, sep:str=None):
    '''
        文件读取
    '''
    assert os.path.exists(filename)
    df = pd.read_table(
        filename, 
        sep=sep, 
        encoding='utf-8', 
        engine='python',
        error_bad_lines=False)

    return df


def parse_time(x):
    return datetime.strptime(str(x), "%Y%m%d%H").strftime('%Y-%m-%d:%H')


def read_org(filepath: str):
    '''
        Read *.txt data file.
    '''
    assert os.path.join(filepath)

    data = pd.read_csv(
        filepath, 
        sep=',', 
        names=['time','stationcode','longitude','latitude']+PM+IONIC+OCEC+METAL,
        encoding='utf-8')
    data.replace(-999.0, np.nan, inplace=True)

    return data


def search(comp_info, idx) -> dict:
    '''
        匹配最近站点, 返回映射关系。
    '''
    _map = {}
    for _, row in comp_info.iterrows():
        lon = row['longitude']
        lat = row['latitude']
        comp_code = row['stationcode']
        nearby = list(idx.nearest((lon, lat, lon, lat), 1, objects=True))[0]
        _map[comp_code] = nearby.object

    return _map


def insert_idx(envi_info, idx):
    for i, row in envi_info.iterrows():
        lon = row['经度']
        lat = row['纬度']
        obj = row['站号']
        idx.insert(i, (lon, lat, lon, lat), obj=obj)

    return idx


def merge_pm(src, dst, nearby, mapping):
    '''
        匹配最近站点PM观测数据.
    '''
    assert os.path.exists(src) and os.path.exists(dst)

    for i, (k, val) in enumerate(mapping.items()):
        orgfile = os.path.join(src, '{}.txt'.format(k))
        org = read_org(orgfile)  # -999.0 -> nan
        near = nearby.loc[nearby['站点编号']==int(val), ['时间','站点编号','PM2.5浓度','PM10浓度']]
        near['time'] = near['时间'].apply(parse_time)
        df = org.merge(near, left_on='time', right_on='time', how='outer')
        df['PM10'] = np.round(np.mean(df[['PM10', 'PM10浓度']], axis=1), 3)
        df['PM25'] = np.round(np.mean(df[['PM25', 'PM2.5浓度']], axis=1), 3)
        picked = df.loc[:, ['time','stationcode','longitude','latitude']+PM+IONIC+OCEC+METAL]
        picked.replace(np.nan, -999.0, inplace=True)
        picked[PM+IONIC+OCEC+METAL].astype(np.float)
        picked.to_csv(
            os.path.join(dst, '{}.txt'.format(k)),
            sep=',',
            index=False,
            header=False,
            float_format='%.3f'
        )
        print('{}\t{}\n'.format(i+1, '-'*100))
        # print(picked.info())
        

def main():
    '''
        主程序.
    '''
    idx = index.Index()
    comp_info = read_txt('../data/obs_com_stations.txt', sep=',')
    envi_info = pd.read_csv('../data/obs_env_stations.txt', delim_whitespace=True)
    # get map
    idx = insert_idx(envi_info, idx)
    mapping = search(comp_info, idx)
    print(mapping)
    # data dir
    raw_src = '../data/raw_data'
    nearby_file = '../data/nearby_envi.txt'
    raw_dst = '../data/raw_data_pm'
    # read obs envi
    nearby = read_txt(nearby_file, sep=',')
    nearby.replace(-999.0, np.nan, inplace=True)

    # merge PM
    merge_pm(raw_src, raw_dst, nearby, mapping)


if __name__ == "__main__":
    main()
