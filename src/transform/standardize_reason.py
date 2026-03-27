import json
import os
import re

def standardize_reason(reason_text):
    """
    Map reason/activity text to one of 5 standardized categories.
    
    Categories:
    - Line Maintenance
    - Vegetation Clearing
    - Infrastructure Upgrade
    - Equipment Maintenance
    - Transmission Maintenance
    """
    
    if not reason_text:
        return "Line Maintenance"
    
    reason_lower = reason_text.lower()
    
    # Vegetation Clearing: tree cutting, line clearing, vegetation
    if any(keyword in reason_lower for keyword in ['tree cutting', 'line clear', 'vegetation', 'clearing']):
        return "Vegetation Clearing"
    
    # Equipment Maintenance: transformer, pole, removal
    if any(keyword in reason_lower for keyword in ['transformer', 'pole removal', 'remove pole', 'old wood pole', 'guy wire', 'tap guy']):
        return "Equipment Maintenance"
    
    # Infrastructure Upgrade: construction, distribution lines, upgrade
    if any(keyword in reason_lower for keyword in ['construction', 'distribution line', 'upgrade', 'installation']):
        return "Infrastructure Upgrade"
    
    # Transmission Maintenance: NGCP, substation, transmission line
    if any(keyword in reason_lower for keyword in ['ngcp', 'substation', 'transmission', 'conductor payout']):
        return "Transmission Maintenance"
    
    # Default: Line Maintenance
    return "Line Maintenance"

def main():
    input_path = 'data/gold/final.json'
    output_path = 'data/gold/final_1.json'
    
    # Read the final.json
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Process and standardize
    standardized_data = []
    for record in data:
        reason = record.get('Reason / Activity', '')
        standardized_reason = standardize_reason(reason)
        
        record['Reason / Activity'] = standardized_reason
        standardized_data.append(record)
    
    # Save to final_1.json
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(standardized_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Standardization complete!")
    print(f"✅ Processed {len(standardized_data)} records")
    print(f"✅ Saved to {output_path}")
    
    # Print summary
    reason_counts = {}
    for record in standardized_data:
        reason = record['Reason / Activity']
        reason_counts[reason] = reason_counts.get(reason, 0) + 1
    
    print("\nReason Distribution:")
    for reason, count in sorted(reason_counts.items()):
        print(f"  - {reason}: {count}")

if __name__ == "__main__":
    os.chdir('/Users/johnreydeguzman/Esamelco-Power-Outage-Data')
    main()
