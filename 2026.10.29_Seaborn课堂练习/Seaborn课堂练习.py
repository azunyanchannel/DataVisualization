"""
课堂作业：Seaborn 数据可视化课堂练习（课件 p.60-63）
学生姓名：沈美梓
学号：17420249605674
课程：数据可视化
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

# ==============================================================================
# 一、环境配置与主题风格
# ==============================================================================

# 1. 采用课件中的 Seaborn 默认主题风格（灰底白网格，与课件幻灯片视觉一致）
sns.set_theme(style='darkgrid')

# 2. 跨平台中文字体配置（兼容 Mac / Windows / Linux）并正常显示负号
mpl.rcParams['font.sans-serif'] = [
    'Arial Unicode MS', 'Hiragino Sans GB', 'PingFang SC', 
    'Songti SC', 'SimHei', 'Microsoft YaHei', 'sans-serif'
]
mpl.rcParams['axes.unicode_minus'] = False


# ==============================================================================
# 二、数据读取与预处理
# ==============================================================================

# 读取订单数据集 orders.txt
df = pd.read_csv('orders.txt')

print(f"数据集总维度：{df.shape[0]} 行, {df.shape[1]} 列")
print(f"年份范围：{df['dt'].min()} ~ {df['dt'].max()}")
print(f"门店列表：{df['store_name'].unique().tolist()}")
print(f"产品品类：{df['category'].unique().tolist()}")

# 筛选 2020 年数据子集 (用于练习 2、3、4)
df_2020 = df[df['dt'] == 2020].copy()
print(f"2020年数据量：{df_2020.shape[0]} 行")


# ==============================================================================
# 三、练习 1：使用 sns.relplot 绘制各门店 2014-2020 利润折线图（课件 p.60）
# ==============================================================================
# 要求：绘制各个门店 2014-2020 期间，不同产品品类 (category) 的利润折线图

g1 = sns.relplot(
    data=df,
    x='dt',
    y='profit',
    hue='category',
    col='store_name',
    col_wrap=3,
    kind='line',
    height=2.8,
    aspect=1.1
)

# 调整总标题与坐标轴标签（与课件 p.60 原图完全对齐）
g1.fig.subplots_adjust(top=0.92)
g1.fig.suptitle('2014-2020门店各品类利润折线图', fontsize=14, y=0.98)
g1.set_axis_labels('年份', '利润')

plt.show()


# ==============================================================================
# 四、练习 2：使用 sns.displot 绘制 2020 年各门店不同品类的利润直方图和核密度曲线（课件 p.61）
# ==============================================================================
# 要求：绘制 2020 年各个门店不同产品品类的利润直方图和核密度曲线

g2 = sns.displot(
    data=df_2020,
    x='profit',
    hue='category',
    col='store_name',
    col_wrap=3,
    kde=True,
    height=2.8,
    aspect=1.1
)

# 调整总标题与坐标轴标签（对应课件 p.61 原图标题：2020年上半年利润额的频数分布图）
g2.fig.subplots_adjust(top=0.92)
g2.fig.suptitle('2020年上半年利润额的频数分布图', fontsize=14, y=0.98)
g2.set_axis_labels('利润额', '计数')

plt.show()


# ==============================================================================
# 五、练习 3：使用 sns.catplot 绘制 2020 年各门店不同品类的分类图（课件 p.62）
# ==============================================================================
# 要求：绘制 2020 年各个门店不同产品品类的利润散点图、箱型图、条形图

# 3.1 分类散点图 (kind='strip')
g3_strip = sns.catplot(
    data=df_2020,
    x='store_name',
    y='profit',
    hue='category',
    kind='strip',
    height=3.8,
    aspect=1.9
)
g3_strip.fig.subplots_adjust(top=0.90)
g3_strip.fig.suptitle('2020门店产品利润散点图', fontsize=13, y=0.96)
g3_strip.set_axis_labels('', '利润额')
plt.show()

# 3.2 分类条形图 (kind='bar')
g3_bar = sns.catplot(
    data=df_2020,
    x='store_name',
    y='profit',
    hue='category',
    kind='bar',
    height=3.8,
    aspect=1.9
)
g3_bar.fig.subplots_adjust(top=0.90)
g3_bar.fig.suptitle('2020门店产品利润条形图', fontsize=13, y=0.96)
g3_bar.set_axis_labels('', '利润额')
plt.show()

# 3.3 分类箱型图 (kind='box')
g3_box = sns.catplot(
    data=df_2020,
    x='store_name',
    y='profit',
    hue='category',
    kind='box',
    height=3.8,
    aspect=1.9
)
g3_box.fig.subplots_adjust(top=0.90)
g3_box.fig.suptitle('2020门店产品利润箱型图', fontsize=13, y=0.96)
g3_box.set_axis_labels('', '利润额')
plt.show()


# ==============================================================================
# 六、练习 4：使用 sns.lmplot 绘制 2020 年产品类别销量与利润拟合曲线（课件 p.63）
# ==============================================================================
# 要求：绘制 2020 年各个产品类别的销量和利润关系的拟合曲线 (二次多项式拟合 order=2)

g4 = sns.lmplot(
    data=df_2020,
    x='sales',
    y='profit',
    hue='category',
    order=2,
    height=4.2,
    aspect=1.7
)

# 调整总标题与坐标轴标签
g4.fig.subplots_adjust(top=0.90)
g4.fig.suptitle('2020销量和利润拟合曲线', fontsize=13, y=0.96)
g4.set_axis_labels('销量', '利润额')

plt.show()


# ==============================================================================
# 附：一次线性拟合与二次多项式拟合对比分析
# ==============================================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 4.8), sharey=True)

categories = df_2020['category'].unique()

for i, (order, title_suffix) in enumerate([(1, '一次线性拟合 (order=1)'), (2, '二次多项式拟合 (order=2)')]):
    ax = axes[i]
    for cat in categories:
        subset = df_2020[df_2020['category'] == cat]
        sns.regplot(
            data=subset,
            x='sales',
            y='profit',
            order=order,
            label=cat,
            ax=ax,
            scatter_kws={'alpha': 0.6, 's': 18},
            line_kws={'linewidth': 2}
        )
    ax.set_title(f'2020年销量与利润关系 - {title_suffix}', fontsize=12)
    ax.set_xlabel('销量', fontsize=11)
    ax.set_ylabel('利润额' if i == 0 else '', fontsize=11)
    ax.legend(title='category')

plt.tight_layout()
plt.show()
