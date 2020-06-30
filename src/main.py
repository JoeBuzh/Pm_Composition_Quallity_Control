# -*- encoding: utf-8 -*-
'''
@Filename    : main.py
@Datetime    : 2020/06/01 11:21:30
@Author      : Joe-Bu
@version     : 1.0
'''

import os
import sys
import json
import configparser
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from cfg import paths, hour_range, PM, OCEC, METAL
from .mylog.logger import init_logger as lg
from .dao.get_rawdata import read_raw_txt, read_ini
from .dao.write2file import write2ini
from .utils.utils_main import split_obs, concat_data, checkdir
from .controllers.IonicController import IonicController
from .controllers.MetalController import MetalController
from .controllers.OcecController import OcecController


def merge_qc(qc_ionic_data, qc_ocec_data, qc_metal_data, raw_df):
    '''
        三类数据合并.
    '''
    qc_data0 = pd.merge(
        qc_ionic_data, 
        qc_ocec_data.drop(columns=PM), 
        left_on='stationcode', right_on='stationcode', how='outer')
    qc_data1 = pd.merge(
        qc_data0, 
        qc_metal_data.drop(columns=PM), 
        left_on='stationcode', right_on='stationcode', how='outer')
    qc_data = pd.merge(
        raw_df[['stationcode','longitude', 'latitude']],
        qc_data1,
        left_on='stationcode', right_on='stationcode', how='outer')
    qc_data.fillna(-999.0, inplace=True)

    return qc_data


def qc_hourly(paths, this_time, hour_range):
    '''
        Main QC Process.
    '''
    # 质控输入目录
    obs_dir = paths.get('input_obs')
    # 阈值参数目录
    cfg_dir = paths.get('configs')
    # 输出路径
    out_logs = paths.get('output_logs')
    out_data = paths.get('output_data')
    # 模型目录
    qc_model_dir = paths.get('models_qc')
    fill_model_dir = paths.get('models_fill')
    # 时间确认
    check_time = this_time - timedelta(hours=1)
    dt_list = [this_time - timedelta(hours=i) for i in range(hour_range)]
    # 读取数据, 当小时质控前一小时数据
    raw_df = read_raw_txt(os.path.join(obs_dir, 'obs_com_{}.txt'.format(check_time.strftime("%Y%m%d%H"))))[1]
    raw_df['time'] = check_time
    # 包含前后时次在内的三个时次数据
    context_df = concat_data(dt_list, obs_dir)
    # 数据切分
    raw_ionic, raw_ocec, raw_metal = split_obs(raw_df)
    context_ionic, context_ocec, context_metal = split_obs(context_df)
    # 数据质控
    ionic_ctl = IonicController(
        check_time, raw_ionic, context_ionic, cfg_dir, qc_model_dir, fill_model_dir)
    ocec_ctl = OcecController(
        check_time, raw_ocec, context_ocec, cfg_dir, qc_model_dir, fill_model_dir)
    metal_ctl = MetalController(check_time, raw_metal, context_metal, cfg_dir)
    # 质控器
    qc_ionic_log = ionic_ctl.step_control()
    qc_ionic_data = ionic_ctl.get_qc_data().drop(columns='time')
    qc_ionic_fill = ionic_ctl.get_fill_data().drop(columns='time')
    qc_ocec_log = ocec_ctl.step_control()
    qc_ocec_data = ocec_ctl.get_qc_data().drop(columns='time')
    qc_ocec_fill = ocec_ctl.get_fill_data().drop(columns='time')
    qc_metal_log = metal_ctl.step_control()
    qc_metal_data = metal_ctl.get_qc_data().drop(columns='time')

    # 合并 质控后&填补后 数据
    qc_data = merge_qc(qc_ionic_data, qc_ocec_data, qc_metal_data, raw_df)
    fill_data = merge_qc(qc_ionic_fill, qc_ocec_fill, qc_metal_data, raw_df)
    qc_file = os.path.join(out_data, 'qc_obs_{}.txt'.format(check_time.strftime("%Y%m%d%H")))
    fill_file = os.path.join(out_data, 'fill_obs_{}.txt'.format(check_time.strftime("%Y%m%d%H")))
    qc_data.to_csv(
        qc_file, header=True, sep=',', index=False, 
        encoding='utf-8', float_format='%.5f')
    fill_data.to_csv(
        fill_file, header=True, sep=',', index=False, 
        encoding='utf-8', float_format='%.5f')

    # 合并质控结果log
    qc_log_all = qc_ionic_log
    for k, _ in qc_ocec_log.items():
        if qc_ocec_log.__contains__(k):
            qc_log_all[k].update(qc_ocec_log[k])
        else:
            qc_log_all[k] = qc_ocec_log[k]
    for k, _ in qc_metal_log.items():
        if qc_log_all.__contains__(k):
            qc_log_all[k].update(qc_metal_log[k])
        else:
            qc_log_all[k] = qc_metal_log[k]

    report = os.path.join(out_logs, 'qc_{}.json'.format(check_time.strftime("%Y%m%d%H")))
    with open(report, 'w', encoding='utf-8') as jsonfile:
        json.dump(qc_log_all, jsonfile, ensure_ascii=False, indent=4)


def main():
    '''
        Main. 
        Time Loop.
    '''
    # unittest
    #now = datetime(2019, 1, 2, 12, 0)
    #qc_hourly(path, now, hour_range)
    #sys.exit()

    # month test
    print('Start at:\t', datetime.now())

    start = datetime(2019, 10, 23, 10, 0)
    end = datetime(2019, 12, 31, 23, 0)
    # Hourly Loop
    while start <= end:
        qc_hourly(paths, start, hour_range)
        start += timedelta(hours=1)

    print('E-n-d at:\t', datetime.now())


if __name__ == "__main__":
    main()
