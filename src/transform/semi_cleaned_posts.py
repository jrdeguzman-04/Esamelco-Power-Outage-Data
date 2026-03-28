import re
import json

# 1. Load the JSON file
input_file = 'data/bronze/filtered_interruption data.json'
output_file = 'data/silver/stage_1_filtered/semi_cleaned_data.json'

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_post = json.load(f)
    print(f"Successfully loaded {len(raw_post)} posts.")
except FileNotFoundError:
    print(f"Error: File {input_file} not found. Please check the path.")
    raw_post = []


def clean_area_data(text):
    if not text: 
        return "Not Found"
    
    # Regex: Matches "Affected Area", "Areas", "Area", "Affected Areas"
    pattern = r"(?i)(?:affected\s+)?area(?:/s|s)?\s*[:\-]\s*(.*)"
    
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        raw_content = match.group(1)
        lines = raw_content.split('\n')
        collected_areas = []
        
        # Stop Words: Kung mag-start ang line dito, ibig sabihin tapos na ang listahan
        stop_words = ["reason", "activity", "activities", "note", "pahinumdum", "we're sorry", "esamelco", "contact", "date", "time"]

        for line in lines:
            line = line.strip()
            if not line: continue
                
            # Check stop words
            clean_check = line.lower().replace(':', '')
            if any(clean_check.startswith(sw) for sw in stop_words):
                break
            
            collected_areas.append(line)
        
        return ", ".join(collected_areas) if collected_areas else "Not Found"
    
    return "Not Found"

# --- FUNCTION 2: EXTRACT DATE AND TIME ---
def extract_schedule(text):
    if not text: return {"date": "Not Found", "time": "Not Found"}

    # --- DATE ---
    date_found = "Not Found"
    # Strategy A: Labels (Date:, When:, Schedule:)
    label_date = re.search(r"(?i)(?:date|when|schedule)\s*[:\-]?\s*\n?[:\-]?\s*([^\n]+)", text)
    if label_date:
        raw_date = label_date.group(1).strip()
        date_found = re.sub(r'^[^\w\d]+', '', raw_date) # Remove emojis
    else:
        # Strategy B: Narrative (e.g., December 19, 2025)
        date_pattern = r"(?i)(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?,?(?:\s+\d{4})?"
        match = re.search(date_pattern, text)
        if match:
            date_found = match.group(0)

    # --- TIME ---
    time_found = []
    # Strategy A: Label (Time:)
    label_time = re.search(r"(?i)^time\s*[:\-]\s*(.*)", text, re.MULTILINE)
    if label_time:
        time_found.append(label_time.group(1).strip())
    
    # Strategy B: Ranges (e.g., 9am - 5pm) regardless of label
    # Note: Added logic to avoid duplicates if Strategy A already found it
    time_pattern = r"(?i)(\d{1,2}(?::\d{2})?\s*(?:am|pm|nn|noon)\s*(?:-|–|to)\s*\d{1,2}(?::\d{2})?\s*(?:am|pm|nn|noon))"
    matches = re.findall(time_pattern, text)
    if matches:
        for m in matches:
            if m not in time_found: # Avoid duplicates
                time_found.append(m)

    final_time = ", ".join(time_found) if time_found else "Not Found"
    
    return {
        "date": date_found,
        "time": final_time
    }

# --- MAIN PROCESS ---
processed_data = []

print("Processing posts...")

for post in raw_post:
    # Handle cases where 'message' key might be missing
    msg_text = post.get('message', '')
    
    # 1. Get Area
    area = clean_area_data(msg_text)
    
    # 2. Get Schedule (Date/Time)
    schedule = extract_schedule(msg_text)
    
    # 3. Compile Data
    extracted_info = {
        "id": post.get('id'),
        "created_time": post.get('created_time'),
        "original_message": msg_text,
        "extracted_date": schedule['date'],
        "extracted_time": schedule['time'],
        "extracted_area": area
    }
    
    processed_data.append(extracted_info)
    
    # Optional: Print results sa console para makita mo habang nagru-run
    # print(f"ID: {extracted_info['id']} | Area: {area} | Date: {schedule['date']}")

# --- SAVE TO FILE ---
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(processed_data, f, ensure_ascii=False, indent=4)

print(f"\nDone! Processed {len(processed_data)} posts.")
print(f"Results saved to: {output_file}")