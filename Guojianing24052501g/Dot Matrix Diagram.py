import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from bs4 import BeautifulSoup
from io import StringIO  # For handling HTML as strings

# 1. Scrape data
url = "https://www.hko.gov.hk/tide/eTPKtext2024.html"
response = requests.get(url)

# Check if the request was successful
if response.status_code != 200:
    print("Failed to retrieve the webpage.")
    exit()

# 2. Parse and read data
soup = BeautifulSoup(response.content, 'html.parser')
tables = soup.find_all("table")

# 3. Convert tables to DataFrames
data_frames = []
for table in tables[:20]:  # Just take the first 20 tables
    html_str = str(table)
    df = pd.read_html(StringIO(html_str), flavor='bs4')[0]
    data_frames.append(df)

# Combine all data into a single DataFrame
full_data = pd.concat(data_frames, ignore_index=True)

# 4. Select relevant data
selected_data = full_data.iloc[:29, :4]

# Rename columns for clarity
selected_data.columns = ["Month", 'Date', 'Time', 'Height(m)']

# Ensure Date and Time columns are strings
selected_data['Time'] = selected_data['Time'].astype(str)
selected_data['YMD'] = selected_data.apply(lambda row: f"{2024}-{row['Month']:02d}-{row['Date']:02d}", axis=1)
selected_data['SJ'] = selected_data.apply(lambda row: f"{row['Time'].zfill(4)[:2]}:{row['Time'].zfill(4)[2:]}:00",
                                          axis=1)

# 5. Calculate datetime values
selected_data['YMDSJ'] = pd.to_datetime(selected_data['YMD'] + ' ' + selected_data['SJ'],
                                        format='%Y-%m-%d %H:%M:%S',
                                        errors='coerce')

# Check if selected_data is not empty
if selected_data.empty:
    print("No valid data available after filtering.")
else:
    try:
        print("Converted DateTime Column:", selected_data['YMDSJ'])

        # 6. Create a bubble chart with Matplotlib
        plt.figure(figsize=(16, 6))

        # Define size of the bubbles based on tidal heights
        sizes = selected_data['Height(m)'] * 500

        # Create a custom color map from #4C9BE6 to #BEE8E8
        colors = LinearSegmentedColormap.from_list("custom_blue", ["#4C9BE6", "#BEE8E8"])

        # Normalize heights to map to colors
        norm = plt.Normalize(vmin=selected_data['Height(m)'].min(), vmax=selected_data['Height(m)'].max())
        color_values = colors(norm(selected_data['Height(m)']))  # Map the heights to colors

        # Create the bubble chart
        scatter = plt.scatter(selected_data['YMDSJ'],
                              np.zeros_like(selected_data['YMDSJ']),
                              s=sizes,
                              alpha=0.7,
                              color=color_values,
                              edgecolors="w",
                              linewidth=2)

        # Add title and axis labels
        plt.title('Matrix Bubble Chart of Tide Height Data', fontweight='bold', fontsize=16)
        plt.xlabel('Date and Time', fontsize=10)
        plt.ylabel('Tide Height (m)', fontsize=10)

        # Add text labels above the bubbles
        for i in range(len(selected_data)):
            plt.text(selected_data['YMDSJ'].iloc[i], 0, f'{selected_data["Height(m)"].iloc[i]:.1f}',
                     ha='center', va='bottom', fontsize=9)

            # Adjust x-axis label font size
        plt.xticks(rotation=45, fontsize=8)

        # Show the plot
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print("Error while processing data:", str(e))
