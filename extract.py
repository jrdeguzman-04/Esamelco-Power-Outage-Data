

import pandas as pd
import requests
import json
import os

# Use environment variables for sensitive data
ACCESS_TOKEN = 'EAAW0omOwcTgBQLh6wpwjtXZAMWOjDTulBWDvxRDqc0mwlztL2bO5lYFtLw9019D3oLkg8IMqufrrABv1OGyZAVjaAG6Xfu7Xm3NZCIojLCH4vdJOCpKZAl5xW6ebK5kaC475skkoZCYaMCZCvwQ4hJJy95PLQmSGzNcGVyME2EVgP2GVkykDZBS5FbXRWZBzlPBoy83WohCK' 
FB_ID = '828975863643614'
URL = f'https://graph.facebook.com/v24.0/{FB_ID}/posts'

params = {
    'access_token': ACCESS_TOKEN,
    'fields': 'message,created_time,id',
    'limit': 100  # Request more posts per page
}

def fetch_posts():
    try:
        response = requests.get(URL, params=params)
        response.raise_for_status() # Automatically triggers HTTPError if status is 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

data = fetch_posts()

if data:
    posts = data.get('data', [])
    
    # Load last saved ID
    last_id = None
    if os.path.exists('latest_id.txt'):
        with open('latest_id.txt', 'r') as f:
            last_id = f.read().strip()

    current_posts = []
    for post in posts:
        if post['id'] == last_id:
            break
        current_posts.append(post)

    if current_posts:
        # Save new posts to JSON
        with open('raw_posts.json', 'a', encoding='utf-8') as f:
            json.dump(current_posts, f, ensure_ascii=False, indent=4)
            f.write('\n')
        
        # Update the checkpoint with the newest post ID
        with open("latest_id.txt", "w") as f:
            f.write(current_posts[0]['id'])
        
        # Display as DataFrame
        df = pd.DataFrame(current_posts)
        print(df)
        print(f"Successfully saved {len(current_posts)} new posts.")
    else:
        print("No new posts found.")