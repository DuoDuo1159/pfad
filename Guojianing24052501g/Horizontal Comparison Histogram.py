import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from bs4 import BeautifulSoup
from io import StringIO  # For handling HTML as strings


# Function to scrape data from a given URL
def scrape_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {url}")
        return None
    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all("table")  # Get all tables
    data_frames = []
    for table in tables[:20]:  # Just take the first 20 tables
        html_str = str(table)  # Convert the table to string format
        df = pd.read_html(StringIO(html_str), flavor='bs4')[0]  # Read table into DataFrame
        data_frames.append(df)
    return pd.concat(data_frames, ignore_index=True)  # Combine and reset index


# 1. Scrape the first dataset
url1 = "https://www.hko.gov.hk/tide/eTPKtext2024.html"  # Example webpage link
full_data1 = scrape_data(url1)

# 2. Process the first dataset
if full_data1 is not None:
    selected_data1 = full_data1.iloc[:29, :4]  # Choose the first 29 rows and first 4 columns
    selected_data1.columns = ["Month", 'Date', 'Time', 'Height(m)']
    selected_data1['Time'] = selected_data1['Time'].astype(str)
    selected_data1['YMD'] = selected_data1.apply(lambda row: f"{2024}-{row['Month']:02d}-{row['Date']:02d}", axis=1)
    selected_data1['SJ'] = selected_data1.apply(lambda row: f"{row['Time'].zfill(4)[:2]}:{row['Time'].zfill(4)[2:]}:00",
                                                axis=1)
    selected_data1['YMDSJ'] = pd.to_datetime(selected_data1['YMD'] + ' ' + selected_data1['SJ'],
                                             format='%Y-%m-%d %H:%M:%S', errors='coerce')

# 3. Scrape the second dataset (same URL for demonstration, modify for different data)
url2 = "https://www.hko.gov.hk/tide/eTPKtext2024.html"  # Modify this if you want a different dataset
full_data2 = scrape_data(url2)

# 4. Process the second dataset
if full_data2 is not None:
    selected_data2 = full_data2.iloc[29:58, :4]  # Choose the next 29 rows for comparison
    selected_data2.columns = ["Month", 'Date', 'Time', 'Height(m)']
    selected_data2['Time'] = selected_data2['Time'].astype(str)
    selected_data2['YMD'] = selected_data2.apply(lambda row: f"{2024}-{row['Month']:02d}-{row['Date']:02d}", axis=1)
    selected_data2['SJ'] = selected_data2.apply(lambda row: f"{row['Time'].zfill(4)[:2]}:{row['Time'].zfill(4)[2:]}:00",
                                                axis=1)
    selected_data2['YMDSJ'] = pd.to_datetime(selected_data2['YMD'] + ' ' + selected_data2['SJ'],
                                             format='%Y-%m-%d %H:%M:%S', errors='coerce')

# Check if both datasets are not empty
if selected_data1.empty or selected_data2.empty:
    print("One or both datasets are empty or invalid.")
else:
    try:
        # Print converted DateTime column for verification
        print("Converted DateTime Column for Dataset 1:", selected_data1['YMDSJ'])
        print("Converted DateTime Column for Dataset 2:", selected_data2['YMDSJ'])

        # 5. Create a comparative horizontal bar plot with Matplotlib
        width = 0.4  # Width of the bars
        indices = np.arange(len(selected_data1))  # Y location for each bar

        plt.figure(figsize=(12, 8))  # Increase figure size

        # Plot tidal data for the first dataset (left)
        bars1 = plt.barh(indices, selected_data1["Height(m)"], width, label='Database 1', color='#75C8AE', alpha=0.6)

        # Plot tidal data for the second dataset (right)
        bars2 = plt.barh(indices, [-x for x in selected_data2["Height(m)"]], width, label='Database 2', color='#87CEEB')

        # Add values next to each bar for the first dataset
        for bar in bars1:
            plt.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f'{bar.get_width():.2f}',
                     va='center', fontsize=8)

            # Add values next to each bar for the second dataset
        for bar in bars2:
            plt.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f'{bar.get_width():.2f}',
                     va='center', fontsize=8)

            # Add title and axis labels
        plt.title('Comparative Tide Height Data', fontweight='bold', fontsize=18)
        plt.xlabel('Tide Height (m)', fontsize=10)
        plt.ylabel('Date and Time', fontsize=12)

        # Set the y-ticks to show both datasets accurately
        plt.yticks(indices + width / 2, selected_data1['YMDSJ'].dt.strftime('%Y-%m-%d %H:%M'))

        # Add a legend
        plt.legend()
        plt.tight_layout()  # Adjust layout to fit labels
        plt.show()

    except Exception as e:
        print("Error while processing data:", str(e))
