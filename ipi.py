# Code for Industrial Production Index
import pandas as pd
import matplotlib.pyplot as plt
import requests
import pprint

def fetch_ipi_api():
    url = "https://api.data.gov.my/data-catalogue?id=ipi&limit=150"
    response = requests.get(url)
    response.raise_for_status()
    records = response.json()
    return records
pprint.pprint(fetch_ipi_api())

def build_df_from_api():
    raw_data = fetch_ipi_api()
    df = pd.DataFrame(raw_data)

    # Correct filter: use the actual index values
    df = df[df['series'] == 'abs']

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['index'] = pd.to_numeric(df['index'], errors='coerce')
    df = df.sort_values('date').dropna(subset=['date', 'index']).reset_index(drop=True)
    return df[['date', 'index']]

def plot_ipp_combined_chart(df):
    # Calculate Year-over-Year (YoY) and Month-over-Month (MoM) changes
    df['YoY'] = df['index'].pct_change(12) * 100
    df['MoM'] = df['index'].pct_change(1) * 100

    # Focus on the latest 13 months
    df = df.tail(13).reset_index(drop=True)

    # Format months 
    month_map = {
        1: 'Jan', 2: 'Feb', 3: 'Mac', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    df['label'] = df['date'].apply(lambda x: f"{month_map[x.month]}\n{x.year}")

    # Print latest data point for reference
    print("\nLatest Data Used:")
    print(df[['date', 'index', 'MoM', 'YoY']].tail(1))
    # Set up the figure and dual axes
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    # Plot IPI index as bar chart
    ax1.bar(df.index, df['index'], color='lightgreen', label='Index', zorder=2)
    # Plot MoM line
    ax2.plot(df.index, df['MoM'], color='black', marker='o', linewidth=2, label='IPP %MoM', zorder=3)
    # Plot YoY line
    ax2.plot(df.index, df['YoY'], color='navy', marker='o', linestyle='dotted', linewidth=2, label='IPP %YoY', zorder=3)
    # Customize x-axis
    ax1.set_xticks(df.index)
    ax1.set_xticklabels(df['label'], fontsize=10)
    # Y-axis labels
    ax1.set_ylabel("Index", color='green')
    ax2.set_ylabel("Change (%)", color='black')
    # Add data labels for index bars
    for i, v in enumerate(df['index']):
        ax1.text(i, v + 2, f"{v:.1f}", ha='center', fontsize=8, color='black')
    # Add MoM labels
    for i, v in enumerate(df['MoM']):
        if pd.notna(v):
            ax2.text(i + 0.1, v - 1 if v > 0 else v + 1, f"{v:.1f}", ha='left', fontsize=8,
                     color='black', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
    # Add YoY labels
    for i, v in enumerate(df['YoY']):
        if pd.notna(v):
            ax2.text(i - 0.1, v + 0.5, f"{v:.1f}", ha='right', fontsize=8, color='white',
                     bbox=dict(facecolor='navy', boxstyle='round,pad=0.3'))
    # Draw horizontal line at 0% change
    ax2.axhline(0, color='gray', linewidth=1, linestyle='--')
    # Title and legend
    plt.title("IPP Index with MoM and YoY Changes", fontsize=14, pad=20)
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.95), ncol=3)
    # Grid and layout
    ax1.grid(True, axis='y', linestyle='--', linewidth=0.5, zorder=1)
    plt.tight_layout()
    plt.show()

    # Add MoM and YoY labels with overlap prevention logic
    for i in range(len(df)):
        mom = df.loc[i, 'MoM']
        yoy = df.loc[i, 'YoY']

        if pd.isna(mom) and pd.isna(yoy):
            continue  # skip if both missing

        # Default offsets
        mom_offset = 0
        yoy_offset = 0.5

        # Check if both values are present
        if pd.notna(mom) and pd.notna(yoy):
            vertical_distance = abs(mom - yoy)

            # If values are close (< 4% apart), increase spacing
            if vertical_distance < 1:
                if mom > yoy:
                    mom_offset = 2
                    yoy_offset = -2
                else:
                    mom_offset = -2
                    yoy_offset = 2
            else:
                # Safe distance, apply smaller offset
                mom_offset = 1.2 if mom > yoy else -1.2
                yoy_offset = -1.2 if mom > yoy else 1.2

        elif pd.isna(yoy):
            mom_offset = -1.5 if mom > 0 else 1.5
        elif pd.isna(mom):
            yoy_offset = -1.5 if yoy > 0 else 1.5

        # Draw MoM label
        if pd.notna(mom):
            ax2.text(i, mom + mom_offset, f"{mom:.1f}", ha='left', fontsize=8,
                     color='black', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

        # Draw YoY label
        if pd.notna(yoy):
            ax2.text(i - 0.3, yoy + yoy_offset, f"{yoy:.1f}", ha='right', fontsize=8, color='white',
                     bbox=dict(facecolor='navy', boxstyle='round,pad=0.3'))

if __name__ == "__main__":
    df = build_df_from_api()
    plot_ipp_combined_chart(df)
