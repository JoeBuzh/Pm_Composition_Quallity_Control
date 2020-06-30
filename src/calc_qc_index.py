# -*- encoding: utf-8 -*-
'''
@Filename    : calc_qc_index.py
@Datetime    : 2020/06/03 14:04:54
@Author      : Joe-Bu
@version     : 1.0
'''

import os
import sys
import xlrd
import warnings
warnings.filterwarnings('ignore')
import configparser
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from .dao.get_rawdata import read_ini
from .dao.write2file import write2ini
from cfg import PM, IONIC, OCEC, METAL
from cfg import STATS_FLOAT_UPPER, STATS_UPPER, paths

'''
    exper 经验的;  stats 统计的
    upper 上限;    lower 下限
    float 前后浮动; ratio 占比; balance 平衡
'''
EXPER = {
    # Ionic
    'SO42-': {'exper_float_upper': 0.4, 'exper_lower': 3.0, 'exper_upper': 100.0}, 
    'NO3-': {'exper_float_upper': 0.4, 'exper_lower': 3.0, 'exper_upper': 100.0}, 
    'NH4+': {'exper_float_upper': 0.4, 'exper_lower': 3.0, 'exper_upper': 100.0}, 
    'SNA': {'exper_balance_lower': 0.7, 'exper_balance_upper': 1.3},
    'AECE': {'exper_balance_lower': 0.7, 'exper_balance_upper': 1.3, 'exper_ratio_upper': 0.8},
    # OCEC
    'OC': {'exper_ratio_upper': 0.3, 'exper_float_upper': 1.0, 'exper_lower': 0.5, 'exper_upper': 100.0},
    'EC': {'exper_ratio_upper': 0.2, 'exper_float_upper': 3.0, 'exper_lower': 0.2, 'exper_upper': 300.0},
    'OCEC': {'exper_ratio_upper': 0.5, 'exper_balance_lower': 0.6, 'exper_balance_upper': 10},
    # Metal
    'Ca': {'exper_lower': 0.1, 'exper_upper': 10.0},
    'Si': {'exper_lower': 0.1, 'exper_upper': 10.0},
    'Al': {'exper_lower': 0.0, 'exper_upper': 5.0},
    'Fe': {'exper_lower': 0.0, 'exper_upper': 2.0}
}
    # 'Metal_normal': {'exper_lower': 0.0, 'exper_upper': 1.0}


def read_txt(filepath: str):
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


def get_balance(data, percentail_lower:float=None, percentail_upper:float=None) -> dict:
    '''
        Stats AECE SNA balance ratio.
        Params
            data: for calc
            percentail_lower: get low% index
            percentail_upper: get up% index
        Return
            config
    '''
    assert percentail_upper<1.0 and percentail_lower<percentail_upper

    config = {}
    tmp = data[PM + IONIC]
    tmp1 = data[PM + OCEC]

    # PM ratio
    tmp['sum'] = tmp[IONIC].apply(lambda x: x.sum(), axis=1)
    tmp['Ionic_ratio'] = tmp['sum']/tmp['PM25']
    
    # SNA balance
    tmp['SO42-NO3-_mol'] = tmp['SO42-']*2/96 + tmp['NO3-']/62
    tmp['NH4+_mol'] = tmp['NH4+']/18
    tmp['SNA_balance'] = tmp['SO42-NO3-_mol'] / tmp['NH4+_mol']
    config['SNA'] = {
        'stats_balance_upper': tmp['SNA_balance'].quantile(percentail_upper), 
        'stats_balance_lower': tmp['SNA_balance'].quantile(percentail_lower)
    } 
    # 阴离子
    tmp['AE'] = tmp['SO42-']/48 + tmp['NO3-']/62 + tmp['Cl-']/35.5 + tmp['F-']/19
    # 阳离子
    tmp['CE'] = tmp['Na+']/23 + tmp['NH4+']/18 + tmp['K+']/39 + tmp['Mg2+']/12 + tmp['Ca2+']/20
    tmp['AECE_balance'] = tmp['AE'] / tmp['CE']
    config['AECE'] = {
        'stats_ratio_upper': tmp['Ionic_ratio'].quantile(percentail_upper), 
        'stats_balance_lower': tmp['AECE_balance'].quantile(percentail_lower),
        'stats_balance_upper': tmp['AECE_balance'].quantile(percentail_upper)
    }
    # OC: OC/PM25, OC_float
    tmp1['OC/PM25'] = tmp1['OC'] / tmp1['PM25']
    config['OC'] = {'stats_ratio_upper': tmp1['OC/PM25'].quantile(percentail_upper)}
    # EC: EC/PM25, EC_float
    tmp1['EC/PM25'] = tmp1['EC'] / tmp1['PM25']
    config['EC'] = {'stats_ratio_upper': tmp1['EC/PM25'].quantile(percentail_upper)}
    # OCEC: OCEC/PM25, OC/EC ratio
    tmp1['OCEC/PM25'] = (tmp1['EC']+tmp1['OC']) / tmp1['PM25']
    tmp1['OC/EC'] = tmp1['OC'] / tmp1['EC']
    config['OCEC'] = {
        'stats_ratio_upper': tmp1['OCEC/PM25'].quantile(percentail_upper),
        'stats_balance_lower': tmp1['OC/EC'].quantile(percentail_lower),
        'stats_balance_upper': tmp1['OC/EC'].quantile(percentail_upper)
    }
    print(tmp[tmp.notna()].sample())
    print('-'*100)
    print(tmp1[tmp1.notna()].sample())

    return config


