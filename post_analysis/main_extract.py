# -*- encoding: utf-8 -*-
'''
@Filename    : main_extract.py
@Datetime    : 2020/05/16 13:55:52
@Author      : Joe-Bu
@version     : 1.0
'''

import os
import sys
import xlrd
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from cfg import paths
from utils.utils_extract import get_code_from, checkdir


def write2file(start, end, src, dst, stationcode):
    '''
        读取原始的文件，提取单个站点全年时刻汇聚为一个站点文件
    '''
    assert start <= end
    assert os.path.exists(src) and os.path.exists(dst)

    while start <= end:
        # obs data
        #filename = 'obs_com_{}.txt'.format(start.strftime("%Y%m%d%H"))
        # qc data
        #filename = 'qc_obs_{}.txt'.format(start.strftime("%Y%m%d%H"))
        # fill data
        filename = 'fill_obs_{}.txt'.format(start.strftime("%Y%m%d%H"))

        if checkdir(os.path.join(src, filename)):
            with open(os.path.join(src, filename), 'r') as f0:
                lines = f0.readlines()
                conts = ['{},'.format(start.strftime("%Y-%m-%d:%H"))+line 
                    for line in lines if line.startswith(str(stationcode))]
                if conts:
                    with open(os.path.join(dst, str(stationcode)+'.txt'), 'a') as f1:
                        f1.write(conts[0])

        start += timedelta(hours=1)


def add_header(dst):
    cmd = r'''sed -i "1i\time,stationcode,longitude,latitude,PM10,PM25,F-,Cl-,NO3-,SO42-,Ca2+,Na+,K+,NH4+,Mg2+,OC,EC,Hg,Br,As,Si,Se,Te,V,Ca,Ti,Ba,Sc,Pd,Co,Mo,K,Fe,Pb,TI,Cu,Al,Cr,Cs,Ag,Zn,Sb,Sn,Mn,Cd,Ni,Ga" '''
    for f in os.listdir(dst):
        cmd_insert = cmd + os.path.join(dst, f)
        #print(cmd_insert)
        os.system(cmd_insert)


def main():
    start = datetime(2019, 1, 1, 11, 0)
    end = datetime(2019, 12, 31, 22, 0)

    stations_info = get_code_from(paths['stationfile'])
    src = paths['extract_src']
    dst = paths['extract_dst']

    for i, stationcode in enumerate(stations_info['stationcode']):
        print('handling station {}: {}'.format(i+1, stationcode))
        write2file(start, end, src, dst, stationcode)
    
    add_header(dst)


if __name__ == "__main__":
    main()
