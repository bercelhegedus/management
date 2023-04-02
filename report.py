import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from google_sheets import get_service, process_table
import seaborn as sns
import os
import sys
import traceback
import pdb
import fpdf
import logging

logger = logging.getLogger(__name__)

def create_summary_table(dataframes, output_file):
    # Combine data from all sheets into a single DataFrame
    combined_data = pd.concat(dataframes.values(), keys=dataframes.keys(), names=['Category']).reset_index(level=1, drop=True).reset_index()

    combined_data['Munkaóra'] = combined_data['Munkaóra'].astype(float)

    # Select only the relevant columns
    combined_data = combined_data[['Category', 'Típus', 'Munkaóra']]

    # Calculate the total Munkaóra for each category and Típus
    summary_data = combined_data.groupby(['Category', 'Típus'])['Munkaóra'].sum().reset_index()

    # Calculate the percentage of the total
    total_munkaora = summary_data['Munkaóra'].sum()
    summary_data['Százalék'] = (summary_data['Munkaóra'] / total_munkaora) * 100

    # Create table
    fig, ax = plt.subplots(figsize=(14, 14))
    ax.axis('off')
    ax.axis('tight')
    table = ax.table(cellText=summary_data.values, colLabels=summary_data.columns, loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(14)
    table.scale(1, 2)
    return table

def create_summary_pie_chart(dataframes, output_file):
    # Combine data from all sheets into a single DataFrame
    combined_data = pd.concat(dataframes.values(), keys=dataframes.keys(), names=['Category']).reset_index(level=1, drop=True).reset_index()

    combined_data['Munkaóra'] = combined_data['Munkaóra'].astype(float)

    # Select only the relevant columns
    combined_data = combined_data[['Category', 'Típus', 'Munkaóra']]

    # Calculate the total Munkaóra for each category and Típus
    summary_data = combined_data.groupby(['Category', 'Típus'])['Munkaóra'].sum().reset_index()

    # Calculate the percentage of the total
    total_munkaora = summary_data['Munkaóra'].sum()
    summary_data['Százalék'] = (summary_data['Munkaóra'] / total_munkaora) * 100

    # Create pie chart with nested sections
    outer_pie_data = summary_data.groupby('Category')['Munkaóra'].sum()
    inner_pie_data = summary_data

    fig, ax1 = plt.subplots(nrows=1, figsize=(14, 14))

    outer_pie_colors = sns.color_palette("husl", n_colors=len(outer_pie_data))
    category_colormap = {category: color for category, color in zip(outer_pie_data.index, outer_pie_colors)}

    inner_pie_colors = []
    for cat, group in inner_pie_data.groupby('Category'):
        base_color = category_colormap[cat]
        inner_colors = sns.light_palette(base_color, n_colors=len(group) + 2, reverse=True)
        inner_pie_colors.extend(inner_colors[1:-1])

    wedges1, _ = ax1.pie(outer_pie_data, radius=1, colors=outer_pie_colors, counterclock=False, startangle=90)
    wedges2, _ = ax1.pie(inner_pie_data['Munkaóra'], radius=0.75, colors=inner_pie_colors, counterclock=False, startangle=90)


    # Draw the legend for the inner pie chart
    ax1.legend(wedges2, inner_pie_data['Típus'], title="Típus", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=12)

    return fig


def create_pdf(output_file, summary_table, pie_chart):
    pass


def main():
    SERVICE_ACCOUNT_FILE = 'service_account.json'
    TORZSSHEET_ID = '1LtCsUPBqGYpnEZXyKFFoaPaeFfe1CLU-O9wiTMGqJUE'

    service = get_service(SERVICE_ACCOUNT_FILE)

    sheet_names = ['Csotarto', 'Hegesztes', 'Csovezetek', 'Karimaszereles']
    dataframes = {
        sheet_name: process_table(service, TORZSSHEET_ID, sheet_name)
        for sheet_name in sheet_names
    }

    output_file = "summary_report.pdf"
    pie_chart = create_summary_pie_chart(dataframes, output_file)
    summary_table = create_summary_table(dataframes, output_file)



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except:
        traceback.print_exc()
        pdb.post_mortem()

