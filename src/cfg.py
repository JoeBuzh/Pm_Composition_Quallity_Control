# -*- encoding: utf-8 -*-
'''
@Filename    : cfg.py
@Datetime    : 2020/06/08 14:30:27
@Author      : Joe-Bu
@version     : 1.0
'''

import os
import numpy


PM = [
    'PM10', 'PM25'
]
IONIC = [
    'F-', 'Cl-', 'NO3-', 'SO42-', 'Ca2+', 'Na+', 'K+', 'NH4+', 'Mg2+'
]
SNA = [
    'NO3-', 'SO42-', 'NH4+'
]
OCEC = [
    'OC', 'EC'
]
METAL = [
    'Hg','Br','As','Si','Se','Te','V','Ca','Ti','Ba','Sc','Pd','Co','Mo','K',
    'Fe','Pb','TI','Cu','Al','Cr','Cs','Ag','Zn','Sb','Sn','Mn','Cd','Ni','Ga'
]


'''
Unsupervised Learninng
    Option: {SINGLE | SNA | OCEC | IONIC}
'''
MODE = 'IONIC'
OUT_FRACTION = 0.1
RANDOM_STATE = np.random.RandomState(42)


'''
Calc qc index threshold
'''
STATS_FLOAT_UPPER = 0.97
STATS_UPPER = 0.97


'''
Machine Learning Fill Value Model
    Option: PM25 + {SO42- | NO3- | NH4+ | OC | EC ...}
'''
FILL_SRC = ['PM25']    # Expand like ['PM25', 'SO42-', ... ]
FILL_DST = ['SO42-']   # Only One Ouput


'''
Check [last - now - next]
'''
hour_range = 3


'''
Paths
'''
# 项目目录，按需修改
base_dir = r'/public/home/buzh/PmCompQC'
# 相对目录，不需要修改
paths = {
    # configs
    'configs': os.path.join(base_dir, 'configs/station_configs'),
    # data
    'stations_info': os.path.join(base_dir, 'data/obs_com_stations.txt'),
    # input for main.py
    'input_obs': os.path.join(base_dir, 'input/obs_hourly'),
    # input for fill_model_train.py
    'obs_data_raw': os.path.join(base_dir,'data/raw_data'),
    # input for {calc_qc_index.py 
    #            fill_model_train.py
    #            qc_model_train.py}
    'obs_addpm_dir': os.path.join(base_dir, 'data/qc_data_pm'),
    # output
    'output_logs':os.path.join(base_dir, 'output/qc_logs'),
    'output_data':os.path.join(base_dir, 'output/qc_data'),
    # models
    'models_qc': os.path.join(base_dir, 'models/qc_models'),
    'models_fill': os.path.join(base_dir, 'models/fill_models')
}
