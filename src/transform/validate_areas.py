import os
import pandas as pd
import json
import difflib

# 1. Parse data.json to create a flat list of all unique 'barangay_name' and municipality names
if os.path.exists('data/bronze/data.json'):
    with open('data/bronze/data.json', 'r') as f:
        data = json.load(f)

    barangays = set()
    municipalities = set()

    for province in data:
        if province.get('province_name', '').lower() == 'eastern samar':
            for municipality in province.get('municipalities', []):
                municipalities.add(municipality.get('municipality_name', '').lower())
                for barangay in municipality.get('barangays', []):
                    barangays.add(barangay.get('barangay_name', '').lower())

    barangay_list = list(barangays)
    municipality_list = list(municipalities)

    data_source_available = True
else:
    print("Warning: data/bronze/data.json not found. Skipping barangay validation and copying final schedule as-is.")
    data_source_available = False
    barangay_list = []
    municipality_list = []

# 2. Load the JSON
df = pd.read_json('data/silver/stage_1_filtered/final_barangay_schedule.json')

# 3. Function to validate area
def is_valid_area(area):
    area_lower = area.lower()
    # Check if it's a municipality
    if area_lower in municipality_list:
        return True
    # Fuzzy match with barangays using difflib
    matches = difflib.get_close_matches(area_lower, barangay_list, n=1, cutoff=0.6)
    return len(matches) > 0

# 4. Filter the DataFrame
if data_source_available:
    df_cleaned = df[df['Affected Area(s)'].apply(is_valid_area)]
else:
    df_cleaned = df.copy()

# 5. Output to JSON
df_cleaned.to_json('data/silver/stage_2_cleaned/fully_cleaned_outages.json', orient='records', force_ascii=False, indent=4)

print(f"Filtered {len(df_cleaned)} rows out of {len(df)}")
print("Saved to data/silver/stage_2_cleaned/fully_cleaned_outages.json")