# -*- encoding: utf-8 -*-
'''
@Filename    : fill_obs.py
@Datetime    : 2020/06/05 16:58:50
@Author      : Joe-Bu
@version     : 1.0
'''

import os
import sys
import xlrd
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime, timedelta

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
    return datetime.strptime(str(x), "%Y%m%d%H").strftime('%Y%m%d:%H')


def read_org(filepath: str):
    '''
        Read *.txt data file.
    '''
    assert os.path.join(filepath)

    data = pd.read_csv(filepath, sep=',', encoding='utf-8')
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


def merge_pm(src, dst, nearby, mapping, start, end):
    '''
        匹配最近站点PM观测数据.
    '''
    assert os.path.exists(src) and os.path.exists(dst)
    for s in nearby['时间'].unique():
        print(s)
        orgfile = os.path.join(src, 'obs_com_{}.txt'.format(s))
        org = read_org(orgfile)  # -999.0 -> nan
        # print(nearby.sample())
        tmp = nearby.loc[nearby['时间']==s]
        # print(tmp)
        # fill one hour
        for i, (k, val) in enumerate(mapping.items()):
            '''
                k: obs_code, val: envi_code
            '''
            # print(org.loc[org['stationcode']==k])
            print(tmp.loc[tmp['站点编号']==val][['PM10浓度', 'PM2.5浓度']])
            if tmp.loc[tmp['站点编号']==val][['PM10浓度', 'PM2.5浓度']].shape[0] > 0:
                org.loc[org['stationcode']==k, 'PM10'] = tmp.loc[tmp['站点编号']==val]['PM10浓度'].values[0]
                org.loc[org['stationcode']==k, 'PM25'] = tmp.loc[tmp['站点编号']==val]['PM2.5浓度'].values[0]
            # print(org)
            # picked = org.loc[['time','stationcode','longitude','latitude']+PM+IONIC+OCEC+METAL]
            org.replace(np.nan, -999.0, inplace=True)
            # print(type(org))
            # picked[PM+IONIC+OCEC+METAL].astype(np.float)
            org.to_csv(
                os.path.join(dst, 'obs_com_{}.txt'.format(start.strftime("%Y%m%d%H"))), 
                sep=',',
                index=False,
                header=True, 
                float_format='%.3f')
            # print('{}\t{}\n'.format(i+1, '-'*100))

        start += timedelta(hours=1)
        

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
    obs_src = '../data/obs_hourly'
    nearby_file = '../data/nearby_envi.txt'
    obs_dst = '../data/obs_hourly_pm'
    # read obs envi
    nearby = read_txt(nearby_file, sep=',')
    nearby.replace(-999.0, np.nan, inplace=True)

    # merge PM
    start = datetime(2019, 1, 1, 0, 0)
    end = datetime(2019, 12, 31, 23, 0)
    merge_pm(obs_src, obs_dst, nearby, mapping, start, end)


if __name__ == "__main__":
    main()
