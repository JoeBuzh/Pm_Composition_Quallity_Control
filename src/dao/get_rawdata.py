# -*- encoding: utf-8 -*-
'''
@Filename    : get__raw_obs.py
@Datetime    : 2020/06/01 11:00:45
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


def read_raw_txt(filename: str, header=None)->tuple:
    '''
        Read obs_com_yyyymmddhh.txt.
        Params
            filename: abspath or relative path
            header: None
        Return
            tuple(boolean, df/None)
    '''
    # print(filename)
    assert os.path.exists(filename)

    df = pd.read_csv(
        filename, sep=',', names=header, encoding='utf-8')

    if len(df) > 0:
        return True, df
    else:
        return False, None


def read_ini(ini_file: str):
    '''
        Function
            Read *.ini file 
        Params
            .ini file path
        Return
            cfp object
    '''
    # print(ini_file)
    assert os.path.exists(ini_file)

    cfp = configparser.ConfigParser()
    cfp.read(ini_file)

    return cfp