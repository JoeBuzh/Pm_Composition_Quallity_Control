# -*- encoding: utf-8 -*-
'''
@Filename    : model_train.py
@Datetime    : 2020/06/04 22:54:31
@Author      : Joe-Bu
@version     : 1.0
'''

import os
import sys
import joblib
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import BaggingRegressor

from .dao.get_rawdata import read_raw_txt, read_ini
from cfg import paths, PM, IONIC, OCEC, METAL, FILL_SRC, FILL_DST


def get_dataset(raw_file, qc_file):
    '''
        获取原始与质控后数据.
        缺失已替换nan
    '''
    assert os.path.exists(raw_file) and os.path.exists(qc_file)

    cols = ['time','stationcode','longitude','latitude'] + PM + IONIC + OCEC + METAL
    raw_df = read_raw_txt(raw_file, header=cols)[1]
    qc_df = read_raw_txt(qc_file, header=cols)[1]
    raw_df.replace(-999.0, np.nan, inplace=True)
    qc_df.replace(-999.0, np.nan, inplace=True)

    return raw_df, qc_df


def define_model():
    '''
        Model Defination.
    '''
    # 扩展相关性算法
    regressors = {
        'LR': LinearRegression(fit_intercept=True),
        'SVR': SVR(kernel='linear'),
        'DTR': DecisionTreeRegressor(max_depth=3),
        'RFR': RandomForestRegressor(n_estimators=10, max_depth=3),
        'BGR': BaggingRegressor()
    }

    return regressors


def select_data(param_list: list, train_df):
    '''
        param_list 选择特征列, 训练不同的模型.
        train_df, 选择不同数据源: raw or qc.
    '''
    df = train_df[param_list]
    df.dropna(inplace=True)
    print(df.sample(5))

    return df


def checkdir(path: str):
    '''
        检查目录    
    '''
    if not os.path.exists(path):
        os.makedirs(path)

    assert os.path.exists(path)


def train(data, models, model_dir):
    '''
        Train.
    '''
    # TODO: 针对PM25缺失，是否考虑将其加入特征项
    # PM25 + param
    savedir = os.path.join(model_dir, FILL_DST[0])
    checkdir(savedir)
    # train multi-models
    for i, (reg_name, reg) in enumerate(models.items()):
        print('{}.\tfitting:\t{}'.format(i+1, reg_name))
        # print(data.shape)
        if len(FILL_SRC) == 1:
            X = data[FILL_SRC].values.reshape(-1,1)
            y = data[FILL_DST].values.reshape(-1,1) 
        else:
            X = data[FILL_SRC]
            y = data[FILL_DST]  

        reg.fit(X, y)
        joblib.dump(reg, os.path.join(savedir, '{}.pkl'.format(reg_name)))


def main():
    # Dir
    raw_dir = paths.get('obs_data_raw')
    qc_dir = paths.get('obs_addpm_dir')
    model_dir = paths.get('models_fill')
    # 基于检测总站的数据进行训练
    f = '110000012.txt'
    rawfile, qc_file = os.path.join(raw_dir, f), os.path.join(qc_dir, f)
    # Normally based on QC data
    raw_df, qc_df = get_dataset(rawfile, qc_file)
    # train data
    print(FILL_SRC+FILL_DST)
    train_set = select_data(FILL_SRC+FILL_DST, qc_df)
    models = define_model()

    assert len(FILL_DST) == 1
    train(train_set, models, model_dir)


if __name__ == "__main__":
    main()
