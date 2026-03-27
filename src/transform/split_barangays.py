import json
import re
import os

def normalize_date(date_string):
    """Normalize date format"""
    if not date_string:
        return date_string
    
    # Remove "(Friday)" or "(SATURDAY)" or "(TODAY)"
    date_string = re.sub(r'\s*\([^)]*\)$', '', date_string).strip()
    
    # Expand abbreviated months ONLY - don't process already-full month names
    month_abbrev = {
        'jan': 'January', 'janua': 'January',  # Handle "JANUA..." edge case
        'feb': 'February', 
        'mar': 'March', 
        'apr': 'April',
        'may': 'May', 
        'jun': 'June', 
        'jul': 'July', 
        'aug': 'August',
        'sep': 'September', 
        'oct': 'October', 
        'nov': 'November', 
        'dec': 'December'
    }
    
    # Only replace if it's an abbreviation (3-4 chars followed by optional period, then space/number)
    for short, full in month_abbrev.items():
        # Match: "Nov." or "Nov" or "NOVEMBER" (keep full names as-is)
        date_string = re.sub(f'\\b{short}\\.(?=\\s|\\d)', full, date_string, flags=re.IGNORECASE)
        date_string = re.sub(f'\\b{short}(?=\\s|\\d|,)', full, date_string, flags=re.IGNORECASE)
    
    # Capitalize full month names (only first letter)
    months = ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november', 'december']
    for month in months:
        pattern = f'\\b{month}\\b'
        date_string = re.sub(pattern, month.capitalize(), date_string, flags=re.IGNORECASE)
    
    # Handle "DECEMBER 3 and 4, 2025" -> "December 3-4, 2025"
    date_string = re.sub(r'(\w+)\s+(\d+)\s+and\s+(\d+)', r'\1 \2-\3', date_string)
    
    return date_string.strip()

def normalize_time(time_string):
    """Normalize time format to standard HH:MM AM/PM – HH:MM AM/PM"""
    if not time_string:
        return time_string
    
    # Replace "NN" with "PM"
    time_string = re.sub(r'\bNN\b', 'PM', time_string, flags=re.IGNORECASE)
    
    # Normalize format: "9am" -> "9:00 AM", "9:00am" -> "9:00 AM"
    time_string = re.sub(r'(\d{1,2})([ap]m)', r'\1:00 \2', time_string, flags=re.IGNORECASE)
    time_string = re.sub(r'(\d{1,2}):(\d{2})([ap]m)', r'\1:\2 \3', time_string, flags=re.IGNORECASE)
    
    # Remove duplicate :00 (from converting both 9am and 09am forms)
    time_string = re.sub(r'(\d{1,2}):00:00', r'\1:00', time_string)
    
    # Use en-dash for ranges
    time_string = re.sub(r'\s*(?:–|to|–|-)\s*', ' – ', time_string)
    time_string = re.sub(r'\s*(?:TO)\s+', ' – ', time_string, flags=re.IGNORECASE)
    
    # Uppercase AM/PM
    time_string = re.sub(r'\b(am|pm)\b', lambda m: m.group(1).upper(), time_string)
    
    # Clean up multiple separators/slashes
    time_string = re.sub(r'\s*[;/]\s*', ' / ', time_string)
    
    # Remove duplicate dash sequences
    time_string = re.sub(r'–\s*–+', ' – ', time_string)
    time_string = re.sub(r',\s*([0-9])', r' / \1', time_string)  # Convert comma-separated times to slash
    
    return time_string.strip()

def clean_area_text(area):
    """Remove unnecessary words and formatting"""
    area = area.strip()
    
    # Remove emojis and markers
    area = re.sub(r'[📍⚡✅☑📌🗓️🕛]', '', area).strip()
    
    # Remove unnecessary phrases
    remove_phrases = [
        r'hospital village',
        r'compound',
        r'(?:entire province)',
        r'(?:Thank you.*)',
        r'(?:\(entire province\))',
        r',?\s*\(entire province\)',
    ]
    
    for phrase in remove_phrases:
        area = re.sub(phrase, '', area, flags=re.IGNORECASE).strip()
    
    # Remove "City" suffix if it's descriptive only
    area = re.sub(r',?\s*City$', '', area, flags=re.IGNORECASE).strip()
    
    # Clean up extra spacing and punctuation
    area = re.sub(r'\s+', ' ', area).strip()
    area = re.sub(r'^[,.\s]+|[,.\s]+$', '', area).strip()
    
    return area

def expand_range(start, end, municipality=''):
    """Expand barangay range like '01-05' into separate entries"""
    try:
        start_num = int(start)
        end_num = int(end)
        results = []
        for i in range(start_num, end_num + 1):
            brgy = f"Brgy. {i:02d}" if i < 10 else f"Brgy. {i}"
            if municipality:
                results.append(f"{brgy} ({municipality})")
            else:
                results.append(brgy)
        return results
    except:
        return []

