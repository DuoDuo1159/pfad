import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
from bs4 import BeautifulSoup

# 1. 爬取数据
url = "https://www.hko.gov.hk/tide/eTPKtext2024.html"  # 示例网页链接
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# 2. 分析和读取数据
tables = soup.find_all("table")  # 获取所有表格

# 3. 使数据矩阵化
data_frames = []
for table in tables[:20]:  # 只取前20个表
    df = pd.read_html(str(table))[0]
    data_frames.append(df)

# 合并所有数据
full_data = pd.concat(data_frames)

# 4. 选择数据部分
selected_data = full_data.iloc[:29, :3]  # 选择前29行和前3列

# 将数据列的名称翻译为英文（假设存在中文标题）
selected_data.columns = ['Date', 'Time', 'Height(m)']

# 确保日期和时间列为字符串类型
selected_data['Date'] = selected_data['Date'].astype(str)
selected_data['Time'] = selected_data['Time'].astype(str)

# 5. 计算每天的潮汐平均值
selected_data['DateTime'] = pd.to_datetime(selected_data['Date'] + ' ' + selected_data['Time'], errors='coerce')
daily_means = selected_data.groupby(selected_data['DateTime'].dt.date)['Height(m)'].mean().reset_index()
daily_means.columns = ['Date', 'AvgHeight']

# 6. 用matplotlib做平滑曲线图并美化
plt.figure(figsize=(16, 6))  # 增加图形宽度

# 绘制潮汐数据
x = np.arange(len(selected_data))
y = selected_data['Height(m)'].astype(float).values

# 使用B样条曲线平滑数据
x_smooth = np.linspace(x.min(), x.max(), 300)
spl = make_interp_spline(x, y, k=2)  # k=2 表示二次B样条
y_smooth = spl(x_smooth)

# 绘制平滑曲线
plt.plot(x_smooth, y_smooth, label='Tidal Height', color='#4C9BE6')  # 使用新的蓝色

# 填充曲线下方的渐变颜色
plt.fill_between(x_smooth, y_smooth, color='#B0DC66', alpha=0.4)  # 使用新颜色填充

# 绘制每天的潮汐平均值
avg_x = pd.to_datetime(daily_means['Date']).map(pd.Timestamp.toordinal).values
plt.scatter(avg_x, daily_means['AvgHeight'], color='#FC9871', label='Daily Avg Height', zorder=5)  # 新的橙色

# 标出最大值和最小值
max_height = y_smooth.max()
min_height = y_smooth.min()
max_index = np.argmax(y_smooth)
min_index = np.argmin(y_smooth)

plt.scatter(x_smooth[max_index], max_height, color='#E995C9', label='Max Height', zorder=6)  # 新的粉色
plt.scatter(x_smooth[min_index], min_height, color='#BEE8E8', label='Min Height', zorder=6)  # 新的绿色

# 添加文本标注
plt.text(x_smooth[max_index], max_height, f'Max: {max_height:.2f}', fontsize=9, ha='right', color='#E995C9')
plt.text(x_smooth[min_index], min_height, f'Min: {min_height:.2f}', fontsize=9, ha='right', color='#BEE8E8')

# 图表美化
plt.title('Tidal Data Analysis at Tai Po Kau (2024)', fontsize=22, fontweight='bold')
plt.xlabel('Date and Time', fontsize=9)
plt.ylabel('Height (m)', fontsize=9)

# 设置横坐标的刻度、标签、旋转角度和字体大小
plt.xticks(ticks=x[::2], labels=selected_data['Date'][::2] + ' ' + selected_data['Time'][::2], rotation=45, ha='right', fontsize=10)  # 每隔一个显示一个标签
plt.yticks(fontsize=12)
plt.legend(title='Tidal Heights', fontsize=9)

# 增加网格线的宽度
plt.grid(True, linestyle='--', alpha=0.6, linewidth=1.5)  # 设置宽度为1.5
plt.tight_layout()

# 显示图表
plt.show()