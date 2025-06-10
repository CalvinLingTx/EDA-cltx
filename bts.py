# Code for Malaysia's Business Confidence
import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

BASE_URL = "https://storage.dosm.gov.my/bts/"
FILE_TEMPLATE = "bts_{year}-q{quarter}.xlsx"

def generate_possible_urls(years, quarters):
    """Generate possible file URLs in descending order of recency."""
    urls = []
    for year in years:
        for quarter in quarters:
            filename = FILE_TEMPLATE.format(year=year, quarter=quarter)
            urls.append((BASE_URL + filename, year, quarter))
    return urls

def find_latest_available_url():
    """Check which of the generated URLs is available."""
    current_year = 2025
    years = list(range(current_year, current_year - 3, -1))  # 2025, 2024, 2023
    quarters = [2, 1, 4, 3]  # In descending priority

    for url, year, quarter in generate_possible_urls(years, quarters):
        print(f"Checking for latest file: {url}")
        if requests.head(url).status_code == 200:
            print(f"Found latest available file: {url}")
            return url, (year, quarter)
    print("❌ No available BTS Excel file found.")
    return None, None

def download_excel_file(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        raise Exception(f"Failed to download file from {url}")

def extract_all_sectors_confidence_index(excel_bytes_io):
    df = pd.read_excel(excel_bytes_io, sheet_name="Table 1.4", header=None)

    # Find the row with 'Semua sektor'
    match = df[df.iloc[:, 0].astype(str).str.contains("Semua sektor", case=False, na=False)]
    if match.empty:
        raise ValueError("'Semua sektor' row not found in Table 1.4.")
    
    row_index = match.index[0]
    row = df.iloc[row_index]

    # Extract numeric values from the row
    numeric_values = row.apply(pd.to_numeric, errors='coerce').dropna().tolist()
    return numeric_values

def plot_confidence_index(values, start_year, start_quarter):
    quarters = []
    year = start_year
    quarter = start_quarter

    for _ in range(len(values)):
        quarters.append(f"{year} Q{quarter}")
        quarter += 1
        if quarter > 4:
            quarter = 1
            year += 1

    plt.figure(figsize=(10, 6))
    plt.plot(quarters, values, marker='o', linestyle='-', color='blue')

    # Determine spacing offset for labels
    y_min = min(values)
    y_max = max(values)
    offset = (y_max - y_min) * 0.03  # 3% of the value range

    # Add value labels above each point
    for x, y in zip(quarters, values):
        plt.text(x, y + offset, f"{y:.1f}", ha='center', va='bottom', fontsize=9)

    plt.title("Quarterly Confidence Indicator, Malaysia", pad=20)
    plt.xlabel("Quarter")
    plt.ylabel("Confidence Interval (%)")

    # Put only the y-axis grid
    plt.grid(axis='y')
    plt.grid(axis='y', linestyle='--', linewidth=0.5)  # regular horizontal gridlines
    plt.axhline(y=0, color='black', linewidth=1.5)     # thicker line at y=0


    # Clean up the borders
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.show()


def calculate_start_period(latest_year, latest_quarter, num_values):
    # Calculate how many quarters back required to plot the graph
    total_quarters = (latest_year * 4 + latest_quarter) - (num_values - 1)
    start_year = (total_quarters - 1) // 4
    start_quarter = total_quarters - (start_year * 4)
    return start_year, start_quarter

def main():
    url, latest_period = find_latest_available_url()
    if not url or not latest_period:
        return

    latest_year, latest_quarter = latest_period

    try:
        excel_data = download_excel_file(url)
        values = extract_all_sectors_confidence_index(excel_data)
        print(f"Extracted values: {values}")

        start_year, start_quarter = calculate_start_period(latest_year, latest_quarter, len(values))
        plot_confidence_index(values, start_year, start_quarter)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
