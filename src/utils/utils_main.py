# -*- encoding: utf-8 -*-

import os
import sys
sys.path.append('../dao')

import numpy as np
import pandas as pd

from dao.get_rawdata import read_raw_txt


IONIC = [
    'time', 'stationcode', 'PM10', 'PM25', 'SO42-', 'F-',
    'NO3-', 'NH4+', 'Cl-', 'Na+', 'Ca2+', 'Mg2+', 'K+'
]
OCEC = ['time', 'stationcode', 'PM10', 'PM25', 'OC', 'EC']
METAL = [
    'time','stationcode','PM10','PM25','Hg','Br','As','Si','Se','Te','V','Ca','Ti','Ba','Sc','Pd','Co',
    'Mo','K','Fe','Pb','TI','Cu', 'Al','Cr','Cs','Ag', 'Zn','Sb','Sn','Mn','Cd','Ni','Ga'
]

def split_obs(df):
    '''
        考虑数据切割时不同列的缺失.
    '''
    obs_ionic = df[[x for x in IONIC if x in df.columns]]
    for x in IONIC:
        if x not in obs_ionic.columns:
            obs_ionic[x] = np.nan
        else:
            continue
    obs_ocec = df[[x for x in OCEC if x in df.columns]]
    for x in OCEC:
        if x not in obs_ocec.columns:
            obs_ocec[x] = np.nan
        else:
            continue    
    obs_metal = df[[x for x in METAL if x in df.columns]]
    for x in METAL:
        if x not in obs_metal.columns:
            obs_metal[x] = np.nan
        else:
            continue

    return obs_ionic, obs_ocec, obs_metal


def concat_data(time_list: list, datadir: str):
    '''
        数据拼接.
    '''
    data_list = []
    for _, t in enumerate(time_list):
        obs_file = 'obs_com_{}.txt'.format(t.strftime("%Y%m%d%H"))
        obs_df = read_raw_txt(os.path.join(datadir, obs_file))[1]
        obs_df['time'] = t
        # print(obs_df)
        data_list.append(obs_df)
    if len(data_list) > 0:
        return pd.concat(data_list, axis=0, join='outer')
    else:
        return None


def checkdir(path):
    '''
        判断路径是否存在，不存在则创建.
    '''
    if not os.path.exists(path):
        os.makedirs(path)

    assert os.path.exists(path)