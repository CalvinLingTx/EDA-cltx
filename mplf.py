# Code for Labour Force Survey
import pandas as pd
import matplotlib.pyplot as plt
import requests
import pprint

def fetch_ipi_api():
    url = "https://api.data.gov.my/data-catalogue?id=lfs_month&limit=500"
    response = requests.get(url)
    response.raise_for_status()
    records = response.json()
    return records
pprint.pprint(fetch_ipi_api())

def build_df_from_api():
    raw_data = fetch_ipi_api()
    df = pd.DataFrame(raw_data)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['lf_unemployed'] = pd.to_numeric(df['lf_unemployed'], errors='coerce')  
    df['u_rate'] = pd.to_numeric(df['u_rate'], errors='coerce')
    df = df.sort_values('date').dropna(subset=['date', 'u_rate']).reset_index(drop=True)
    return df[['date', 'lf_unemployed', 'u_rate']]

def plot_combined_chart(df):
    df = df.tail(13).reset_index(drop=True)

    # Format months for x-axis labels
    month_map = {
        1: 'Jan', 2: 'Feb', 3: 'Mac', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    df['label'] = df['date'].apply(lambda x: f"{month_map[x.month]}\n{x.year}")

    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Bar chart for lf_unemployed
    bars = ax1.bar(df['label'], df['lf_unemployed'], color='lightblue', label='Unemployed')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Unemployed (thousands)', color='black')
    ax1.tick_params(axis='y', labelcolor='black')

    # Set y-limits for bar axis
    ax1.set_ylim(0, max(df['lf_unemployed']) * 1.15)
    bar_ylim = ax1.get_ylim()

    # Add value labels to bars, clipped to y-limits
    for i, bar in enumerate(bars):
        height = bar.get_height()
        label_y = height + max(df['lf_unemployed']) * 0.01
        # Clip label_y to not exceed top of y-axis
        label_y = min(label_y, bar_ylim[1] - max(df['lf_unemployed']) * 0.03)
        ax1.text(bar.get_x() + bar.get_width()/2, label_y, 
                 f"{height:,.0f}", ha='center', va='bottom', fontsize=8, color='black')

    # Line chart for u_rate
    ax2 = ax1.twinx()
    line = ax2.plot(df['label'], df['u_rate'], marker='o', color='red', label='Unemployment Rate')
    ax2.set_ylabel('Unemployment Rate (%)', color='black')
    ax2.tick_params(axis='y', labelcolor='black')

    # Set y-limits for line axis
    ax2.set_ylim(min(df['u_rate']) * 0.95, max(df['u_rate']) * 1.10)
    line_ylim = ax2.get_ylim()

    # Add value labels to line points, clipped to y-limits
    for i, val in enumerate(df['u_rate']):
        label_y = val + 0.05
        # Clip label_y to not exceed top of y-axis
        label_y = min(label_y, line_ylim[1] - 0.1)
        ax2.text(i, label_y, f"{val:.1f}", ha='center', va='bottom', fontsize=8, color='black',
                 bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.2'))

    plt.title('Unemployed and Unemployment Rate')
    fig.tight_layout()
    plt.show()

# Usage:
if __name__ == "__main__":
    df = build_df_from_api()
    plot_combined_chart(df)
