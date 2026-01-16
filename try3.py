import barangay
import json

# PSGC code for Region 8 (Eastern Visayas)
REGION8_PSGC = '0800000000'

# Step 1: Filter Region 8 itself (just for verification)
region8 = [r for r in barangay.BARANGAY_FLAT if r['type'] == 'region' and r['psgc_id'] == REGION8_PSGC]
print("Region 8:", region8[0]['name'] if region8 else "Not found")

# Step 2: Filter provinces in Region 8
provinces = [p for p in barangay.BARANGAY_FLAT if p['type'] == 'province' and p['parent_psgc_id'] == REGION8_PSGC]

region8_data = []  # This will store the final hierarchical data

for prov in provinces:
    prov_dict = {
        'province_name': prov['name'],
        'province_psgc': prov['psgc_id'],
        'municipalities': []
    }
    
    # Step 3: Filter municipalities in this province
    municipalities = [m for m in barangay.BARANGAY_FLAT 
                      if m['type'] == 'municipality' and m['parent_psgc_id'] == prov['psgc_id']]
    
    for m in municipalities:
        mun_dict = {
            'municipality_name': m['name'],
            'municipality_psgc': m['psgc_id'],
            'barangays': []
        }
        
        # Step 4: Filter barangays in this municipality
        barangays = [b for b in barangay.BARANGAY_FLAT 
                     if b['type'] == 'barangay' and b['parent_psgc_id'] == m['psgc_id']]
        
        for b in barangays:
            mun_dict['barangays'].append({
                'barangay_name': b['name'],
                'barangay_psgc': b['psgc_id']
            })
        
        prov_dict['municipalities'].append(mun_dict)
    
    region8_data.append(prov_dict)

# Step 5: Save hierarchical data to JSON
with open('region8_data.json', 'w', encoding='utf-8') as f:
    json.dump(region8_data, f, ensure_ascii=False, indent=4)

print("Saved Region 8 data to 'region8_data.json'")
