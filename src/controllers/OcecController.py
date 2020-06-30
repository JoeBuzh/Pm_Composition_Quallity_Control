# -*- encoding: utf-8 -*-
'''
@Filename    : OcecController.py
@Datetime    : 2020/06/02 10:41:01
@Author      : Joe-Bu
@version     : 1.0
'''

import os
import sys
import configparser
from copy import deepcopy
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sklearn.externals import joblib

from src.controllers.Controller import Controller
from src.cfg import PM, OCEC, OUT_FRACTION, RANDOM_STATE

class OcecController(Controller):
    '''
        OCEC Quality Control Class.
    '''
    def __init__(self, check_time, raw_df, context, cfp_dir, qc_model_dir, fill_model_dir):
        super().__init__(
            name='ocec_ctl', 
            check_time=check_time,
            raw_df=raw_df, 
            context=context,
            cfp_dir=cfp_dir)
        # -> Controller
        # self.qc_msg = {}
        # self.qc_data = None
        # self.qc_row = None
        self.thds = {}
        self.qc_model_dir = qc_model_dir
        self.fill_model_dir = fill_model_dir

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

    def _calc_index(self, df):
        '''
            计算相关指标.
        '''
        print(df)
        df['OCEC'] = df[OCEC].apply(lambda x: x.sum(), axis=1)
        df['OC/PM25'] = df['OC'] / df['PM25']
        df['EC/PM25'] = df['EC'] / df['PM25']
        df['OC/EC'] = df['OC'] / df['EC']
        df['OCEC/PM25'] = df['OCEC'] / df['PM25']
        
        return df

    def _check_balance(self, station, row, context):
        '''
            检查 OC/EC
        '''
        # TODO: 
        tmp_dict = self.thds
        self.qc_msg[station]['OC/EC'] = []
        if np.isnan(row['OC/EC'].values[0]):
            self.qc_msg[station]['OC/EC'].append(u'无OC/EC结果')
        else:
            val = np.round(row['OC/EC'].values[0], 3)
            self.qc_msg[station]['OC/EC'].append(val)
            if tmp_dict['OCEC']['exper_balance_lower']!=-999.0 and val < tmp_dict['OCEC']['exper_balance_lower']:
                self.qc_msg[station]['OC/EC'].append(
                    u'{}小于经验斜率阈值下限{}'.format(val, tmp_dict['OCEC']['exper_balance_lower'])
                )
            if tmp_dict['OCEC']['exper_balance_upper']!=-999.0 and val > tmp_dict['OCEC']['exper_balance_upper']:
                self.qc_msg[station]['OC/EC'].append(
                    u'{}大于经验斜率阈值上限{}'.format(val, tmp_dict['OCEC']['exper_balance_upper'])
                )
            if tmp_dict['OCEC']['stats_balance_lower']!=-999.0 and val < tmp_dict['OCEC']['stats_balance_lower']:
                self.qc_msg[station]['OC/EC'].append(
                    u'{}小于统计斜率阈值下限{}'.format(val, tmp_dict['OCEC']['stats_balance_lower'])
                )
            if tmp_dict['OCEC']['stats_balance_upper']!=-999.0 and val > tmp_dict['OCEC']['stats_balance_upper']:
                self.qc_msg[station]['OC/EC'].append(
                    u'{}大于统计斜率阈值上限{}'.format(val, tmp_dict['OCEC']['stats_balance_upper'])
                )

    def _check_thd(self, station, row, context):
        '''
            检查 数据浮动 OC/PM25 EC/PM25 OCEC/PM25 超过阈值
        '''
        # TODO:
        tmp_dict = self.thds
        self.qc_row = row[['time','stationcode']+PM+OCEC]

        for x in ['OC', 'EC', 'OCEC']:
            val = row['{}/PM25'.format(x)].values[0]
            self.qc_msg[station][x] = []
            if np.isnan(val) or val == 0.0:
                self.qc_msg[station][x].append(-999.0)
                self.qc_msg[station][x].append(u'缺失')
                continue
            val = np.round(val, 6)
            self.qc_msg[station][x].append(val)
            # 检查所有 OC/PM25 EC/PM25 阈值
            if tmp_dict[x]['exper_ratio_upper']!=-999.0 and val > tmp_dict[x]['exper_ratio_upper']:    
                self.qc_msg[station][x].append(
                    u'{}大于占比经验上限{}'.format(val, tmp_dict[x]['exper_ratio_upper']))
                if x == 'OCEC':
                    pass
                else:
                    self.qc_row[x] = np.nan
            if tmp_dict[x]['stats_ratio_upper']!=-999.0 and val > tmp_dict[x]['stats_ratio_upper']:    
                self.qc_msg[station][x].append(
                    u'{}大于占比统计上限{}'.format(val, tmp_dict[x]['stats_ratio_upper']))
                if x == 'OCEC':
                    pass
                else:
                    self.qc_row[x] = np.nan
            # 检查OC EC变化浮动比率
            if x == 'OCEC':
                continue
            if tmp_dict[x]['exper_float_upper']!=-999.0 and abs(context[x].diff().max()) > tmp_dict[x]['exper_float_upper']:    
                self.qc_msg[station][x].append(
                    u'{}大于前后浮动经验上限{}'.format(
                        abs(context[x].diff().max()), 
                        tmp_dict[x]['exper_float_upper']))
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
        self._check_balance(station, _row, _context)

    def _model_predict(self, df, model_dir, _type, src=None):
        '''
            9个异常识别模型综合判别，最后voting取得结果
            _type 选择特征项
        '''
        print(df[_type].shape)
        for name, _ in self.qc_models.items():
            model_file = os.path.join(model_dir, '{}.pkl'.format(name))
            model = joblib.load(model_file)
            df[name] = model.predict(df[_type])
        df['ensemble'] = df[self.qc_models.keys()].apply(lambda x: x.sum(), axis=1)
        df['ensemble'] = [1 if x > 4 else 0 for x in df['ensemble']]
        print(df)
        for _, row in df.iterrows():
            # stationcode
            if not self.qc_msg.__contains__(int(row['stationcode'])):
                self.qc_msg[int(row['stationcode'])] = {}
            # src 
            if not self.qc_msg[int(row['stationcode'])].__contains__(src):
                self.qc_msg[int(row['stationcode'])][src] = []
            # Add 
            self.qc_msg[int(row['stationcode'])][src].append(
                u'模型判别异常' if row['ensemble']==1 else u'模型判别正常')

    def _check_model(self):
        '''
            模型异常识别过程
        '''
        # 初始化模型
        self._qc_model_define()
        # 单变量模型
        for x in OCEC:
            df = self.raw[['stationcode', 'PM25', x]]
            df.dropna(inplace=True)
            if len(df) == 0:
                print('No {} data'.format(x))
                continue
            else:
                model_dir = os.path.join(self.qc_model_dir, x)
                self._model_predict(df, model_dir, ['PM25', x], src=x)
            
        # 全变量模型
        df_ocec = self.raw[['stationcode', 'PM25'] + OCEC]
        df_ocec.dropna(inplace=True)
        if len(df_ocec) == 0:
            print('No Ionic data.')
        else:
            model_dir = os.path.join(self.qc_model_dir, 'OCEC')
            self._model_predict(df_ocec, model_dir, ['PM25','OC','EC'], src='OCEC')

    def _model_fill(self):
        '''
            模型填数.
            目前针对 PM25 -> OC EC 
        '''
        self._fill_model_define()
        self.fill_data = deepcopy(self.qc_data)

        for x in OCEC:
            df0 = self.fill_data[self.fill_data[PM[-1]].notna() & self.fill_data[x].isna()]
            df1 = self.fill_data.append(df0).drop_duplicates(keep=False)
            if len(df0) == 0:
                continue
            for name, _ in self.fill_models.items():
                model_dir = os.path.join(self.fill_model_dir, x)
                model_file = os.path.join(model_dir, '{}.pkl'.format(name))
                model = joblib.load(model_file)    
                df0[name] = self._fill_value(df0, PM[-1:], [x], model)
            df0[x] = df0[self.fill_models.keys()].apply(lambda x:np.mean(x), axis=1)
            df0.drop(columns=self.fill_models.keys(), inplace=True)
            self.fill_data = pd.concat([df0, df1])
        print(self.fill_data)
        print('~'*100)

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
        if set(OCEC) < set(self.raw.columns):
            self.raw = self._calc_index(self.raw)
            print(self.raw)
            self.context = self._calc_index(self.context)
            self._qc_all()
            self._check_model()
            # 修改key为int类型
            self.qc_msg = {int(k): v for k, v in self.qc_msg.items()}
            self._model_fill()

            return self.get_qc_msg()
        else:
            print(self.raw)
            self.qc_data = self.raw
            # self.qc_data['time'] =
            self.qc_data['OC'] = np.nan
            self.qc_data['EC'] = np.nan
            self._model_fill()
            print(self.fill_data)
            return self.get_qc_msg()