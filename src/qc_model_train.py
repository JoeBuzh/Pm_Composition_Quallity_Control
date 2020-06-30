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
from sklearn.externals import joblib
from pyod.models.abod import ABOD
from pyod.models.cblof import CBLOF 
from pyod.models.feature_bagging import FeatureBagging
from pyod.models.hbos import HBOS
from pyod.models.iforest import IForest
from pyod.models.knn import KNN
from pyod.models.pca import PCA
from pyod.models.ocsvm import OCSVM
from pyod.models.lof import LOF

from .dao.get_rawdata import read_raw_txt, read_ini
from cfg import PM, IONIC, SNA, OCEC, METAL, MODE
from cfg import OUT_FRACTION, RANDOM_STATE, paths


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


def set_label(data: pd.DataFrame):
    '''
        打标签.
        暂不考虑监督学习，任务属于异常检测.
    '''
    pass


def define_model():
    '''
        Model Defination.
    '''
    # TODO: 检查算法
    classifiers = {
    'Angle_based_Outlier_Detector': ABOD(contamination=OUT_FRACTION),
    'Cluster_based_Local_Outlier_Factor': CBLOF(contamination=OUT_FRACTION, 
        check_estimator=False, random_state=RANDOM_STATE),
    'Feature_Bagging': FeatureBagging(
        LOF(n_neighbors=25), contamination=OUT_FRACTION, 
        check_estimator=False, random_state=RANDOM_STATE),
    'Histogram_base_Outlier_Detection': HBOS(contamination=OUT_FRACTION),
    'Isolation_Forest': IForest(contamination=OUT_FRACTION,random_state=RANDOM_STATE),
    # 'K_Nearest_Neighbors': KNN(contamination=OUT_FRACTION),
    'Average_KNN': KNN(method='mean',contamination=OUT_FRACTION),
    'PCA': PCA(svd_solver='auto'),
    'OCSVM': OCSVM(kernel='rbf', degree=4),
    'LOF': LOF()
    }

    return classifiers


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
    if data.shape[1] == 2:  
        _type = data.columns[-1]
    # PM25 OC EC
    elif data.shape[1] == 3:
        _type = 'OCEC'
    # PM25 SNA
    elif data.shape[1] == 4:
        _type = 'SNA'
    # PM25 IONIC
    elif data.shape[1] > 4:
        _type = 'IONIC'
    savedir = os.path.join(model_dir, _type)
    checkdir(savedir)
    # train multi-models
    for i, (clf_name, clf) in enumerate(models.items()):
        print('{}.\tfitting:\t{}'.format(i+1, clf_name))
        # print(data.shape)
        clf.fit(data)
        joblib.dump(clf, os.path.join(savedir, '{}.pkl'.format(clf_name)))


def main():
    '''
        Main.
    '''
    # dir
    raw_dir = paths.get('obs_data_raw')
    qc_dir = paths.get('obs_addpm_dir')
    model_dir = paths.get('models_qc')
    # unittest 基于环境检测总站数据
    f = '110000012.txt'
    rawfile, qc_file = os.path.join(raw_dir, f), os.path.join(qc_dir, f)
    # data
    raw_df, qc_df = get_dataset(rawfile, qc_file)
    
    if MODE == 'SINGLE':
        for x in IONIC+OCEC:
            train_set = select_data(PM[-1:]+[x], qc_df)
            # train_set = select_data([x], qc_df)
            models = define_model()
            train(train_set, models, model_dir)
    elif MODE == 'SNA':
        train_set = select_data(PM[-1:]+SNA, qc_df)
        # train_set = select_data(SNA, raw_df)
        models = define_model()
        train(train_set, models, model_dir)
    elif MODE == 'OCEC':
        train_set = select_data(PM[-1:]+OCEC, qc_df)
        # train_set = select_data(OCEC, raw_df)
        models = define_model()
        train(train_set, models, model_dir)
    elif MODE == 'IONIC':
        train_set = select_data(PM[-1:]+IONIC, qc_df)
        # train_set = select_data(IONIC, raw_df)
        models = define_model()
        train(train_set, models, model_dir)
    else:
        print('Error Mode.')
        sys.exit()


if __name__ == "__main__":
    main()
