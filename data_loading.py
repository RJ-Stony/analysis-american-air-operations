# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 09:16:03 2025
"""

import pandas as pd

dfs = []

for i in range(87, 100):
    df = pd.read_csv(f'./data/dataverse_files_1987-1999/19{i}.csv')
    dfs.append(df)

len(dfs)

total_df = pd.concat(dfs, ignore_index=True)
total_df.head()

total_df.columns

dfs2 = []

for i in range(0, 9):
    df = pd.read_csv(f'./data/dataverse_files_2000-2008/200{i}.csv', encoding='latin-1', low_memory=False)
    dfs2.append(df)

len(dfs2)

total_df = pd.concat(dfs2, ignore_index=True)
total_df.head()

total_df.columns