def parse_barangays(area_string):
    """Parse area string and return list of individual barangays"""
    if not area_string:
        return []
    
    area_string = clean_area_text(area_string)
    barangays = []
    
    # Handle "BRGY. MAYPANGDAN TO SMART TOWER" -> "BRGY. MAYPANGDAN"
    area_string = re.sub(r'\s*TO\s+SMART\s+TOWER', '', area_string, flags=re.IGNORECASE).strip()
    
    # Check for range patterns like "Brgy. 01-05"
    range_match = re.search(r'Brgy\.?\s*(\d{1,2})\s*-\s*(\d{1,2})', area_string, re.IGNORECASE)
    if range_match:
        start, end = range_match.groups()
        municipality = re.sub(r'Brgy\.?\s*\d{1,2}\s*-\s*\d{1,2}', '', area_string).strip()
        municipality = municipality.replace('(', '').replace(')', '').strip()
        if not municipality:
            municipality = None
        barangays.extend(expand_range(start, end, municipality))
        return barangays
    
    # Split by comma, semicolon, and "and" but be careful with parentheses
    parts = re.split(r'[,;]\s*(?:and\s+)?|(?<!\()\s+and\s+(?!\))', area_string, flags=re.IGNORECASE)
    
    for part in parts:
        part = part.strip()
        if not part or len(part) < 2 or part == '()':
            continue
        
        # Format: "brgy. Mabini Sulat" -> "Brgy. Mabini (Sulat)"
        brgy_match = re.match(r'^(?:Brgy\.?|Barangay)\s+([A-Za-z\s]+?)(?:\s+([A-Za-z]+))?$', part, re.IGNORECASE)
        if brgy_match:
            brgy_name = brgy_match.group(1).strip()
            mun = brgy_match.group(2)
            
            # Format properly
            if mun and mun.lower() not in ['substation']:
                barangays.append(f"Brgy. {brgy_name} ({mun})")
            else:
                barangays.append(f"Brgy. {brgy_name}")
        elif 'substation' in part.lower():
            # Extract name before "substation"
            substation_name = re.sub(r'\s+substation.*$', '', part, flags=re.IGNORECASE).strip()
            if substation_name:
                barangays.append(f"{substation_name} Substation")
        else:
            # Regular location name
            barangays.append(part)
    
    # Remove duplicates while preserving order
    seen_set = set()
    unique = []
    for item in barangays:
        if item and item not in seen_set and item != '()':
            seen_set.add(item)
            unique.append(item)
    
    return unique

def format_barangay(barangay_name):
    """Format barangay name consistently"""
    barangay_name = barangay_name.strip()
    
    # Already properly formatted
    if re.match(r'^Brgy\.\s+', barangay_name) or re.match(r'.+\s+Substation$', barangay_name, re.IGNORECASE):
        return barangay_name
    
    # Return as-is for other valid entries
    return barangay_name

def clean_reason(reason):
    """Clean reason/activity field"""
    if not reason:
        return reason
    
    # Remove emoji markers at start
    reason = re.sub(r'^[📌✅⚡]\s*', '', reason).strip()
    
    # Clean up extra spaces
    reason = re.sub(r'\s+', ' ', reason).strip()
    
    return reason

def transform_data(input_file, output_file):
    """Transform semi_final.json to final.json with split barangays"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    final_data = []
    seen = set()  # Track exact duplicates
    
    for record in data:
        raw_date = record.get('Date', '').strip()
        raw_time = record.get('Time', '').strip()
        affected_areas = record.get('Affected Area(s)', '')
        reason = clean_reason(record.get('Reason / Activity', '').strip())
        original_post = record.get('Original Post', '').strip()
        
        # Special handling for January 7, 2026 with ESSU - split into two records
        if 'JANUARY 7' in raw_date.upper() and 'ESSU' in affected_areas.upper():
            # First record: Brgy. Maypangdan with 10:30 AM - 12:00 PM
            final_data.append({
                "Date": "January 7, 2026",
                "Time": "10:30 AM – 12:00 PM",
                "Barangay": "Brgy. Maypangdan (Borongan)",
                "Reason / Activity": "Removal of old wood pole and transformer",
                "Original Post": original_post
            })
            # Second record: Brgy. 2 (Balangkayan) with 10:00 AM - 3:00 PM
            final_data.append({
                "Date": "January 7, 2026",
                "Time": "10:00 AM – 3:00 PM",
                "Barangay": "Brgy. 2 (Balangkayan)",
                "Reason / Activity": "Vegetation line clearing",
                "Original Post": original_post
            })
            continue  # Skip general parsing for this record
        
        # Normalize date and time for other records
        date = normalize_date(raw_date)
        time = normalize_time(raw_time)
        
        # General parsing for other records
        barangays = parse_barangays(affected_areas)
        
        # If no barangays found, use cleaned area name
        if not barangays:
            clean_area = clean_area_text(affected_areas)
            if clean_area and clean_area != '()':
                barangays = [clean_area]
            else:
                continue  # Skip if no valid area found
        
        for barangay in barangays:
            barangay = format_barangay(barangay)
            
            # Skip empty barangays
            if not barangay or barangay == '()':
                continue
            
            final_record = {
                "Date": date,
                "Time": time,
                "Barangay": barangay,
                "Reason / Activity": reason,
                "Original Post": original_post
            }
            
            # Create a unique key for duplicate detection
            record_key = (date, time, barangay, reason)
            
            # Only add if not a duplicate
            if record_key not in seen:
                seen.add(record_key)
                final_data.append(final_record)
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Transformation complete!")
    print(f"📊 {len(final_data)} records created from {len(data)} source records")
    print(f"💾 Saved to: {output_file}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    input_path = os.path.join(project_root, 'data', 'gold', 'semi_final.json')
    output_path = os.path.join(project_root, 'data', 'gold', 'final.json')
    
    transform_data(input_path, output_path)
