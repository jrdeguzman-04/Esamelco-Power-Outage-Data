import json
import psycopg2
import sys
import os
from pathlib import Path

# PostgreSQL connection details (can be overridden by environment variables)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'power_data'),
    'user': os.getenv('DB_USER', 'postgres'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'password': os.getenv('DB_PASSWORD', '123')
}

def create_table(conn):
    """Create the power_outages table if it doesn't exist"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS power_outages (
        id SERIAL PRIMARY KEY,
        date VARCHAR(50) NOT NULL,
        time TEXT NOT NULL,
        reason_activity TEXT NOT NULL,
        original_post TEXT,
        affected_areas TEXT NOT NULL,
        date_parsed DATE
    )
    """
    
    create_index_query = """
    CREATE INDEX IF NOT EXISTS idx_date_parsed ON power_outages(date_parsed DESC)
    """
    
    try:
        with conn.cursor() as cur:
            cur.execute(create_table_query)
            cur.execute(create_index_query)
            conn.commit()
            print("✓ Table 'power_outages' created or already exists")
    except Exception as e:
        print(f"✗ Error creating table: {e}")
        conn.rollback()
        raise

def load_json_to_db(conn, json_file_path):
    """Load data from JSON file to PostgreSQL"""
    try:
        # Verify file exists
        if not Path(json_file_path).exists():
            raise FileNotFoundError(f"JSON file not found: {json_file_path}")
        
        # Read the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ Loaded {len(data)} records from: {json_file_path}")
        
        # Insert data into the database
        insert_query = """
        INSERT INTO power_outages (date, time, reason_activity, original_post, affected_areas, date_parsed)
        VALUES (%s, %s, %s, %s, %s, TO_DATE(%s, 'Month DD, YYYY'))
        """
        
        with conn.cursor() as cur:
            for record in data:
                date_val = record.get('Date')
                cur.execute(insert_query, (
                    date_val,
                    record.get('Time'),
                    record.get('Reason / Activity'),
                    record.get('Original Post'),
                    record.get('Affected Area(s)'),
                    date_val
                ))
            
            conn.commit()
            print(f"✓ Successfully inserted {len(data)} records into the database")
    
    except FileNotFoundError as e:
        print(f"✗ {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON file: {e}")
        raise
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        conn.rollback()
        raise

def get_json_path():
    """Get JSON file path from command line argument or use default"""
    if len(sys.argv) > 1:
        return sys.argv[1]
    raise ValueError(
        "Usage: python load.py <path_to_json_file>\n"
        "Example: python load.py ./data/gold/final_1_cleaned.json"
    )

def display_sorted_data(conn):
    """Display data sorted by date (latest to oldest)"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, date, time, affected_areas, reason_activity, date_parsed
                FROM power_outages 
                ORDER BY date_parsed DESC NULLS LAST, time DESC
            """)
            results = cur.fetchall()
            print("\n📊 All Power Outages (Latest to Oldest):")
            print("-" * 120)
            for row in results:
                parsed_date = row[5] if row[5] else "PARSE ERROR"
                print(f"  ID: {row[0]:2d} | Date: {row[1]:20s} | Parsed: {str(parsed_date):12s} | Time: {row[2]:20s} | Area: {row[3]}")
            print("-" * 120)
    except Exception as e:
        print(f"✗ Error retrieving sorted data: {e}")

def main():
    """Main function to orchestrate the data loading process"""
    conn = None
    try:
        # Get JSON file path
        json_file_path = get_json_path()
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        print("✓ Connected to PostgreSQL successfully")
        print(f"  Host: {DB_CONFIG['host']}, Database: {DB_CONFIG['database']}")
        
        # Create table
        create_table(conn)
        
        # Load data from JSON
        load_json_to_db(conn, json_file_path)
        
        # Display sorted data
        display_sorted_data(conn)
        
        print("\n✓ Data loading completed successfully!")
        
    except psycopg2.Error as e:
        print(f"✗ Database error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"✗ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()
            print("✓ Database connection closed")

if __name__ == '__main__':
    main()
