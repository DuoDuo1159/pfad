import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup

# 获取数据
url = "https://www.hko.gov.hk/tide/eTPKtext2024.html"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# 找到表格
table = soup.find('table')
rows = table.find_all('tr')

# 提取数据
data = []
for row in rows[1:30]:  # 只取第1行到第29行
    cols = row.find_all('td')
    if len(cols) >= 8:  # 确保有至少8列
        row_data = [col.text.strip() for col in cols[:7]]  # 只取前7列
        data.append(row_data)

# 创建 DataFrame
columns = ['Data and Time', 'Height1', 'Height2', 'Height3', 'Height4', 'Height5', 'Height6']
df = pd.DataFrame(data, columns=columns)

# 数据预处理
df['Data and Time'] = pd.to_datetime(df['Data and Time'], errors='coerce')
df.iloc[:, 1:] = df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')

# 归一化处理
normalized_data = df.iloc[:, 1:].div(df.iloc[:, 1:].sum(axis=1), axis=0)

# 定义颜色(将无效的十六进制代码替换为有效代码)
colors = ['#B0DC66', '#E995C9', '#87CEEB', '#BEE8E8', '#FC9871', '#75C8AE']  # 更换了第一个颜色代码

# 确保颜色数量与列数一致
if len(colors) < normalized_data.shape[1]:
    raise ValueError("指定的颜色数量少于需要的列数。")

# 绘制堆叠图
plt.figure(figsize=(10, 6))
normalized_data.plot(kind='barh', stacked=True, figsize=(10, 6), color=colors, alpha=0.6, width=0.8)

# 设置坐标轴和标题
plt.xlabel('Normalized Height')
plt.ylabel('Data and Time')
plt.title('Normalized Stacked Bar Chart of Heights')
plt.yticks(range(len(df)), df['Data and Time'].dt.strftime('%Y-%m-%d %H:%M:%S'), rotation=0)
plt.legend(title='Heights')
plt.tight_layout()
plt.show()