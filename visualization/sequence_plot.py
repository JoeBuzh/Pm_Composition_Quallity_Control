# -*- encoding: utf-8 -*-
'''
@Filename    : squence_plot.py
@Datetime    : 2020/06/20 13:41:38
@Author      : Joe-Bu
@version     : 1.0
'''

import os
import sys
import xlrd
import json
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from cfg import duration, paths, mapping, PM, SNA, OCEC
from utils import get_env, checkdir, get_all_stations, read_data

plt.switch_backend('agg')
warnings.filterwarnings('ignore')

T_DOMAIN = duration
PATHS = paths


def ploter(obs_domain, qc_domain, fill_domain, stat_id):
    '''
        绘制时间范围内三类数据的时间序列图.
    '''
    start = T_DOMAIN.get('start', None)
    end = T_DOMAIN.get('end', None)
    out_dir = PATHS.get('save_dir')
    savedir = checkdir(os.path.join(out_dir, str(stat_id)))

    for _, x in enumerate(SNA+OCEC):
        plt.figure(figsize=(22, 18))
        for i, (name, color) in enumerate(zip(['obs','qc','fill'], ['y', 'r', 'b'])):
            ax = plt.subplot(3, 1, i+1)
            if i == 0:
                data = obs_domain
            elif i == 1:
                data = qc_domain
            elif i == 2:
                data = fill_domain
            ax.plot(data['time'], data[x], color=color, label='{}_{}'.format(name, x))
            ax.set_xlabel('Time (h)', fontsize=13)
            ax.set_ylabel('Conc (ug/m3)', fontsize=13)
            ax1 = ax.twinx()
            ax1.plot(data['time'], data['PM25'], color='g', label='PM25')
            ax1.set_ylabel('Conc (ug/m3)', fontsize=13)
            ax.set_title('{}_{}'.format(x, name), 
                    fontsize=14)
            # legennd
            ax.legend(fontsize=12, loc='upper left')
            ax1.legend(fontsize=12, loc='upper right')

        plt.savefig(os.path.join(
            savedir, '{}_{}_{}_{}'.format(stat_id, 
                                          x, 
                                          start.strftime("%Y%m%d%H"), 
                                          end.strftime("%Y%m%d%H"))))


def plot_all(ids: list):
    '''
        绘制配置中所有站点.
    '''
    for i, stat_id in enumerate(ids):
        print('Plot {}:\t{}'.format(i+1, stat_id))
        plot_station(stat_id)
    

def plot_station(stat_id: int):
    '''
        绘制单一站点.
    '''
    obs_file = os.path.join(paths.get('obs_dir'), '{}.txt'.format(stat_id))
    qc_file = os.path.join(paths.get('qc_dir'), '{}.txt'.format(stat_id))
    fill_file = os.path.join(paths.get('fill_dir'), '{}.txt'.format(stat_id))

    assert os.path.exists(obs_file) and os.path.exists(qc_file) and os.path.exists(fill_file)

    obs_data = read_data(obs_file)
    qc_data = read_data(qc_file)
    fill_data = read_data(fill_file)
    start = T_DOMAIN.get('start', None)
    end = T_DOMAIN.get('end', None)
    obs_domain = obs_data[(obs_data['time']>=start) & (obs_data['time']<=end)]
    qc_domain = qc_data[(qc_data['time']>=start) & (qc_data['time']<=end)]
    fill_domain = fill_data[(fill_data['time']>=start) & (fill_data['time']<=end)]

    ploter(obs_domain, qc_domain, fill_domain, stat_id)


def main():
    '''
        Main Func.
    '''
    # if get_env() == 'linux':
    #     plt.switch_backend('agg')
    # Time Domain
    start = duration.get('start', None)
    end = duration.get('end', None)
    # ids
    id_list = get_all_stations(mapping)
    print(start, end)
    # plot
    plot_all(id_list)



if __name__ == "__main__":
    main()
