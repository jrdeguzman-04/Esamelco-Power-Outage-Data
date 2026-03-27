import pandas as pd
import re

# 1. Load the semi-cleaned JSON data into a DataFrame
df = pd.read_json('data/silver/semi_cleaned_data.json')

# Rename columns for consistency
df.rename(columns={
    'extracted_date': 'Date',
    'extracted_time': 'Time',
    'extracted_area': 'Affected Area(s)'
}, inplace=True)

# 2. Explode the 'Affected Area(s)' column
def split_areas(area_str):
    if pd.isna(area_str):
        return []
    # Split on commas, ampersands, and 'and'
    areas = re.split(r'[,&]|and', area_str)
    # Strip whitespace and filter out empty strings
    areas = [area.strip() for area in areas if area.strip()]
    return areas

df['Affected Area(s)'] = df['Affected Area(s)'].apply(split_areas)
df_exploded = df.explode('Affected Area(s)').reset_index(drop=True)

# 3. Clean the 'Time' field: Replace Unicode en-dash with standard hyphen
df_exploded['Time'] = df_exploded['Time'].str.replace('\u2013', '-', regex=False)

# 4. Normalize the 'Area' names
def normalize_area(area):
    if pd.isna(area):
        return area
    # Remove emojis and special chars except letters, numbers, space
    area = re.sub(r'[^\w\s]', '', area)
    # Replace 'Brgy.' with 'Barangay'
    area = re.sub(r'\bBrgy\.?\b', 'Barangay', area, flags=re.IGNORECASE)
    # Remove extra dots
    area = re.sub(r'\.+', '', area)
    # Title case
    area = area.title()
    return area

df_exploded['Affected Area(s)'] = df_exploded['Affected Area(s)'].apply(normalize_area)

# 5. Final Output: Show the first 10 rows and save as CSV and JSON
print(df_exploded.head(10))
df_exploded.to_csv('data/gold/final_barangay_schedule.csv', index=False)
df_exploded.to_json('data/gold/final_barangay_schedule.json', orient='records', force_ascii=False, indent=4)
print('Saved to data/gold/final_barangay_schedule.csv and data/gold/final_barangay_schedule.json')