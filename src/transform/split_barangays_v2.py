import json
import re
import os

def normalize_date(date_string):
    """Normalize date format"""
    if not date_string:
        return ""
    
    # Remove parenthetical suffixes
    date_string = re.sub(r'\s*\([^)]*\)$', '', date_string).strip()
    
    # Replace abbreviated months with full names
    abbrev = {'jan': 'January', 'feb': 'February', 'mar': 'March', 'apr': 'April', 'may': 'May', 'jun': 'June',
              'jul': 'July', 'aug': 'August', 'sep': 'September', 'oct': 'October', 'nov': 'November', 'dec': 'December'}
    for short, full in abbrev.items():
        date_string = re.sub(f'\\b{short}\\.?\\b', full, date_string, flags=re.IGNORECASE)
    
    # Capitalize months
    for month in ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']:
        date_string = re.sub(f'\\b{month}\\b', month.capitalize(), date_string, flags=re.IGNORECASE)
    
    # "X and Y" -> "X-Y"
    date_string = re.sub(r'(\d+)\s+and\s+(\d+)', r'\1-\2', date_string)
    
    return date_string

def normalize_time(time_str):
    """Normalize time format"""
    if not time_str:
        return ""
    
    time_str = re.sub(r'\bNN\b', 'PM', time_str, flags=re.IGNORECASE)
    time_str = re.sub(r'(\d{1,2})([ap]m)', r'\1:00 \2', time_str, flags=re.IGNORECASE)
    time_str = re.sub(r'(\d{1,2}):(\d{2})([ap]m)', r'\1:\2 \3', time_str, flags=re.IGNORECASE)
    time_str = re.sub(r'(\d{1,2}):00:00', r'\1:00', time_str)  # Remove duplicate :00
    time_str = re.sub(r'\s*(?:–|to|-|/)\s*', ' – ', time_str)
    time_str = re.sub(r'\bAM\b|\bPM\b', lambda m: m.group().upper(), time_str)
    time_str = re.sub(r'\s*,\s*', ' / ', time_str)
    return time_str.strip()

def main():
    with open('data/silver/stage_3_standardized/semi_final.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    output = []
    
    for record in data:
        date = record.get('Date', '').strip()
        time = record.get('Time', '').strip()
        areas = record.get('Affected Area(s)', '').strip()
        reason = record.get('Reason / Activity', '').strip()
        post = record.get('Original Post', '').strip()
        
        # Special case: January 7, 2026 ESSU record -> split into 2 records
        if 'JANUARY 7' in date.upper() and 'ESSU' in areas.upper():
            output.append({
                "Date": "January 7, 2026",
                "Time": "10:30 AM – 12:00 PM",
                "Barangay": "Brgy. Maypangdan (Borongan)",
                "Reason / Activity": "Removal of old wood pole and transformer",
                "Original Post": post
            })
            output.append({
                "Date": "January 7, 2026",
                "Time": "10:00 AM – 3:00 PM",
                "Barangay": "Brgy. 2 (Balangkayan)",
                "Reason / Activity": "Vegetation line clearing",
                "Original Post": post
            })
            continue
        
        # Parse and split barangays
        date_norm = normalize_date(date)
        time_norm = normalize_time(time)
        reason_clean = re.sub(r'^[📌✅⚡]\s*', '', reason).strip()
        
        # Extract barangays based on content
        barangays = []
        
        # Borongan, San Isidro, San Julian (simple municipality names)
        if 'Borongan' in areas and 'San' not in areas:
            barangays = ['Borongan (General Area)']
        elif 'San Isidro' in areas:
            barangays = ['San Isidro']
        elif 'San Julian' in areas:
            barangays = ['San Julian']
        # San Policarpo Brgy. 01-05 range
        elif 'Brgy. 01- 05' in areas or '(Brgy. 01- 05)' in areas:
            barangays = [f'Brgy. {i:02d} (San Policarpo)' for i in range(1, 6)]
        # November 28: multiple barangays
        elif 'San Mateo' in areas and 'San Juan' in areas:
            barangays = ['Brgy. San Mateo', 'Brgy. San Juan', 'Brgy. A-et', 'Brgy. Mabini (Sulat)']
        # November 29: Maypangdan
        elif 'MAYPANGDAN' in areas and 'SMART TOWER' in areas:
            barangays = ['Brgy. Maypangdan']
        # December 3-4: Substations
        elif 'Borongan' in areas and 'Taft' in areas and 'Substations' in areas:
            barangays = ['Borongan Substation', 'Taft Substation', 'Quinapondan Substation', 'Balangiga Substation']
        # December 2: Brgy. Sabang South
        elif 'Sabang South' in areas:
            barangays = ['Brgy. Sabang South (Borongan)']
        # March 25: Brgy. 8 and 9A
        elif 'Brgy. 8' in areas and 'Brgy. 9A' in areas:
            barangays = ['Brgy. 8 (Guiuan)', 'Brgy. 9A (Guiuan)']
        else:
            # Fallback
            barangays = [areas.replace('📍', '').strip()] if areas else []
        
        # Create output records
        for brgy in barangays:
            if brgy:
                output.append({
                    "Date": date_norm,
                    "Time": time_norm,
                    "Affected Area(s)": brgy,
                    "Reason / Activity": reason_clean,
                    "Original Post": post
                })
    
    with open('data/silver/stage_4_final/final.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Complete! {len(output)} records generated")

if __name__ == "__main__":
    os.chdir('/Users/johnreydeguzman/Esamelco-Power-Outage-Data')
    main()
