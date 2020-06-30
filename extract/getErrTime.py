# -*- encoding: utf-8 -*-
'''
@Filename    : check_hourly_format.py
@Datetime    : 2020/06/17 14:43:00
@Author      : Joe-Bu
@version     : 1.0
'''

import os
import sys

STD_NUM=46


def parse_err_time(filename):
    '''
        获取发生错误的站点
    '''
    assert os.path.exists(filename)

    with open(filename, 'r') as f:
        cont = f.readlines()
        err_time = [f.split('_')[-1].split('.')[0] for f in cont]
    # print('\n'.join(err_time))

    return err_time


def main():
    '''
        Main
    '''
    err_file = r'./err_hour.txt'
    parse_err_time(err_file)

    
if __name__ == "__main__":
    main()