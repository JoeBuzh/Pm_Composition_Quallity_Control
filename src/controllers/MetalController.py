# -*- encoding: utf-8 -*-
'''
@Filename    : MetalController.py
@Datetime    : 2020/06/02 10:01:45
@Author      : Joe-Bu
@version     : 1.0
'''

import os
import sys
import configparser
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from src.controllers.Controller import Controller
from src.cfg import PM, METAL


class MetalController(Controller):
    '''
        Metal Quality Control Class.
    '''
    def __init__(self, check_time, raw_df, context, cfp_dir):
        super().__init__(
            name='metal_ctl', 
            check_time=check_time,
            raw_df=raw_df, 
            context=context,
            cfp_dir=cfp_dir)
        # -> Controller
        # self.qc_msg = {}
        # self.qc_data = None
        # self.qc_row = None
        self.thds = {}

    def _init_thd(self, stationcode):
        '''
            初始指定站点的阈值到self.thds
        '''
        cfp_file = os.path.join(self.cfp_dir, '{}.ini'.format(stationcode))
        cfp_tmp = configparser.ConfigParser()
        cfp_tmp.read(cfp_file)
        
        for section in cfp_tmp.sections():
            self.thds[section] = {}
            for k, _ in cfp_tmp.items(section):
                self.thds[section][k] = cfp_tmp.getfloat(section, k)

    def _check_miss(self):
        '''
            处理缺失.
        '''
        self.raw.replace(-999.0, np.nan, inplace=True)
        self.context.replace(-999.0, np.nan, inplace=True)

    def _check_thd(self, station, row, context):
        '''
            检查 数据 超过阈值
        '''
        tmp_dict = self.thds
        self.qc_row = row[['time','stationcode']+PM+METAL]

        for x in METAL:
            if x not in row.columns:
                self.qc_row[x] = np.nan
                continue
            val = row[x].values[0]
            self.qc_msg[station][x] = []
            if np.isnan(val):
                self.qc_msg[station][x].append(-999.0)
                self.qc_msg[station][x].append(u'缺失')
                continue
            self.qc_msg[station][x].append(np.round(val, 6))
            # 检查所有重金属阈值
            if tmp_dict[x]['exper_upper']!=-999.0 and val > tmp_dict[x]['exper_upper']:    
                self.qc_msg[station][x].append(
                    u'大于经验上限{}'.format(tmp_dict[x]['exper_upper']))
                # self.qc_data[x] = 
            if tmp_dict[x]['exper_lower']!=-999.0 and val < tmp_dict[x]['exper_lower']:    
                self.qc_msg[station][x].append(
                    u'小于经验下限{}'.format(tmp_dict[x]['exper_lower']))
                # self.qc_data[x] = 
            if tmp_dict[x]['stats_upper']!=-999.0 and val > tmp_dict[x]['stats_upper']:    
                self.qc_msg[station][x].append(
                    u'大于统计上限{}'.format(tmp_dict[x]['stats_upper']))
                # TODO: Add.
                self.qc_row[x] = np.nan

    def _check_single(self, station):
        '''
            质控单一站点所有内容
        '''
        _row = self.raw[self.raw['stationcode']==station]
        _context = self.context[self.context['stationcode']==station]
        print(_row)
        # print(_context)
        self._check_thd(station, _row, _context)

    def _qc_all(self):
        '''
            质控全部站点
        '''
        qc_list = []
        for station in self.raw['stationcode'].unique():
            print(station)
            self.qc_msg[station] = {}
            self._init_thd(station)
            self._check_single(station)
            qc_list.append(self.qc_row)

        self.qc_data = pd.concat(qc_list, join='outer')

    def step_control(self):
        '''
            内部主流程
        '''
        print(self.name)
        self._check_miss()
        self._qc_all()
        # 修改key为int类型
        self.qc_msg = {int(k): v for k, v in self.qc_msg.items()}

        return self.get_qc_msg()