def get_exper(cfp):
    '''
        Record all metal. 
    '''
    for metal in METAL:
        if cfp.has_section(metal):
            cfp.set(metal, 'exper_lower', '0.0')
            cfp.set(metal, 'exper_upper', '1.0')
    # record 
    for indxer, dict0 in EXPER.items():
        cfp = check_section(cfp, indxer)
        for k, v in dict0.items():
            cfp.set(indxer, k, str(v))

    return cfp


def check_section(cfp, section: str):
    '''
        Check *.ini if section exists.
    '''
    if not cfp.has_section(section):
        cfp.add_section(section)

    return cfp


def get_float_thd(data, 
    float_percentile:float=None, 
    threshold_percentile:float=None) -> tuple:
    '''
        Calc float ratio x_percentile.
        Params
            data: calc samples
            float_percentile:  between [0.8, 1)
            threshold_percentile: between [0.8, 1)
    '''
    # print(data.info())
    assert float_percentile>=0.8 and float_percentile<1

    config_float, config_thd = {}, {}
    # calc float ratio
    for col in data[IONIC+OCEC].columns:
        tmp = data[IONIC+OCEC][[col]]
        # print(tmp.info())
        tmp['diff'] = tmp[col].diff()
        tmp['ratio'] = abs(tmp['diff'])/tmp[col]
        config_float[col] = tmp['ratio'].quantile(q=float_percentile)
    # calc threshold
    for col in data[METAL+OCEC+IONIC].columns:
        config_thd[col] = data[METAL+OCEC+IONIC][col].quantile(q=threshold_percentile)

    return config_float, config_thd


def write_index(data_dir: str, config_dir: str):
    '''
        Main process of read data, stats index, write into config files.
    '''
    assert os.path.exists(data_dir) and os.path.exists(config_dir)

    for i, f in enumerate(os.listdir(data_dir)):
        print('*'*100)
        stationcode = f.split('.')[0]
        print('{}\tCalc {} ...'.format(i+1, stationcode))
        datafile = os.path.join(data_dir, f)
        df = read_txt(datafile)
        # init cfp
        cfp = configparser.ConfigParser()
        # hyperparams threshold
        config_float, config_thd = get_float_thd(
            data=df, 
            float_percentile=STATS_FLOAT_UPPER, 
            threshold_percentile=STATS_UPPER)
        config_balance = get_balance(
            data=df, 
            percentail_lower=0.03, 
            percentail_upper=STATS_UPPER)

        # record stats index
        for k, val in config_float.items():
            cfp = check_section(cfp, k)
            if np.isnan(val):
                val =  -999.0
            cfp.set(k, "stats_float_upper", str(round(val, 5)))
        for k, val in config_thd.items():
            cfp = check_section(cfp, k)
            if np.isnan(val):
                val = -999.0
            cfp.set(k, "stats_upper", str(round(val, 5)))
        for k0, dict0 in config_balance.items():
            cfp = check_section(cfp, k0)
            for k1, val in dict0.items():
                if np.isnan(val):
                    val = -999.0
                cfp.set(k0, k1, str(round(val, 5)))
        # record exper index
        cfp = get_exper(cfp)
        # write index
        cfgfile = os.path.join(config_dir, '{}.ini'.format(stationcode))
        write2ini(cfgfile, cfp)  


def main():
    '''
        Main Func
    '''
    # src and dst
    data_src = paths.get('obs_addpm_dir')
    config_dst = paths.get('configs')
    # main calc
    write_index(data_src, config_dst)


if __name__ == "__main__":
    main()
