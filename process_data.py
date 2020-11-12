# -*- coding: utf-8 -*-
# @Author  : Hiram
# @Date    : 2020/11/10
# @File    : process_data.py
# @Project : negative_priming
import pandas as pd
import sqlite3


def process_data(df):
    db = sqlite3.connect('data.sqlite')
    df.to_sql('results', db, if_exists='replace', index=False)
    query_str = "select resp_result," \
                "count(*) as cnt,max(resp_time) as max_resp_time,min(resp_time) as min_resp_time," \
                "avg(resp_time) as avg_resp_time FROM results " \
                "group by resp_result order by 1"
    rs = pd.read_sql_query(query_str, db)
    print(rs)
    return rs
