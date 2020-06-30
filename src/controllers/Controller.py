# -*- encoding: utf-8 -*-
'''
@Filename    : Controller.py
@Datetime    : 2020/06/02 10:07:43
@Author      : Joe-Bu
@version     : 1.0
'''

import os
import sys
sys.path.append('../')
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

from src.cfg import OUT_FRACTION, RANDOM_STATE
from src.qc_model_train import define_model as define_qc_models
from src.fill_model_train import define_model as define_fill_models

class Controller(object):
    '''
        Base Controller Class.
        Params
            name -> identify name
            dt -> now time
            raw_df -> raw data
            context -> last now next
            cfp_dir  -> .ini file dir
    '''
    def __init__(self, name, check_time, raw_df, context, cfp_dir):
        '''
            Base Class Init.
        '''
        self.name = name
        self.check_time = check_time
        self.raw = raw_df
        self.context = context
        self.cfp_dir = cfp_dir
        self.qc_msg = {}
        self.qc_data = None
        self.fill_data = None
        self.qc_row = None

    def _qc_model_define(self):
        '''
            Init QC Model Method.
        '''
        self.qc_models = define_qc_models()

    def _fill_model_define(self):
        '''
            Init Fill Model Method.
        '''
        self.fill_models = define_fill_models()

    def _fill_value(self, data, src: list, dst: list, model):
        '''
            Predict Method to Fill Value.
        '''
        if len(src) == 1:
            X = data[src].values.reshape(-1,1)
        else:
            X = data[src]
        y_pred = model.predict(X)

        return y_pred

    def get_name(self):
        print(self.name)

    def set_name(self, name):
        self.name = name

    def get_qc_msg(self):
        '''
            Get qc msg dict.
        '''
        return self.qc_msg

    def get_qc_data(self):
        '''
            Get qc data.
        '''
        return self.qc_data

    def get_fill_data(self):
        '''
            Get filled data
        '''
        return self.fill_data