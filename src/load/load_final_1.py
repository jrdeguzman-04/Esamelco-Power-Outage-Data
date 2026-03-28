import json
import psycopg2
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'database': 'power_data',
    'user': 'postgres',
    'port': 5432,
    'password': '123'
}

# Read the original JSON file with all data intact
with open('data/gold/final_1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Connect to database
conn = psycopg2.connect(**DB_CONFIG)

try:
    with conn.cursor() as cur:
        # Delete all old records
        cur.execute("DELETE FROM power_outages")
        print(f"✓ Cleared old records")
        
        # Insert all records from JSON
        insert_query = """
        INSERT INTO power_outages (date, time, reason_activity, original_post, affected_areas, date_parsed)
        VALUES (%s, %s, %s, %s, %s, TO_DATE(%s, 'Month DD, YYYY'))
        """
        
        for record in data:
            # Format date if needed
            date_str = record.get('Date', '')
            # Normalize date format
            if date_str.endswith('.'):
                date_str = date_str[:-1]
            if '-' in date_str and 'December' in date_str:
                # Handle "December 3-4, 2025" -> use first date
                date_str = date_str.replace('December 3-4,', 'December 3,')
            
            cur.execute(insert_query, (
                date_str,
                record.get('Time', ''),
                record.get('Reason / Activity', ''),
                record.get('Original Post', ''),
                record.get('Affected Area(s)', ''),
                date_str
            ))
        
        conn.commit()
        print(f"✅ Loaded {len(data)} records from final_1.json")
        
        # Display all records ordered by date descending
        cur.execute("""
            SELECT id, date, time, affected_areas, reason_activity 
            FROM power_outages 
            ORDER BY date_parsed DESC, time DESC
        """)
        
        results = cur.fetchall()
        print(f"\n📊 Database Content (Total: {len(results)} records):")
        print("-" * 140)
        for i, row in enumerate(results, 1):
            print(f"{i:2d}. Date: {row[1]:20s} | Time: {row[2]:20s} | Area: {row[3]:50s} | Activity: {row[4]}")
        print("-" * 140)

except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
    import traceback
    traceback.print_exc()
finally:
    conn.close()
