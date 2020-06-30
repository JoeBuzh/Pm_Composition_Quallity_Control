# -*- encoding: utf-8 -*-
'''
@Filename    : cfg.py
@Datetime    : 2020/06/20 13:18:10
@Author      : Joe-Bu
@version     : 1.0
'''

import os 
from datetime import datetime

# time domain
duration = {
    'start': datetime(2019, 11, 1, 0, 0),
    'end': datetime(2019, 12, 31, 23, 0)
}

# path
base_dir = r'/public/home/buzh/PmQc'
paths = {
    'obs_dir': os.path.join(base_dir, r'post_analysis/2019_obs'),
    'qc_dir': os.path.join(base_dir, r'post_analysis/2019_qc'),
    'fill_dir': os.path.join(base_dir, r'post_analysis/2019_fill'),
    'save_dir': os.path.join(base_dir, r'visualization/images')
}

'''
stationns
    MODE: All or Specific station list.
'''
mapping = os.path.join(base_dir, r'fill_pm/nearby.json')
# mapping = [110000012, 120000003, 120000004, 120000005, 12000006]

PM = ['PM10', 'PM25']
IONIC = ['F-', 'Cl-', 'NO3-', 'SO42-', 'Ca2+', 'Na+', 'K+', 'NH4+', 'Mg2+']
SNA = ['NO3-', 'SO42-', 'NH4+']
OCEC = ['OC', 'EC']
METAL = [
    'Hg','Br','As','Si','Se','Te','V','Ca','Ti','Ba','Sc','Pd','Co','Mo','K',
    'Fe','Pb','TI','Cu','Al','Cr','Cs','Ag','Zn','Sb','Sn','Mn','Cd','Ni','Ga'
]
