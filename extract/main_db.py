# -*- encoding: utf-8 -*-
'''
@Filename    : main.py
@Datetime    : 2020/05/13 11:19:11
@Author      : Joe-Bu
@version     : 1.0
@description : 主程序
               暂时确定的方案 - 数据按照小时为文件
               当小时文件中含目前数据库内存在的组分观测站点的数据
               -999.0为无效
               保存至obs_com_yyyymmhh.txt
'''

from __future__ import print_function

import os
import sys
import calendar
import traceback
from copy import deepcopy
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import psycopg2

from getErrTime import parse_err_time
from cfg import db_info, paths, lizi_cn, lizi_en, ocec_cn, ocec_en 
from cfg import jins_cn, jins_en, aqi_cn, aqi_en
from cfg import PM, IONIC, OCEC, METAL
from utils.utils_workflow import get_station_code, checkdir, fetch_data 


def sql_hourly(dt, composition: dict, stationcode) -> str:
    '''
        基于组分参数、站点位置，获取单小时所有站点的数据.
    '''
    params = tuple(k for k, _ in composition.items())
    stations = tuple(str(m) for m in stationcode)

    if 29 in params:
        sql0 = '''
            SELECT a.lst as time, a.stationcode, a.parameterid, b.name, round(a.value/1000, 5) as value 
            from data_{0} as a
            LEFT JOIN "parameter" as b ON a.parameterid=b.parameterid
            WHERE a.lst='{1}'
            and a.parameterid in {2}
            and a.stationcode in {3}
            and a.qccode=0
            and a.value>=0;'''.format(
                dt.strftime("%Y%m"),
                dt.strftime("%Y-%m-%d %H:00:00"),
                params,
                stations)
        return sql0

    sql = '''
        SELECT a.lst as time, a.stationcode, a.parameterid, b.name, a.value 
        from data_{0} as a
        LEFT JOIN "parameter" as b ON a.parameterid=b.parameterid
        WHERE a.lst='{1}'
        and a.parameterid in {2}
        and a.stationcode in {3}
        and a.qccode=0
        and a.value>=0;'''.format(
            dt.strftime("%Y%m"), 
            dt.strftime("%Y-%m-%d %H:00:00"), 
            params,
            stations)

    return sql


def reshape(raw_df, dict_cn: dict, dict_en: dict):
    tmp_df = raw_df[['stationcode', 'name', 'value']].set_index(['stationcode', 'name'], append=True)
    # handle different instruments: sum mean max min
    new_df = tmp_df.unstack().groupby('stationcode').max()
    new_df[new_df<=0] = np.nan
    new_df.columns = [x for _,x in new_df.columns.values]

    trans_dict = {v1:v2 for (k1, v1),(k2, v2) in zip(dict_cn.items(), dict_en.items())}
    new_df = new_df.rename(columns=trans_dict)
    # 填补无记录的字段
    for col in dict_en.values():
        if col not in new_df.columns:
            new_df[col] = np.nan
        else:
            continue

    return new_df


def filter_prefer(df, lists: list, src: str):
    '''
        按照优先级筛选
    '''
    if '{}_trans'.format(src) in lists:
        return df['{}_trans'.format(src)]

    elif '{}_refl'.format(src) in lists:
        return df['{}_refl'.format(src)]

    elif '{}_optics'.format(src) in lists:
        return df['{}_optics'.format(src)]

    elif '{}_raw'.format(src) in lists:
        return df['{}_raw'.format(src)]


def calc_ocec(raw_df):
    '''
        根据所有OCEC的参数，根据优先级，计算汇总OC、EC的值;
        *** 优先级 --> 透射 > 反射 > 光学 > 元素
        raw_df.shape -> new_df.shape(, 2)
    '''
    ec_list = [ec for ec in raw_df.columns if ec.startswith('EC')]
    oc_list = [oc for oc in raw_df.columns if oc.startswith('OC')]

    raw_df['OC'] = filter_prefer(raw_df, oc_list, 'OC')
    raw_df['EC'] = filter_prefer(raw_df, ec_list, 'EC')

    return raw_df[['OC', 'EC']]


