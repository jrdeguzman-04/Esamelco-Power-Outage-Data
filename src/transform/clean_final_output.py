import json
import re
import os
from datetime import datetime

def normalize_date(date_str):
    """Normalize date format to 'Month DD, YYYY'."""
    if not date_str:
        return date_str
    
    date_str = date_str.strip()
    
    # Remove any periods after month names that came from input
    date_str = re.sub(r'November\.(?=\s)', 'November', date_str, flags=re.IGNORECASE)
    date_str = re.sub(r'December\.(?=\s)', 'December', date_str, flags=re.IGNORECASE)
    date_str = re.sub(r'January\.(?=\s)', 'January', date_str, flags=re.IGNORECASE)
    
    # Handle month abbreviations
    months = {
        'jan': 'January', 'feb': 'February', 'mar': 'March',
        'apr': 'April', 'may': 'May', 'jun': 'June',
        'jul': 'July', 'aug': 'August', 'sep': 'September',
        'oct': 'October', 'nov': 'November', 'dec': 'December'
    }
    
    for abbr, full in months.items():
        # Handle both with and without period
        date_str = re.sub(rf'\b{abbr}\.?\b', full, date_str, flags=re.IGNORECASE)
    
    # Handle "DECEMBER 3-4, 2025" -> split into individual dates
    if re.search(r'(\w+)\s+(\d+)-(\d+),\s+(\d{4})', date_str):
        match = re.search(r'(\w+)\s+(\d+)-(\d+),\s+(\d{4})', date_str)
        month, day1, day2, year = match.groups()
        return [f"{month} {day1}, {year}", f"{month} {day2}, {year}"]
    
    return date_str

def normalize_time(time_str):
    """Normalize time format to 'X:XX AM/PM - X:XX AM/PM'."""
    if not time_str:
        return time_str
    
    time_str = time_str.strip()
    
    # Handle "MN" -> "AM" (midnight notation)
    time_str = re.sub(r'\bMN\b', 'AM', time_str, flags=re.IGNORECASE)
    
    # Handle "NN" -> "PM" (noon notation)
    time_str = re.sub(r'\bNN\b', 'PM', time_str, flags=re.IGNORECASE)
    
    # Handle "am/pm" -> "AM/PM"
    time_str = re.sub(r'\bam\b', 'AM', time_str, flags=re.IGNORECASE)
    time_str = re.sub(r'\bpm\b', 'PM', time_str, flags=re.IGNORECASE)
    
    # Handle "TO" -> "-"
    time_str = re.sub(r'\s+TO\s+', ' - ', time_str, flags=re.IGNORECASE)
    
    # Handle en-dash (–) -> hyphen (-)
    time_str = time_str.replace('–', '-')
    
    # Remove seconds format (:MM:00) but keep regular :MM format
    # This handles 9:30:00 AM -> 9:30 AM
    time_str = re.sub(r'(\d{1,2}):(\d{2}):00(\s*(?:AM|PM))', r'\1:\2\3', time_str, flags=re.IGNORECASE)
    
    # Normalize spaces around hyphens
    time_str = re.sub(r'\s*-\s*', ' - ', time_str)
    
    return time_str

def normalize_reason(reason_str):
    """Normalize reason to one of 5 categories."""
    if not reason_str:
        return "Line Maintenance"
    
    reason_lower = reason_str.lower()
    
    # Vegetation Clearing
    if any(kw in reason_lower for kw in ['vegetation', 'tree cutting', 'line clear', 'clearing', 'magpuputol', 'harani']):
        return "Vegetation Clearing"
    
    # Equipment Maintenance
    if any(kw in reason_lower for kw in ['remove guy wire', 'tap guy', 'transformer', 'pole removal', 'old wood pole']):
        return "Equipment Maintenance"
    
    # Infrastructure Upgrade
    if any(kw in reason_lower for kw in ['construction', 'distribution line', 'upgrade', 'installation', 'three phase']):
        return "Infrastructure Upgrade"
    
    # Transmission Maintenance
    if any(kw in reason_lower for kw in ['transmission', 'ngcp', 'substation', 'conductor payout', 'correction of defects']):
        return "Transmission Maintenance"
    
    # Line Maintenance (default)
    return "Line Maintenance"

