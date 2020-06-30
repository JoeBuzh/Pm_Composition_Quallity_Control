# -*- encoding: utf-8 -*-
'''
@Filename    : write2file.py
@Datetime    : 2020/06/01 14:05:15
@Author      : Joe-Bu
@version     : 1.0
'''

from __future__ import print_function

import os
import sys
sys.path.append('../')
sys.path.append('../..')
import xlrd
import configparser

import pandas as pd


def write2ini(filename, cfp):
    '''
        Write thresholds into *.ini file.
    '''
    # assert os.path.exists(filename)

    with open(filename, 'w') as configfile:
        cfp.write(configfile)