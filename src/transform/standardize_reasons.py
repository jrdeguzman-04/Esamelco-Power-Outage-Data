import json
import re
import os

os.chdir('/Users/johnreydeguzman/Esamelco-Power-Outage-Data')

def standardize_reason(reason):
    """Map reason/activity to one of 5 standard categories"""
    reason_lower = reason.lower()
    
    # Transmission Maintenance patterns - check first (most specific)
    if any(pattern in reason_lower for pattern in ['transmission', 'substation', 'ngcp']):
        return "Transmission Maintenance"
    
    # Infrastructure Upgrade patterns
    if any(pattern in reason_lower for pattern in ['construction', 'three phase distribution', 'distribution lines']):
        return "Infrastructure Upgrade"
    
    # Equipment Maintenance patterns
    if any(pattern in reason_lower for pattern in ['transformer', 'pole', 'conductor', 'removal', 'guy wire', 'payout']):
        return "Equipment Maintenance"
    
    # Vegetation Clearing patterns
    if any(pattern in reason_lower for pattern in ['tree cutting', 'line clearing', 'vegetation clearing', 'line clear', 'kahoy', 'cutting']):
        return "Vegetation Clearing"
    
    # Default
    return "Line Maintenance"

# Load final.json
with open('data/silver/stage_4_final/final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Standardize all reasons
for record in data:
    original_reason = record.get('Reason / Activity', '')
    standardized = standardize_reason(original_reason)
    record['Reason / Activity'] = standardized

# Save back
with open('data/silver/stage_4_final/final.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Display the mapping
print("✅ Standardization complete!")
print("\nStandardized reasons:")
mapping = {}
for record in data:
    reason = record['Reason / Activity']
    if reason not in mapping:
        mapping[reason] = 0
    mapping[reason] += 1

for category, count in sorted(mapping.items()):
    print(f"  {category}: {count} records")
