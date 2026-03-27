import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# Load data from semi_final.json
DATA_FILE = Path(__file__).resolve().parents[1] / 'data' / 'gold' / 'semi_final.json'

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Normalize the Time column to use hyphen (-) instead of en-dash
if 'Time' in df.columns:
    df['Time'] = df['Time'].astype(str).str.replace('\u2013', '-', regex=False)

# Parse dates
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Process duration
def calculate_duration(time_str):
    if ' – ' not in time_str and '-' not in time_str:
        return 0

    delimiter = ' – ' if ' – ' in time_str else '-'
    parts = time_str.split(delimiter)
    if len(parts) != 2:
        return 0

    start_str, end_str = parts
    try:
        start_str = start_str.strip().replace('NN', 'PM')
        end_str = end_str.strip().replace('NN', 'PM')
        start = datetime.strptime(start_str, '%I:%M %p')
        end = datetime.strptime(end_str, '%I:%M %p')
        duration = (end - start).total_seconds() / 3600
        return max(duration, 0)
    except ValueError:
        return 0

df['Duration'] = df.get('Time', pd.Series()).fillna('').astype(str).apply(calculate_duration)

# Sidebar filters
st.sidebar.title('Filters')
area_options = ['All'] + sorted(df['Affected Area(s)'].dropna().unique().tolist()) if 'Affected Area(s)' in df else ['All']
selected_area = st.sidebar.selectbox('Affected Area(s)', area_options)

start_date = st.sidebar.date_input('Start Date', value=df['Date'].min() if 'Date' in df else None)
end_date = st.sidebar.date_input('End Date', value=df['Date'].max() if 'Date' in df else None)

show_all = st.sidebar.checkbox('Show all data (ignore filters)', value=False)

if show_all:
    filtered_df = df.copy()
else:
    filtered_df = df.copy()
    if selected_area != 'All' and 'Affected Area(s)' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Affected Area(s)'] == selected_area]

    if 'Date' in filtered_df.columns:
        if start_date:
            filtered_df = filtered_df[filtered_df['Date'] >= pd.to_datetime(start_date)]
        if end_date:
            filtered_df = filtered_df[filtered_df['Date'] <= pd.to_datetime(end_date)]

# Dashboard header
st.title('ESAMELCO Power Interruptions Dashboard')

# Table
st.header('Power Outage Data Table')
st.write('Data source: data/gold/semi_final.json')
st.dataframe(filtered_df)

# Download option
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button('Download filtered data as CSV', csv, 'esamelco_outages_filtered.csv', 'text/csv')

# Summary metrics
st.subheader('Summary')
col1, col2, col3 = st.columns(3)
with col1:
    st.metric('Total Records', len(filtered_df))
with col2:
    st.metric('Total Valid Dates', filtered_df['Date'].nunique() if 'Date' in filtered_df.columns else 0)
with col3:
    st.metric('Total Outage Hours', round(filtered_df['Duration'].sum(), 2) if 'Duration' in filtered_df.columns else 0)

# Bar chart
if 'Affected Area(s)' in filtered_df.columns and 'Duration' in filtered_df.columns:
    st.header('Total Outage Hours per Area')
    area_duration = filtered_df.groupby('Affected Area(s)')['Duration'].sum().sort_values()
    fig, ax = plt.subplots()
    area_duration.plot(kind='barh', ax=ax, color='skyblue')
    ax.set_xlabel('Total Hours')
    ax.set_ylabel('Affected Area(s)')
    ax.set_title('Total Outage Hours per Area')
    plt.style.use('ggplot')
    st.pyplot(fig)

# Timeline
if 'Date' in filtered_df.columns and 'Time' in filtered_df.columns:
    st.header('Outage Timeline')
    unique_dates = sorted(filtered_df['Date'].dropna().unique())
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    for i, date in enumerate(unique_dates):
        day_data = filtered_df[filtered_df['Date'] == date]
        for _, row in day_data.iterrows():
            if ' – ' not in str(row['Time']):
                continue
            start_str, end_str = str(row['Time']).split(' – ')
            start_str = start_str.strip().replace('NN', 'PM')
            end_str = end_str.strip().replace('NN', 'PM')
            try:
                start_time = datetime.strptime(start_str, '%I:%M %p').time()
                end_time = datetime.strptime(end_str, '%I:%M %p').time()
            except ValueError:
                continue
            start_min = start_time.hour * 60 + start_time.minute
            end_min = end_time.hour * 60 + end_time.minute
            duration_min = max(end_min - start_min, 0)
            ax2.broken_barh([(start_min, duration_min)], (i, 0.8), facecolors='red', alpha=0.7)

    ax2.set_xlabel('Time of Day (minutes from midnight)')
    ax2.set_ylabel('Date')
    ax2.set_yticks(range(len(unique_dates)))
    ax2.set_yticklabels([d.strftime('%b %d, %Y') for d in unique_dates])
    ax2.set_xticks(range(0, 1441, 120))
    ax2.set_xticklabels([f'{h:02d}:00' for h in range(0, 25, 2)])
    ax2.set_title('Outage Timeline')
    plt.style.use('ggplot')
    st.pyplot(fig2)
