import json
import os
import re

def load_semi_cleaned_data():
    """Load semi-cleaned data dynamically from file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    semi_cleaned_path = os.path.join(project_root, 'data', 'silver', 'semi_cleaned_data.json')
    
    try:
        with open(semi_cleaned_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {semi_cleaned_path} not found. Using empty list.")
        return []

def extract_reason_activity(original_message):
    """Extract reason/activity from original message."""
    patterns = [
        r'(?:Reason|CAUSE|Activity|ACTIVITIES)[:\s]+([^\n]+?)(?:\n|$)',
        r'✅(.+?)(?:\n|$)',
    ]
    
    reasons = []
    for pattern in patterns:
        matches = re.findall(pattern, original_message, re.IGNORECASE | re.DOTALL)
        for match in matches:
            reason = match.strip()
            reason = re.sub(r'[^\w\s\-\.\,]', '', reason).strip()
            if reason and len(reason) > 3:
                reasons.append(reason)
    
    return ' | '.join(set(reasons)) if reasons else "Not specified"

def clean_posts(semi_cleaned_data):
    """Transform semi-cleaned data into cleaned format."""
    cleaned_data = []
    
    for post in semi_cleaned_data:
        # Handle both old and new key structures
        date = post.get('Date') or post.get('extracted_date', '')
        time = post.get('Time') or post.get('extracted_time', '')
        area = post.get('Affected Area(s)') or post.get('extracted_area', '')
        reason_activity = post.get('Reason / Activity') or extract_reason_activity(post.get('original_message', ''))
        original_post = post.get('Original Post') or post.get('original_message', '')
        
        cleaned_entry = {
            "Date": date,
            "Time": time,
            "Affected Area(s)": area,
            "Reason / Activity": reason_activity,
            "Original Post": original_post
        }
        cleaned_data.append(cleaned_entry)
    
    return cleaned_data

def main():
    # Load semi-cleaned data dynamically
    print("Loading semi-cleaned data...")
    semi_cleaned_data = load_semi_cleaned_data()
    
    if not semi_cleaned_data:
        print("No data to process.")
        return
    
    print(f"Processing {len(semi_cleaned_data)} posts...")
    
    # Transform to cleaned format
    cleaned_data = clean_posts(semi_cleaned_data)
    
    # Save to gold folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    output_path = os.path.join(project_root, 'data', 'gold', 'cleaned_data.json')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Cleaned data saved to {output_path}")
    print(f"Processed {len(cleaned_data)} posts")

if __name__ == "__main__":
    main()