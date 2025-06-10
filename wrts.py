# Code for Wholesale & Retail Trade Sales
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import requests
import pprint

def fetch_ipi_api():
    url = "https://api.data.gov.my/data-catalogue?id=iowrt&limit=500"
    response = requests.get(url)
    response.raise_for_status()
    records = response.json()
    return records
pprint.pprint(fetch_ipi_api())

def build_df_from_api():
    raw_data = fetch_ipi_api()
    df = pd.DataFrame(raw_data)
    df = df[df['series'] == 'abs']
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['sales'] = pd.to_numeric(df['sales'], errors='coerce')
    df['sales'] = df['sales'] / 1000  # Convert sales to RM billion  
    return df[['date', 'sales']]
    

def plot_combined_chart(df):
    df = df.sort_values('date').reset_index(drop=True)
    df['YoY'] = df['sales'].pct_change(periods=12) * 100  # Calculate YoY % change

    df = df.tail(13).reset_index(drop=True)

    # Format months for x-axis labels
    month_map = {
        1: 'Jan', 2: 'Feb', 3: 'Mac', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    df['label'] = df['date'].apply(lambda x: f"{month_map[x.month]}\n{x.year}")

    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Bar chart for sales
    bars = ax1.bar(df['label'], df['sales'], color='lightblue', label='Sales')
    ax1.set_xlabel('Month-Year')
    ax1.set_ylabel('Sales (thousands)', color='black')
    ax1.tick_params(axis='y', labelcolor='black')

    # Set y-limits for bar axis
    ax1.set_ylim(140, max(df['sales']) * 1.15)
    bar_ylim = ax1.get_ylim()
    ax1.yaxis.set_major_locator(ticker.MultipleLocator(5))

    # Add value labels to bars, clipped to y-limits
    for i, bar in enumerate(bars):
        height = bar.get_height()
        label_y = height + max(df['sales']) * 0.01
        label_y = min(label_y, bar_ylim[1] - max(df['sales']) * 0.03)
        ax1.text(bar.get_x() + bar.get_width()/2, label_y, 
                 f"{height:,.1f}", ha='center', va='bottom', fontsize=8, color='black')

    # Line chart for sales YoY performance
    ax2 = ax1.twinx()
    line = ax2.plot(df['label'], df['YoY'], marker='o', color='red', label='Sales YoY (%)')
    ax2.set_ylabel('Sales YoY (%)', color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    # Set y-limits for line axis
    ax2.set_ylim(min(df['YoY'].min(), 0) * 1.15, max(df['YoY'].max(), 0) * 1.15)
    line_ylim = ax2.get_ylim()

    # Add value labels to line points, clipped to y-limits
    for i, val in enumerate(df['YoY']):
        if pd.notna(val):
            label_y = val + 0.25
            label_y = min(label_y, line_ylim[1] - 0.1)
            ax2.text(i, label_y, f"{val:.1f}%", ha='center', va='bottom', fontsize=8, color='black',
                     bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.2'))

    plt.title('Sales Value of Wholesale & Retail Trade (RM Thousand) and YoY Change')
    fig.tight_layout()
    plt.show()

# Usage:
if __name__ == "__main__":
    df = build_df_from_api()
    plot_combined_chart(df)
