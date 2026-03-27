import json
import os
from ingest import fetch_posts

# This is where your master list of posts will live
JSON_FILE_PATH = "data/bronze/raw_posts.json"

def run_pipeline():
    print("Connecting to Facebook...")
    new_posts = fetch_posts()
    
    if not new_posts:
        print("No data received.")
        return

    # 1. Load existing data if the file exists
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            try:
                existing_posts = json.load(f)
            except json.JSONDecodeError:
                existing_posts = []
    else:
        existing_posts = []

    # 2. Create a set of IDs we already have to prevent duplicates
    existing_ids = {post['id'] for post in existing_posts}

    # 3. Filter only the brand new posts
    added_count = 0
    updated_list = existing_posts
    
    for post in new_posts:
        if post['id'] not in existing_ids:
            # Add new post to the TOP of the list
            updated_list.insert(0, post)
            added_count += 1

    # 4. Save back to the JSON file
    if added_count > 0:
        # Create folder if it doesn't exist
        os.makedirs(os.path.dirname(JSON_FILE_PATH), exist_ok=True)
        
        with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(updated_list, f, indent=4, ensure_ascii=False)
        print(f"Done! Added {added_count} new posts.")
    else:
        print("Everything is already up to date. No new posts to add.")

if __name__ == "__main__":
    run_pipeline()