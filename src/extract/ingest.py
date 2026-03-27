import requests
from dotenv import load_dotenv
import os

load_dotenv()
access_token = os.getenv("ACCESS_TOKEN")
fb_id = os.getenv("FB_ID")
def fetch_posts():
    print(f"Fetching posts for FB_ID: {fb_id}")
    print(f"Access token available: {bool(access_token)}")
    
    url = f"https://graph.facebook.com/v24.0/{fb_id}/posts"
    params = {
        "access_token": access_token,
        "fields": "id,message,created_time",
        "limit": 25
    }

    try:
        print(f"Making API call to: {url}")
        response = requests.get(url, params=params)
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"API Error: {response.text}")
            return []
        
        raw_data = response.json().get("data", [])
        print(f"Retrieved {len(raw_data)} posts from API")
        
        clean_posts = []

        for post in raw_data:
            if 'message' in post and post['message'].strip():
                clean_posts.append({
                    "id": post.get("id"),
                    "created_time": post.get("created_time"),
                    "message": post.get("message", "")
                })

        print(f"Filtered to {len(clean_posts)} posts with messages")
        return clean_posts

    except requests.exceptions.RequestException as e:
        print(f"Error fetching posts: {e}")
        return []
    
if __name__=="__main__":
    fetch_posts()