def extract_barangay_info(original_post, current_barangay):
    """Extract barangay information from original post."""
    barangays = []
    
    # Handle special case: January 7 ESSU split
    if 'ESSU' in original_post and 'Balangkayan' in original_post:
        if 'Brgy. Maypangdan' in current_barangay or 'ESSU' in current_barangay:
            return ["Brgy. Maypangdan (Borongan)"], ["10:30 AM - 12:00 PM"]
        elif 'Brgy. 2' in original_post:
            return ["Brgy. 2 (Balangkayan)"], ["10:00 AM - 3:00 PM"]
    
    # Handle Sabang South case
    if 'Sabang South' in original_post and 'Borongan' in current_barangay:
        return ["Brgy. Sabang South (Borongan)"], [None]
    
    # Handle municipalities split: "Municipalities of Oras, San Policarpo, Arteche and Jipapad, (Brgy...)"
    if 'Municipalities of' in current_barangay or 'municipalities of' in current_barangay:
        # Remove parenthetical info first
        cleaned = re.sub(r'\s*\([^)]*\)', '', current_barangay)
        # Extract municipality names
        cleaned = cleaned.replace('Municipalities of ', '').replace('municipalities of ', '')
        # Split on commas and 'and'
        municipalities = re.split(r'[,]\s*|,\s*and\s+|\s+and\s+', cleaned)
        municipalities = [m.strip() for m in municipalities if m.strip() and len(m.strip()) > 1]
        if municipalities:
            return municipalities, [None] * len(municipalities)
    
    # Handle range like "Brgy. 01- 05"
    if re.search(r'Brgy\.\s+(\d+)-\s*(\d+)', current_barangay):
        match = re.search(r'Brgy\.\s+(\d+)-\s*(\d+)', current_barangay)
        start, end = int(match.group(1)), int(match.group(2))
        municipality = re.search(r'\(([^)]+)\)', current_barangay)
        municipality_name = municipality.group(1) if municipality else ""
        
        result = []
        for i in range(start, end + 1):
            if municipality_name:
                result.append(f"Brgy. {i:02d} ({municipality_name})")
            else:
                result.append(f"Brgy. {i:02d}")
        return result, [None] * len(result)
    
    # Handle substation split
    if 'substation' in current_barangay.lower():
        # Extract substations from post or barangay field
        substations = []
        for word in ['Borongan', 'Taft', 'Quinapondan', 'Balangiga']:
            if word in current_barangay or word in str(original_post):
                substations.append(f"{word} Substation")
        if substations:
            return substations, [None] * len(substations)
    
    # Handle comma/ampersand separated with multiple items (but not parenthetical)
    if (',' in current_barangay or ' and ' in current_barangay) and 'Municipalities' not in current_barangay:
        # Remove parenthetical info first
        cleaned = re.sub(r'\s*\([^)]*\)', '', current_barangay)
        # Split on commas and 'and'
        parts = re.split(r'[,]\s*|,\s*and\s+|\s+and\s+', cleaned)
        parts = [p.strip() for p in parts if p.strip() and len(p.strip()) > 1]
        if len(parts) > 1:
            return parts, [None] * len(parts)
    
    # If it's already in good format, return as-is
    if '(' in current_barangay and ')' in current_barangay:
        return [current_barangay], [None]
    
    return [current_barangay], [None]

