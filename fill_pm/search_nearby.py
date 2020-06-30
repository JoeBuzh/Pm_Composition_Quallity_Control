# -*- encoding: utf-8 -*-
'''
@Filename    : search_nearby.py
@Datetime    : 2020/06/05 16:58:50
@Author      : Joe-Bu
@version     : 1.0
'''

import os
import sys
import xlrd

import folium
import numpy as np
import pandas as pd
from rtree import index

CN_center = [34.75, 113.62]


def position_visual(comp_info, envi_info):
    '''
        观测站点分布简单可视化.
    '''
    map_station = folium.Map(CN_center, zoom_start=5)
    # Add comp stations
    for _, row in comp_info.iterrows():
        lat, lon = row['latitude'], row['longitude']
        text = folium.Html(
            u'<b>编号:{}</b></br> <b>名称:{}</b></br> <b>城市:{}</b></br></br>'.format(
                row['stationcode'], row['name'], row['cityname']),
            script=True)
        popup = folium.Popup(text, max_width=2650)
        icon = folium.Icon(color='red', icon='info-sign')
        folium.Marker([lat, lon], popup=popup, icon=icon).add_to(map_station)
    # Add envi stations
    for _, row in envi_info.iterrows():
        lat, lon = row['纬度'], row['经度']
        text = folium.Html(
            u'<b>编号:{}</b></br> <b>名称:{}</b></br> <b>城市:{}</b></br></br>'.format(
                row['站号'], row['站点'], row['城市']),
            script=True)
        popup = folium.Popup(text, max_width=2650)
        icon = folium.Icon(color='green', icon='info-sign')
        folium.Marker([lat, lon], popup=popup, icon=icon).add_to(map_station)
    # save html
    map_station.save(u"{}.html".format('demo'))


def read_txt(filename: str, sep:str=None):
    '''
        文件读取
    '''
    assert os.path.exists(filename)
    df = pd.read_table(filename, sep=sep, encoding='utf-8', engine='python')

    return df


def search(comp_info, idx) -> dict:
    '''
        匹配最近站点, 返回映射关系。
    '''
    _map = {}
    for i, row in comp_info.iterrows():
        lon = row['longitude']
        lat = row['latitude']
        comp_code = row['stationcode']
        nearby = list(idx.nearest((lon, lat, lon, lat), 1, objects=True))[0]
        # print(len(list(idx.nearest((lon, lat, lon, lat), 1, objects=True))))
        _map[comp_code] = nearby.object


    return _map


def get_nearby(nearby: list, envi_info) -> pd.DataFrame:
    assert len(nearby) > 0

    print(len(nearby))
    print(len(set(nearby)))
    nearby_list = [int(x) for x in nearby]
    nearby_df = envi_info.loc[envi_info['站号'].isin(nearby_list)]
    print(nearby_df.head())

    return nearby_df


def insert_idx(envi_info, idx):
    for i, row in envi_info.iterrows():
        lon = row['经度']
        lat = row['纬度']
        obj = row['站号']
        idx.insert(i, (lon, lat, lon, lat), obj=obj)

    return idx


def main():
    idx = index.Index()
    comp_info = read_txt('../data/obs_com_stations.txt', sep=',')
    envi_info = pd.read_csv('../data/obs_env_stations.txt', delim_whitespace=True)
    idx = insert_idx(envi_info, idx)
    mapping = search(comp_info, idx)
    print(mapping)
    # get nearby file
    nearby = get_nearby(mapping.values(), envi_info)
    nearby.to_csv(
        'nearby.txt', header=True, index=False, sep=' ', encoding='utf-8')
    # demonstrate rtree
    # position_visual(comp_info, envi_info)


if __name__ == "__main__":
    main()
