# -*- encoding: utf-8 -*-
'''
@Filename    : cfg.py
@Datetime    : 2020/05/13 11:14:21
@Author      : Joe-Bu
@version     : 1.0
@description : 配置信息
'''

# 分月表
months = [
    '201901','201902','201903','201904','201905','201906',
    '201907','201908','201909','201910','201911','201912'
]
# 水溶性离子
lizi_cn = {
    1:"钙离子", 2:"镁离子", 3:"钾离子", 4:"铵盐", 5:"钠离子", 6:"硫酸盐", 7:"硝酸盐", 9:"氯离子", 545:"氟离子",
    }
lizi_en = {
    1:"Ca2+", 2:"Mg2+", 3:"K+", 4:"NH4+", 5:"Na+", 6:"SO42-", 7:"NO3-", 9:"Cl-", 545:"F-"
}
# OCEC    透射transmittance 光学optics 反射reflection  *** 优先级：透射>反射>光学>元素
ocec_cn = {
    15:"热光透射法OC",16:"热光透射法EC",17:"光学OC",18:"光学EC",
    555:"热光反射法OC",556:"热光反射法EC",577:"元素碳",578:"有机碳"
}
ocec_en = {
    15:"OC_trans", 16:"EC_trans", 17:"OC_optics", 18:"EC_optics", 
    555:"OC_refl",556:"EC_refl", 577:"EC_raw", 578:"OC_raw"
}
# 在线重金属
jins_cn = {
    29:"铅", 30:"硒", 31:"汞", 32:"铬", 33:"镉", 34:"锌", 35:"铜", 36:"镍", 37:"铁", 38:"锰", \
    39:"钛", 40:"锑", 41:"锡", 42:"钒", 43:"钡", 44:"砷", 45:"钙", 46:"钾", 47:"钴", 48:"钼", \
    49:"银", 50:"钪", 51:"铊", 52:"钯", 53:"溴", 54:"碲", 55:"镓", 56:"铯", 64:"硅", 256:"铝"
}
jins_en = {
    29:"Pb", 30:"Se", 31:"Hg", 32:"Cr", 33:"Cd", 34:"Zn", 35:"Cu", 36:"Ni", 37:"Fe", 38:"Mn", \
    39:"Ti", 40:"Sb", 41:"Sn", 42:"V", 43:"Ba", 44:"As", 45:"Ca", 46:"K", 47:"Co", 48:"Mo", \
    49:"Ag", 50:"Sc", 51:"TI", 52:"Pd", 53:"Br", 54:"Te", 55:"Ga", 56:"Cs", 64:"Si", 256:"Al"
}
# PM
aqi_cn = {
    23:"颗粒物(PM10)", 24:"颗粒物(PM2.5)"
}
aqi_en = {
    23:"PM10", 24:"PM25"
}

# 路径相关
paths = {
    'stationfile': r'/public/home/buzh/PmQc/post_analysis/obs_com_stations.txt',
    'extract_src': r'/public/home/buzh/PmQc/output/qc_data',
    #'extract_src': r'/public/home/buzh/PmQc/input/obs_hourly',
    'extract_dst': r'/public/home/buzh/PmQc/post_analysis/result'
}