def clean_output(input_file, output_file):
    """Clean and normalize the output JSON file."""
    
    # Load original data
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cleaned_data = []
    
    for record in data:
        date = record.get('Date', '').strip()
        time = record.get('Time', '').strip()
        barangay = record.get('Affected Area(s)', '').strip()
        reason = record.get('Reason / Activity', '').strip()
        original_post = record.get('Original Post', '').strip()
        
        # Normalize formats
        normalized_date = normalize_date(date)
        normalized_time = normalize_time(time)
        normalized_reason = normalize_reason(reason)
        
        # Handle date ranges (e.g., "December 3-4, 2025")
        if isinstance(normalized_date, list):
            dates = normalized_date
            times = normalized_time.split(' / ')
            if len(times) == 2:
                date_time_pairs = [(dates[0], times[0]), (dates[1], times[1])]
            else:
                date_time_pairs = [(d, normalized_time) for d in dates]
        else:
            date_time_pairs = [(normalized_date, normalized_time)]
        
        # Extract barangays and custom times if applicable
        barangays, custom_times = extract_barangay_info(original_post, barangay)
        
        # For January 7 ESSU special case
        if 'ESSU' in original_post and 'Balangkayan' in original_post:
            # Create two records
            cleaned_data.append({
                "Date": "January 7, 2026",
                "Time": "10:30 AM - 12:00 PM",
                "Affected Area(s)": "Brgy. Maypangdan (Borongan)",
                "Reason / Activity": "Equipment Maintenance",
                "Original Post": original_post
            })
            cleaned_data.append({
                "Date": "January 7, 2026",
                "Time": "10:00 AM - 3:00 PM",
                "Affected Area(s)": "Brgy. 2 (Balangkayan)",
                "Reason / Activity": "Vegetation Clearing",
                "Original Post": original_post
            })
            continue
        
        # Handle December 3-4 substation case
        if date.count('-') >= 1 and '3' in date and '4' in date and 'December' in date:
            # Extract substations from the post content
            substations_list = []
            for word in ['Borongan', 'Taft', 'Quinapondan', 'Balangiga']:
                if word in original_post:
                    substations_list.append(f"{word} Substation")
            
            if not substations_list:
                substations_list = ['Borongan Substation', 'Taft Substation', 'Quinapondan Substation', 'Balangiga Substation']
            
            for substation in substations_list:
                cleaned_data.append({
                    "Date": "December 3, 2025",
                    "Time": "6:00 AM - 7:00 AM",
                    "Affected Area(s)": substation,
                    "Reason / Activity": normalized_reason,
                    "Original Post": original_post
                })
                cleaned_data.append({
                    "Date": "December 4, 2025",
                    "Time": "5:00 PM - 6:00 PM",
                    "Affected Area(s)": substation,
                    "Reason / Activity": normalized_reason,
                    "Original Post": original_post
                })
            continue
        
        # Regular processing
        for idx, (dt_date, dt_time) in enumerate(date_time_pairs):
            custom_time = custom_times[idx] if idx < len(custom_times) and custom_times[idx] else dt_time
            
            for brgy in barangays:
                cleaned_data.append({
                    "Date": dt_date,
                    "Time": custom_time,
                    "Affected Area(s)": brgy,
                    "Reason / Activity": normalized_reason,
                    "Original Post": original_post
                })
    
    # Remove duplicates while preserving order
    seen = set()
    deduplicated_data = []
    for record in cleaned_data:
        # Create a hashable key from record
        key = (record['Date'], record['Time'], record['Affected Area(s)'], record['Reason / Activity'])
        if key not in seen:
            seen.add(key)
            deduplicated_data.append(record)
    
    cleaned_data = deduplicated_data
    
    # Sort by date (newest to oldest) and then by time
    def parse_date_for_sorting(date_str):
        """Convert date string to datetime object for sorting"""
        try:
            return datetime.strptime(date_str, "%B %d, %Y")
        except:
            return datetime.now()
    
    cleaned_data.sort(
        key=lambda x: parse_date_for_sorting(x['Date']),
        reverse=True  # Newest first
    )
    
    # Save cleaned data
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Cleaned output saved to {output_file}")
    print(f"📊 Total records: {len(cleaned_data)}")
    print(f"📅 Date range: {cleaned_data[0]['Date']} to {cleaned_data[-1]['Date']}")
    return cleaned_data

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    input_file = os.path.join(project_root, 'data', 'gold', 'final_1.json')
    output_file = os.path.join(project_root, 'data', 'gold', 'final_1_cleaned.json')
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}")
        return
    
    clean_output(input_file, output_file)

if __name__ == "__main__":
    main()
