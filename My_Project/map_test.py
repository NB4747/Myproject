#!/usr/bin/python
# -*- coding:utf-8 -*-
#pip install pyecharts
from pyecharts import options as opts
from pyecharts.charts import Map
import pandas as pd

# value = [95.1, 23.2, 43.3, 66.4, 88.5]
# attr = ["China", "Canada", "Brazil", "Russia", "United States"]
#
# map0 = Map()
# map0.add(
#     series_name="世界地图",
#     data_pair=list(zip(attr, value)),
#     maptype="world"
# )
# map0.set_global_opts(
#     title_opts=opts.TitleOpts(title="世界地图示例"),
#     visualmap_opts=opts.VisualMapOpts()
# )
# map0.render(path="世界地图.html")
# from pyecharts import Map

province_distribution = {'河南省': 45.23, '北京': 37.56, '河北': 21, '辽宁': 12, '江西': 6, '上海': 20, '安徽': 10,
                         '江苏': 16, '湖南': 9, '浙江': 13, '海南': 2, '广东': 22, '湖北': 8, '黑龙江': 11, '澳门': 1,
                         '陕西': 11, '四川': 7, '内蒙古': 3, '重庆': 3, '云南': 6, '贵州': 2, '吉林': 3, '山西': 12,
                         '山东': 11, '福建': 4, '青海': 1, '天津': 1, '其他': 1}
provice = list(province_distribution.keys())
values = list(province_distribution.values())

map = Map()
map.add(
    series_name="",
    data_pair=list(zip(provice, values)),
    maptype='china'
)
map.set_global_opts(
    title_opts=opts.TitleOpts(title="中国地图"),
    visualmap_opts=opts.VisualMapOpts(min_=0, max_=50)
)
map.render(path="中国地图.html")