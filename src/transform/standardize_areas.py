import json
import re
import os
from thefuzz import fuzz
from thefuzz import process

def load_json(file_path):
    """Load JSON data from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, file_path):
    """Save data to JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def clean_original_post(original_post):
    """Clean original post by removing newlines and extra spaces."""
    if not original_post:
        return ""
    
    # Replace newlines with spaces
    cleaned = original_post.replace('\n', ' ')
    
    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Strip leading/trailing whitespace
    cleaned = cleaned.strip()
    
    return cleaned

def extract_clean_date(original_post, current_date):
    """Extract and clean date from original post."""
    original_post_lower = original_post.lower()
    
    # Try to extract from original post
    patterns = [
        r'(?:DATE|WHEN)[:\s]+([A-Za-z0-9,\s\-\(\)]+?)(?:\n|$)',
        r'🗓\ufe0f?[:\s]*([A-Za-z0-9,\s\-\(\)]+?)(?:\n|$)',
        r'🗓[:\s]*([A-Za-z0-9,\s\-\(\)]+?)(?:\n|$)',
        r'([A-Za-z]+\.?\s+\d{1,2},?\s+\d{4}(?:\s*\([^)]+\))?)',  # Nov. 28, 2025 (Friday)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, original_post, re.IGNORECASE)
        if match:
            date_text = match.group(1).strip()
            # Remove extra phrases like "- TODAY"
            date_text = re.sub(r'\s*-\s*(TODAY|today).*$', '', date_text).strip()
            if date_text and len(date_text) > 5 and "power" not in date_text.lower():
                return date_text
    
    # Fallback: clean current_date
    clean_date = current_date.strip()
    clean_date = re.sub(r'\s*-\s*(TODAY|today).*$', '', clean_date).strip()
    # Return even if it looks odd, better than "Date not specified"
    if clean_date and len(clean_date) > 3 and "power" not in clean_date.lower():
        return clean_date
    return "Date not specified"

def extract_clean_time(original_post, current_time):
    """Extract and clean time from original post."""
    # Look for time ranges in emoji format first
    pattern = r'🕛\s*([0-9]{1,2}:[0-9]{2}\s*(?:AM|PM|am|pm|NN|nn)\s*(?:-|–|to)\s*[0-9]{1,2}:[0-9]{2}\s*(?:AM|PM|am|pm|NN|nn))'
    matches = re.findall(pattern, original_post)
    
    if matches:
        # Clean and deduplicate time ranges
        times_set = []
        for m in matches:
            clean = m.strip()
            if clean not in times_set:
                times_set.append(clean)
        if times_set:
            return '; '.join(times_set)
    
    # Fallback to current_time if valid
    clean_time = current_time.strip()
    # Remove location text if attached
    clean_time = re.sub(r'\s*-\s*[A-Z][A-Za-z\s]+(?=;|$)', '', clean_time).strip()
    return clean_time if clean_time else current_time.strip()

def extract_clean_area(original_post, current_area):
    """Extract and clean affected area from original post."""
    # Remove emojis and unnecessary text from area
    cleaned = re.sub(r'[📍⚡✅☑📌]', '', current_area).strip()
    cleaned = re.sub(r',\s*Thank you.*$', '', cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r',\s*\*All substations.*$', '', cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r'[,\s]*\(entire province\)\s*,.*$', r' (entire province)', cleaned, flags=re.IGNORECASE).strip()
    
    # STRICT OVERRIDE: Replace ESSU references with full name
    if re.search(r'\b(ESSU|ESSU Main Campus|ESSU Compound)\b', cleaned, re.IGNORECASE):
        cleaned = re.sub(r'\bESSU Main Campus\b', 'Eastern Samar State University in Maypangdan', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\bESSU Compound\b', 'Eastern Samar State University in Maypangdan', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\bESSU\b', 'Eastern Samar State University in Maypangdan', cleaned, flags=re.IGNORECASE)
    
    # Remove trailing garbage  
    if len(cleaned) > 5:
        return cleaned
    
    return current_area.strip()

def parse_areas(area_string):
    """Parse extracted_area string to get potential barangay names."""
    if not area_string:
        return []

    # Remove emojis and special characters
    cleaned = re.sub(r'[📍⚡✅☑📌]', '', area_string)

    # Common non-location phrases to remove
    non_location_phrases = [
        'thank you for your patience',
        'understanding',
        'we are working as quickly',
        'safely as possible',
        'get lights back on',
        'sorry for the inconvenience',
        'we\'re sorry for the inconvenience',
        'contact numbers',
        'esamelco burak',
        'line maintenance',
        'esamelco office',
        'pahinumdum',
        'ine nga trabahuon',
        'para maiwasan',
        'damo nga salamat',
        'activity',
        'activities',
        'cause',
        'reason',
        'affected area',
        'affected areas',
        'power interruption',
        'emergency power interruption',
        'scheduled power interruption',
        'substations',
        'entire province',
        'briefly interrupted',
        'isolation',
        'normalization',
        'december 3',
        'december 4',
        'another 30 minutes',
        'between 5:00 pm',
        'between 6:00 pm',
        '7:00 am',
        '5:00 pm',
        '6:00 pm',
        'on december',
        'for the',
        'transmission line maintenance',
        'correction of defects',
        'vegetation clearing',
        'conductor payout',
        'transferring of secondary line',
        'removal of old wood pole',
        'distribution transformer',
        'construction of three phase',
        'distribution lines',
        'remove guy wire',
        'tap guy',
        'requested by',
        'municipal vice mayor',
        'as requested by',
        'management',
        'lgu',
        'magpuputol hn kahoy',
        'harani hit primary line'
    ]
    
    # Remove non-location phrases (case insensitive)
    for phrase in non_location_phrases:
        cleaned = re.sub(re.escape(phrase), '', cleaned, flags=re.IGNORECASE)
    
    # Remove extra whitespace and punctuation
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = re.sub(r'^[,.\s]+|[,.\s]+$', '', cleaned)

    # Split by common delimiters
    areas = re.split(r'[,&]|and|to', cleaned)

    # Clean up each area
    parsed_areas = []
    for area in areas:
        area = area.strip()
        # Remove common prefixes
        area = re.sub(r'^(Brgy\.?\s*|Barangay\s*|Brgy\s*\d+\s*,?\s*)', '', area, flags=re.IGNORECASE)
        area = re.sub(r'\s+', ' ', area).strip()

        # Filter out non-location text
        # Skip if it contains numbers only, is too short, or looks like a sentence
        if (area and 
            len(area) > 2 and 
            not re.match(r'^\d+$', area) and  # Not just numbers
            not re.search(r'\b(the|and|or|for|with|from|this|that|these|those|our|your|their|between|another|briefly|on|am|pm|december|january|february|march|april|may|june|july|august|september|october|november)\b', area, re.IGNORECASE) and  # No common words
            not area.lower().startswith(('we ', 'our ', 'your ', 'their ', '7:00 ', '5:00 ', '6:00 ', 'december ', 'another ', 'between ')) and  # No sentence starters
            not 'substation' in area.lower() and  # Remove substation references
            not 'province' in area.lower()):  # Remove province references
            parsed_areas.append(area)

    return parsed_areas

def find_best_match(area_name, barangay_list, threshold=95):
    """Find best fuzzy match for area_name in barangay list."""
    # First, check for exact municipality match
    for barangay in barangay_list:
        if fuzz.ratio(area_name, barangay['Municipality']) >= threshold:
            return barangay['Municipality'], 100  # Exact municipality match
    
    # Then check for barangay name match
    for barangay in barangay_list:
        if fuzz.ratio(area_name, barangay['Barangay']) >= threshold:
            return barangay['Full_Name'], fuzz.ratio(area_name, barangay['Barangay'])
    
    # Finally, check full name match
    for barangay in barangay_list:
        if fuzz.ratio(area_name, barangay['Full_Name']) >= threshold:
            return barangay['Full_Name'], fuzz.ratio(area_name, barangay['Full_Name'])
    
    return None, 0

def standardize_areas(semi_cleaned_data, barangay_list):
    """Standardize areas in semi_cleaned_data using barangay list."""
    standardized_data = []

    for post in semi_cleaned_data:
        standardized_post = post.copy()

        extracted_area = post.get('Affected Area(s)', '')
        parsed_areas = parse_areas(extracted_area)

        standardized_areas = []
        for area in parsed_areas:
            match, score = find_best_match(area, barangay_list)
            if match:
                standardized_areas.append(match)
            else:
                # Keep original if no good match
                standardized_areas.append(area)

        # Join standardized areas back
        if standardized_areas:
            standardized_post['Affected Area(s)'] = ', '.join(standardized_areas)
        else:
            standardized_post['Affected Area(s)'] = extracted_area

        standardized_data.append(standardized_post)

    return standardized_data

def clean_original_post(original_post):
    """Clean original post by removing newlines and extra spaces."""
    if not original_post:
        return ""
    
    # Replace newlines with spaces
    cleaned = original_post.replace('\n', ' ')
    
    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Strip leading/trailing whitespace
    cleaned = cleaned.strip()
    
    return cleaned

def extract_reason_activity(original_message):
    """Extract reason/activity from original message."""
    # Look for REASON, CAUSE, ACTIVITIES, ACTIVITY labels
    patterns = [
        r'(?:REASON|CAUSE)[:\s]+([^(\n]*?)(?:\n|AFFECTED|$)',
        r'(?:ACTIVITIES|ACTIVITY)[:\s]+\n?✅([^\n]+)',
        r'(?:ACTIVITIES|ACTIVITY)[:\s]+([^\n]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, original_message, re.IGNORECASE)
        if match:
            reason = match.group(1).strip()
            reason = re.sub(r'[✅☑]', '', reason).strip()
            if reason and len(reason) > 2:
                return reason
    
    return ""

def main():
    # File paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    semi_cleaned_path = os.path.join(project_root, 'data', 'silver', 'stage_1_filtered', 'semi_cleaned_data.json')
    barangay_list_path = os.path.join(project_root, 'data', 'list_barangay_e.samar', 'eastern_samar_barangays.json')
    output_path = os.path.join(project_root, 'data', 'silver', 'stage_3_standardized', 'standardized_outages.json')
    semi_final_path = os.path.join(project_root, 'data', 'silver', 'stage_3_standardized', 'semi_final.json')

    # Load data
    print("Loading semi-cleaned data...")
    semi_cleaned_data = load_json(semi_cleaned_path)

    print("Loading barangay list...")
    barangay_list = load_json(barangay_list_path)

    print(f"Processing {len(semi_cleaned_data)} posts...")

    # Standardize areas
    standardized_data = standardize_areas(semi_cleaned_data, barangay_list)

    # Save standardized data
    print("Saving standardized outages...")
    save_json(standardized_data, output_path)

    # Create semi-final format directly from semi_cleaned (no standardization)
    semi_final_data = []
    for post in semi_cleaned_data:
        original_message = post.get('original_message', '')
        
        # Apply cleaning functions to extract proper values
        clean_date = extract_clean_date(original_message, post.get('extracted_date', ''))
        clean_time = extract_clean_time(original_message, post.get('extracted_time', ''))
        clean_area = extract_clean_area(original_message, post.get('extracted_area', ''))
        clean_reason = extract_reason_activity(original_message)
        
        semi_final_entry = {
            "Date": clean_date,
            "Time": clean_time,
            "Affected Area(s)": clean_area,
            "Reason / Activity": clean_reason,
            "Original Post": clean_original_post(original_message)
        }
        semi_final_data.append(semi_final_entry)

    print("Saving semi-final data...")
    save_json(semi_final_data, semi_final_path)

    print("✅ Standardization completed successfully!")
    print(f"Processed {len(semi_cleaned_data)} posts")
    print(f"Output saved to: {output_path}")
    print(f"Semi-final saved to: {semi_final_path}")

if __name__ == "__main__":
    main()