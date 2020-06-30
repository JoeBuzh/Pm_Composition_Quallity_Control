# -*- encoding: utf-8 -*-
'''
@Filename    : IonicController.py
@Datetime    : 2020/06/01 14:31:22
@Author      : Joe-Bu
@version     : 1.0
'''

import os
import sys
import json
sys.path.append('../src')
import warnings
warnings.filterwarnings('ignore')
import configparser
from copy import deepcopy
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sklearn.externals import joblib

from src.controllers.Controller import Controller
from src.cfg import PM, IONIC, SNA, OUT_FRACTION, RANDOM_STATE


class IonicController(Controller):
    '''
        Water Soluble Ionic Quality Controll Class.
    '''
    def __init__(self, check_time, raw_df, context, cfp_dir, qc_model_dir, fill_model_dir):
        super().__init__(
            name='ionic_ctl',
            check_time = check_time, 
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
            初始化所有站点的阈值为dict.
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
        df['ionic'] = df[IONIC].apply(lambda x: x.sum(), axis=1)
        df['SNA'] = df[SNA].apply(lambda x: x.sum(), axis=1)
        df['AE/CE'] = df[IONIC].apply(calc_AECE, axis=1)
        df['SO42-NO3-_mol'] = df['SO42-']*2/96 + df['NO3-']/62
        df['NH4+_mol'] = df['NH4+']/18
        df['SNA_balance'] = df['SO42-NO3-_mol'] / df['NH4+_mol']

        return df

    def _check_balance(self, station, row, context):
        '''
            检查 AECE SNA 平衡
        '''
        tmp_dict = self.thds
        self.qc_msg[station]['AE/CE'] = []
        if np.isnan(row['AE/CE'].values[0]):
            self.qc_msg[station]['AE/CE'].append(u'无AECE结果')
        else:
            val = np.round(row['AE/CE'].values[0], 3)
            self.qc_msg[station]['AE/CE'].append(val)
            if tmp_dict['AECE']['exper_balance_lower']!=-999.0 and val < tmp_dict['AECE']['exper_balance_lower']:
                self.qc_msg[station]['AE/CE'].append(
                    u'小于经验平衡阈值下限{}'.format(tmp_dict['AECE']['exper_balance_lower'])
                )
            if tmp_dict['AECE']['exper_balance_upper']!=-999.0 and val > tmp_dict['AECE']['exper_balance_upper']:
                self.qc_msg[station]['AE/CE'].append(
                    u'大于经验平衡阈值上限{}'.format(tmp_dict['AECE']['exper_balance_upper'])
                )
            if tmp_dict['AECE']['stats_balance_lower']!=-999.0 and val < tmp_dict['AECE']['stats_balance_lower']:
                self.qc_msg[station]['AE/CE'].append(
                    u'小于统计平衡阈值下限{}'.format(tmp_dict['AECE']['stats_balance_lower'])
                )
            if tmp_dict['AECE']['stats_balance_upper']!=-999.0 and val > tmp_dict['AECE']['stats_balance_upper']:
                self.qc_msg[station]['AE/CE'].append(
                    u'大于统计平衡阈值上限{}'.format(tmp_dict['AECE']['stats_balance_upper'])
                )

        self.qc_msg[station]['SNA'] = []
        if np.isnan(row['SNA_balance'].values[0]):
            self.qc_msg[station]['SNA'].append(u'无SNA_balance结果')
        else:
            val = np.round(row['SNA_balance'].values[0], 3)
            self.qc_msg[station]['SNA'].append(val)
            if tmp_dict['SNA']['exper_balance_lower']!=-999.0 and val < tmp_dict['SNA']['exper_balance_lower']:
                self.qc_msg[station]['SNA'].append(
                    u'小于经验平衡阈值下限{}'.format(tmp_dict['SNA']['exper_balance_lower'])
                )
            if tmp_dict['SNA']['exper_balance_upper']!=-999.0 and val > tmp_dict['SNA']['exper_balance_upper']:
                self.qc_msg[station]['SNA'].append(
                    u'大于经验平衡阈值上限{}'.format(tmp_dict['AECE']['exper_balance_upper'])
                )
            if tmp_dict['SNA']['stats_balance_lower']!=-999.0 and val < tmp_dict['SNA']['stats_balance_lower']:
                self.qc_msg[station]['SNA'].append(
                    u'小于统计平衡阈值下限{}'.format(tmp_dict['SNA']['stats_balance_lower'])
                )
            if tmp_dict['SNA']['stats_balance_upper']!=-999.0 and val > tmp_dict['SNA']['stats_balance_upper']:
                self.qc_msg[station]['SNA'].append(
                    u'大于统计平衡阈值上限{}'.format(tmp_dict['SNA']['stats_balance_upper'])
                )
            
    def _check_thd(self, station, row, context):
        '''
            检查 数据浮动 超过阈值
        '''
        tmp_dict = self.thds
        self.qc_row = row[['time','stationcode']+PM+IONIC]

        for x in IONIC:
            if x not in row.columns:
                self.qc_row[x] = np.nan
                continue
            val = row[x].values[0]
            self.qc_msg[station][x] = []
            if np.isnan(val):
                self.qc_msg[station][x].append(-999.0)
                self.qc_msg[station][x].append(u'缺失')
                continue
            val = np.round(val, 6)
            self.qc_msg[station][x].append(val)
            # 检查所有水溶性离子阈值与变化情况
            if tmp_dict[x]['stats_upper']!=-999.0 and val > tmp_dict[x]['stats_upper']:    
                self.qc_msg[station][x].append(
                    u'大于分布统计上限{}'.format(tmp_dict[x]['stats_upper']))
                self.qc_row[x] = np.nan
            if tmp_dict[x]['stats_float_upper']!=-999.0 and abs(context[x].diff().max()) > tmp_dict[x]['stats_float_upper']:    
                self.qc_msg[station][x].append(
                    u'{}大于前后浮动统计上限{}'.format(
                        abs(context[x].diff().max()),
                        tmp_dict[x]['stats_float_upper']))
                self.qc_row[x] = np.nan
            # 检查 SNA组分 相关
            if x in SNA:
                if tmp_dict[x]['exper_lower']!=-999.0 and val < tmp_dict[x]['exper_lower']:
                    self.qc_msg[station][x].append(
                        u'小于经验阈值下限{}'.format(tmp_dict[x]['exper_lower']))
                if tmp_dict[x]['exper_upper']!=-999.0 and val > tmp_dict[x]['exper_upper']:
                    self.qc_msg[station][x].append(
                        u'大于经验阈值上限{}'.format(tmp_dict[x]['exper_upper']))
                if tmp_dict[x]['exper_float_upper']!=-999.0 and abs(context[x].diff().max()) > tmp_dict[x]['exper_float_upper']:
                    self.qc_msg[station][x].append(
                        u'{}大于前后浮动经验上限{}'.format(
                            abs(context[x].diff().max()),
                            tmp_dict[x]['exper_float_upper']))

    def _check_single(self, station):
        '''
            质控单一站点所有内容
        '''
        _row = self.raw[self.raw['stationcode']==station]
        _context = self.context[self.context['stationcode']==station]
        print(_row)
        self._check_thd(station, _row, _context)
        self._check_balance(station, _row, _context)

    def _model_predict(self, df, model_dir, _type, src=None):
        '''
            9个异常识别模型综合判别，最后voting取得结果
            _type 选择特征项
        '''
        # print(df)
        for name, _ in self.qc_models.items():
            model_file = os.path.join(model_dir, '{}.pkl'.format(name))
            model = joblib.load(model_file)
            if len(_type) == 1:
                df[name] = model.predict(df[_type].values.reshape(-1, 1))
            else:
                df[name] = model.predict(df[_type])
        df['ensemble'] = df[self.qc_models.keys()].apply(lambda x: x.sum(), axis=1)
        df['ensemble'] = [1 if x > 4 else 0 for x in df['ensemble']]
        # print(df)
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
            模型异常识别
        '''
        # 初始化模型
        self._qc_model_define()
        # 单变量模型
        for x in IONIC:
            df = self.raw[['stationcode', 'PM25', x]]
            df.dropna(inplace=True)
            # print(df)
            if len(df) == 0:
                print('No {} data'.format(x))
                continue
            else:
                model_dir = os.path.join(self.qc_model_dir, x)
                self._model_predict(df, model_dir, ['PM25', x], src=x)
                
        # SNA模型
        df_sna = self.raw[['stationcode', 'PM25'] + SNA]
        df_sna.dropna(inplace=True)
        # print(df_sna)
        if len(df_sna) == 0:
            print('No SNA data.')
        else:
            model_dir = os.path.join(self.qc_model_dir, 'SNA')
            self._model_predict(df_sna, model_dir, ['PM25']+SNA, src='SNA')
            
        # 全变量模型
        df_ionic = self.raw[['stationcode', 'PM25'] + IONIC]
        df_ionic.dropna(inplace=True)
        # print(df_ionic)
        if len(df_ionic) == 0:
            print('No Ionic data.')
        else:
            model_dir = os.path.join(self.qc_model_dir, 'IONIC')
            self._model_predict(df_ionic, model_dir, ['PM25']+IONIC, src='IONIC')

    def _model_fill(self):
        '''
            模型填数.
            目前针对 PM25 -> SO42- NO3- NH4+ 
        '''
        self._fill_model_define()
        self.fill_data = deepcopy(self.qc_data)

        for x in SNA:
            df0 = self.fill_data[self.qc_data[PM[-1]].notna() & self.qc_data[x].isna()]
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
            self.fill_data = pd.concat([df1, df0])
        
        print(self.fill_data)
        print('~'*100)

    def _qc_all(self):
        '''
            质控全部站点
        '''
        qc_lsit = []
        for station in self.raw['stationcode'].unique():
            print('-'*100)
            print(station)
            self.qc_msg[station] = {}
            self._init_thd(station)
            self._check_single(station)
            qc_lsit.append(self.qc_row)

        self.qc_data = pd.concat(qc_lsit, join='outer')

    def step_control(self):
        '''
            内部主流程
        '''
        print(self.name)
        self._check_miss()
        self.raw = self._calc_index(self.raw)
        self.context = self._calc_index(self.context)
        self._qc_all()
        self._check_model()
        # 修改key为int类型
        self.qc_msg = {int(k): v for k, v in self.qc_msg.items()}
        # 审核后填数
        print('*'*100)
        print(self.qc_data)
        self._model_fill()

        return self.get_qc_msg()


def calc_AECE(x):
    _CE = x['Na+']/23 + x['NH4+']/18 + x['K+']/18 + x['Mg2+']/12 + x['Ca2+']/20
    _AE = x['SO42-']/48 + x['NO3-']/62 + x['Cl-']/35.5 + x['F-']/19

    return _AE/_CE