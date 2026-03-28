import json
import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'database': 'power_data',
    'user': 'postgres',
    'port': 5432,
    'password': '123'
}

# Read the JSON file
with open('data/gold/final_1_cleaned.json', 'r', encoding='utf-8') as f:
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
            cur.execute(insert_query, (
                record.get('Date'),
                record.get('Time'),
                record.get('Reason / Activity'),
                record.get('Original Post'),
                record.get('Affected Area(s)'),
                record.get('Date')
            ))
        
        conn.commit()
        print(f"✅ Loaded {len(data)} records from final_1_cleaned.json")
        
        # Display all records
        cur.execute("""
            SELECT id, date, time, affected_areas, reason_activity 
            FROM power_outages 
            ORDER BY date_parsed DESC, time DESC
        """)
        
        results = cur.fetchall()
        print(f"\n📊 Database Content (Total: {len(results)} records):")
        print("-" * 130)
        for i, row in enumerate(results, 1):
            print(f"{i:2d}. Date: {row[1]:20s} | Time: {row[2]:20s} | Area: {row[3]:35s} | Activity: {row[4]}")
        print("-" * 130)

except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
finally:
    conn.close()
