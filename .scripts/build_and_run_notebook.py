#!/usr/bin/env python3
"""
生成并执行高质量满分作业 Notebook
文件：17420249605674_沈美梓_作业一.ipynb
"""

import os
import sys
import json
import base64
import io
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import missingno as msno

try:
    from data_profiling import ProfileReport
except ImportError:
    from ydata_profiling import ProfileReport

work_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(work_dir)

# 1. 字体与主题配置
mpl.rcParams['font.sans-serif'] = [
    'Arial Unicode MS', 'PingFang SC', 'Hiragino Sans GB', 
    'SimHei', 'Microsoft YaHei', 'sans-serif'
]
mpl.rcParams['axes.unicode_minus'] = False
sns.set_theme(style='whitegrid', font='Arial Unicode MS')
plt.rcParams['figure.dpi'] = 110

print("开始执行数据处理与分析...")

# 读取数据
df = pd.read_csv('Used Cars.csv', encoding='gbk')
df_raw = df.copy()

# 缺失值填充
df['引擎'] = df['引擎'].fillna(df.groupby('车名')['引擎'].transform('median'))
df['引擎'] = df['引擎'].fillna(df.groupby('车体类型')['引擎'].transform('median'))
df['引擎'] = df['引擎'].fillna(df['引擎'].median())

def get_mode(s):
    m = s.mode()
    return m.iloc[0] if len(m) > 0 else np.nan

doors_mode_name = df.groupby('车名')['车门数量'].transform(get_mode)
doors_mode_body = df.groupby('车体类型')['车门数量'].transform(get_mode)
df['车门数量'] = df['车门数量'].fillna(doors_mode_name).fillna(doors_mode_body).fillna(df['车门数量'].mode().iloc[0])

seats_mode_name = df.groupby('车名')['座位数量'].transform(get_mode)
seats_mode_body = df.groupby('车体类型')['座位数量'].transform(get_mode)
df['座位数量'] = df['座位数量'].fillna(seats_mode_name).fillna(seats_mode_body).fillna(df['座位数量'].mode().iloc[0])

df['车门数量'] = df['车门数量'].astype(int)
df['座位数量'] = df['座位数量'].astype(int)

# 特征工程
df['车龄'] = 2025 - df['注册年份']
df['品牌'] = df['车名'].apply(lambda x: str(x).split()[0] if pd.notnull(x) else 'Unknown')
df['年均里程'] = (df['里程'] / df['车龄']).round(1)
df['对数价格'] = np.log(df['价格'])
df['车龄分段'] = pd.cut(
    df['车龄'], 
    bins=[0, 3, 7, 12, 100], 
    labels=['准新车(≤3年)', '次新车(4-7年)', '成熟车(8-12年)', '老旧车(>12年)']
)

print("数据准备完成，共计:", df.shape)

# 生成自动化数据诊断报告 HTML
report_filename = "17420249605674_沈美梓_数据诊断报告.html"
if not os.path.exists(report_filename):
    print(f"正在生成 {report_filename} ...")
    profile = ProfileReport(
        df,
        title='厦门大学数据可视化 - 二手车数据集(Used Cars)自动化诊断报告',
        explorative=True
    )
    profile.to_file(report_filename)
    print("诊断报告生成完成！")
else:
    print(f"诊断报告 {report_filename} 已存在。")

print("全部预处理与报告生成成功！")
