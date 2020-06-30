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


def dig_obs(lines: list):
    '''
        Calc line split num.
    '''
    flag = 0
    for line in lines:
        items = line.split(',')
        if len(items) != STD_NUM:
            # print(len(items))
            # print(line)
            flag += 1
    
    return flag



def loop_dir(dirname):
    '''
        Main Dir Looping.
    '''
    assert os.path.exists(dirname)

    for _, filename in enumerate(os.listdir(dirname)):
        # print(i, filename)
        with open(os.path.join(dirname, filename), 'r') as f:
            lines = f.readlines()
            res = dig_obs(lines)
            if res != 0:
                print(filename)
            else:
                continue


def parse_err_time(filename):
    '''
        获取发生错误的站点
    '''
    assert os.path.exists(filename)

    with open(filename, 'r') as f:
        cont = f.readlines()
        t = [f.split('_')[-1].split('.')[0] for f in cont]
    
    print('\n'.join(t))


def main():
    '''
        Main
    '''
    src = r'../extract/obs_data'
    loop_dir(src)
    # err_file = r'./err_hour.txt'
    # parse_err_time(err_file)

    
if __name__ == "__main__":
    main()