def index_obj2int(df):
    '''
        将df的index类型进行转换，str -> int
    '''
    df.index = pd.to_numeric(df.index, errors='coerce')

    return df


def get_hourly_data(db_info, dt, stations, savepath):
    '''
        Extract One Datetime.
    '''
    checkdir(savepath)
    # set index
    base_info = stations[['stationcode', 'longitude', 'latitude']].set_index('stationcode')
    decimals = pd.Series([3, 3], index=['longitude', 'latitude'])
    base_info = base_info.round(decimals)
    stationcode = stations['stationcode']
    # sql
    lizi_sql = sql_hourly(dt, lizi_en, stationcode)
    ocec_sql = sql_hourly(dt, ocec_en, stationcode)
    jins_sql = sql_hourly(dt, jins_en, stationcode)
    aqi_sql = sql_hourly(dt, aqi_en, stationcode)
    # get data
    if fetch_data(db_info, lizi_sql)[0]:
        _, lizi = fetch_data(db_info, lizi_sql)
        lizi_df = reshape(lizi, lizi_cn, lizi_en)
        lizi_df = index_obj2int(lizi_df)
    else:
        lizi_df = pd.DataFrame(index=stationcode, columns=IONIC)
        # lizi_df = index_obj2int(lizi_df.index)
        
    if fetch_data(db_info, ocec_sql)[0]:
        _, ocec = fetch_data(db_info, ocec_sql)
        ocec_df = reshape(ocec, ocec_cn, ocec_en)
        ocec_new = calc_ocec(ocec_df)
        ocec_new = index_obj2int(ocec_new)
    else:
        ocec_new = pd.DataFrame(index=stationcode, columns=OCEC)
        # ocec_new = index_obj2int(ocec_new.index)
        
    if fetch_data(db_info, jins_sql)[0]:
        _, jins = fetch_data(db_info, jins_sql)
        jins_df = reshape(jins, jins_cn, jins_en)
        jins_df = index_obj2int(jins_df)
    else:
        jins_df = pd.DataFrame(index=stationcode, columns=METAL)
        # jins_df = index_obj2int(jins_df.index)

    if fetch_data(db_info, aqi_sql)[0]:
        _, aqi = fetch_data(db_info, aqi_sql)
        aqi_df = reshape(aqi, aqi_cn, aqi_en)
        aqi_df = index_obj2int(aqi_df)
    else:
        aqi_df = pd.DataFrame(index=stationcode, columns=PM)
        # aqi_df = index_obj2int(aqi_df.index)

    # sys.exit()
    
    # merge composition
    comp_0 = aqi_df.merge(lizi_df, left_on='stationcode', right_on='stationcode', how='outer')
    comp_1 = comp_0.merge(ocec_new, left_on='stationcode', right_on='stationcode', how='outer')
    comp_2 = comp_1.merge(jins_df, left_on='stationcode', right_on='stationcode', how='outer')
    # merge lon+lat
    all_df = base_info.merge(comp_2, left_on='stationcode', right_on='stationcode', how='outer')
    all_df.fillna(-999.0, inplace=True)

    # save
    all_df.to_csv(
        os.path.join(paths['savepath'], 'obs_com_{}.txt'.format(dt.strftime("%Y%m%d%H"))),
        sep=',', 
        encoding='utf-8',
        float_format='%.3f')


def main():
    '''
        Main.
    '''
    stations = get_station_code(localfile=paths['stationfile'])
    err_time = parse_err_time(paths.get('err_file'))

    for _, t_str in enumerate(err_time):
        dtime = datetime.strptime(t_str, "%Y%m%d%H")
        print("processing {} ...".format(dtime.strftime("%Y-%m-%d %H")))
        get_hourly_data(db_info, dtime, stations, paths['savepath'])


if __name__ == "__main__":
    main()
