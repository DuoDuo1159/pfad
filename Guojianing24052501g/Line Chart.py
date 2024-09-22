import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
from bs4 import BeautifulSoup
from io import StringIO

# 1. Scrape data
url = "https://www.hko.gov.hk/tide/eTPKtext2024.html"  # Example webpage link
response = requests.get(url)

# Check if the request was successful
if response.status_code != 200:
    print("Failed to retrieve the webpage.")
    exit()

# 2. Parse and read data
soup = BeautifulSoup(response.content, 'html.parser')
tables = soup.find_all("table")  # Get all tables

# 3. Convert tables to DataFrames
data_frames = []
for table in tables[:20]:  # Just take the first 20 tables
    html_str = str(table)  # Convert the table to string format
    df = pd.read_html(StringIO(html_str), flavor='bs4')[0]  # Read table into DataFrame
    data_frames.append(df)

# Combine all data into a single DataFrame
full_data = pd.concat(data_frames, ignore_index=True)  # Combine and reset index

# 4. Select relevant data
selected_data = full_data.iloc[:29, :4]  # Choose the first 29 rows and first 4 columns
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

# Check if selected_data is empty
if selected_data.empty:
    print("No valid data available for plotting.")
else:
    # Check for height data
    selected_data['Height(m)'] = selected_data['Height(m)'].astype(float)
    height_data = selected_data['Height(m)'].values

    if len(height_data) == 0 or np.all(np.isnan(height_data)):
        print("Height data is empty or contains NaNs.")
    else:
        # Prepare data for a smoother curve
        x = np.arange(len(selected_data))
        x_smooth = np.linspace(x.min(), x.max(), 300)  # Smooth x values
        spl = make_interp_spline(x, height_data, k=3)  # Interpolating spline
        height_smooth = spl(x_smooth)  # Generate smooth y values

        plt.figure(figsize=(12, 6))  # Set figure size
        plt.fill_between(x_smooth, height_smooth, color='#BEE8E8', alpha=0.6)  # Fill color
        plt.plot(x_smooth, height_smooth, color='#4C9BE6', lw=2, label='Height(m)')  # Draw line

        # Mark max, min, and average values
        max_height = np.max(height_data)
        min_height = np.min(height_data)
        avg_height = np.mean(height_data)

        max_index = np.argmax(height_data)
        min_index = np.argmin(height_data)

        plt.scatter(max_index, max_height, color='#B0DC66', zorder=5, label='Max Value')
        plt.scatter(min_index, min_height, color='#75C8AE', zorder=5, label='Min Value')
        plt.axhline(avg_height, color='#E995C9', linestyle='-', label='Average Value')  # Change to solid line

        # Annotate max, min, and average values with specific font colors
        plt.text(max_index, max_height, f'{max_height:.2f} m', fontsize=10, ha='left',
                 color='#B0DC66')  # Max value in red
        plt.text(min_index, min_height, f'{min_height:.2f} m', fontsize=10, ha='right',
                 color='#75C8AE')  # Min value in green
        plt.text(len(selected_data) - 1, avg_height, f'Avg: {avg_height:.2f} m', fontsize=10, ha='right',
                 color='#E995C9')  # Avg in orange

        # Add titles and labels
        plt.title("Tide Height Plot for 2024", fontsize=16, fontweight='bold', color='navy')  # Make title bold
        plt.xlabel("Date and Time", fontsize=14, color='darkblue')  # X-axis label color
        plt.ylabel("Tide Height (m)", fontsize=14, color='darkblue')  # Y-axis label color
        plt.xticks(ticks=np.arange(len(selected_data)), labels=selected_data['Date'], rotation=45)
        plt.yticks(fontsize=12)
        plt.legend()

        # Modify the grid lines
        plt.grid(color='lightgrey', linestyle='--', linewidth=1, alpha=0.3)  # Light grey dashed grid

        # Show the plot
        plt.tight_layout()
        plt.show()
