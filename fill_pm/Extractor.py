# -*- encoding: utf-8 -*-
'''
@Filename    : Extractor.py
@Datetime    : 2020/04/28 16:15:34
@Author      : Joe-Bu
@Version     : 1.0

@Descrption  : 根据指定气象站点信息提取指定气象观测、污染观测数据；
               配置项在config.ini中配置，可配置气象、污染观测站点信息，指定提取时间段。
'''

import os
import sys
import traceback
import configparser
from datetime import datetime, timedelta


def getStationId(filename):
    assert os.path.exists(filename)

    with open(filename, 'r') as f:
        cont = f.readlines()
        ids = [x.split(' ')[0] for x in cont[1:]]

    return ids


def getData(config: dict):
    start = config['start']
    while start <= config['end']:
        year = start.strftime("%Y")
        if config['type'] == 'mete':
            filename = os.path.join(os.path.join(config['mete_dir'], year), 
                'obs_{}_'.format(config['type']) + start.strftime("%Y%m%d%H")+'.txt')
        elif config['type'] == 'envi':
            filename = os.path.join(os.path.join(config['envi_dir'], year), 
                'obs_{}_'.format(config['type']) + start.strftime("%Y%m%d%H")+'.txt')
        else:
            print("Error type.")
            sys.exit()

        print(filename)
        assert os.path.exists(filename)

        extr_cmd = extract_cmd(config, filename, start)
        # print(extr_cmd)
        # '''
        try:
            os.system(extr_cmd)
        except Exception as err0:
            traceback.print_exc(err0)
        # '''
        start += timedelta(hours=1)
    
    add_header = add_cmd(config)
    # print(add_header)
    try:
        os.system(add_header)
    except Exception as err1:
        traceback.print_exc(err1)


def extract_cmd(config: dict, filename: str, start) -> str:
    return "grep -E '{0}' {1} | sed 's/^/{2},/g' >> {3}.txt".format(
        '|'.join(config['ids']), 
        filename, 
        start.strftime("%Y%m%d%H"), 
        '{}/{}_{}_{}'.format(config['savedir'], 
                             config['start'].strftime("%Y%m%d%H"),
                             config['end'].strftime("%Y%m%d%H"),
                             config['type']))


def add_cmd(config: dict) -> str:
    if config['type'] == 'mete':
        return r'''sed -i "1i\时间,站点编号,2分钟平均风向,2分钟平均风速,气温,本站气压,海平面气压,露点温度,相对湿度,小时降水量,能见度,总云量" {}
            '''.format('{}/{}_{}_{}.txt'.format(config['savedir'], 
                                            config['start'].strftime("%Y%m%d%H"),
                                            config['end'].strftime("%Y%m%d%H"),
                                            config['type']))
    elif config['type'] == 'envi':
        return r'''sed -i "1i\时间,站点编号,PM2.5浓度,PM10浓度,CO浓度,NO2浓度,SO2浓度,O3浓度,O3 8小时浓度,AQI,空气质量等级,首要污染物" {}
            '''.format('{}/{}_{}_{}.txt'.format(config['savedir'], 
                                            config['start'].strftime("%Y%m%d%H"),
                                            config['end'].strftime("%Y%m%d%H"),
                                            config['type']))
    else:
        print('Error type')
        sys.exit()
        

def parseConfig(path: str) -> dict:
    cfg = configparser.ConfigParser()
    cfg.read(path)
    config = {}

    config['mete_info'] = cfg.get("StationInfo", "mete_info")
    config['envi_info'] = cfg.get("StationInfo", "envi_info")

    config['mete_dir'] = cfg.get("DataDir", "mete_dir")
    config['envi_dir'] = cfg.get("DataDir", "envi_dir")

    config['start'] = datetime.strptime(
        cfg.get("Duration", "starttime"), "%Y%m%d%H")
    config['end'] = datetime.strptime(
        cfg.get("Duration", "endtime"), "%Y%m%d%H")

    config['savedir'] = cfg.get("SaveDir", "savedir")
    config['type'] = cfg.get("Type", "type")

    return config


def main():
    workdir = os.path.dirname(__file__)
    cfgpath = os.path.join(workdir, 'config.ini')

    configs = parseConfig(cfgpath)
    if configs['type'] == 'mete':
        configs['ids'] = getStationId(configs['mete_info'])
    elif configs['type'] == 'envi':
        configs['ids'] = getStationId(configs['envi_info'])

    # for _id in configs['ids']:
    #     configs['id'] = _id
    getData(configs)


if __name__ == "__main__":
    main()