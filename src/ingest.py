import requests
from dotenv import load_dotenv
import os

load_dotenv()
access_token = os.getenv("ACCESS_TOKEN")
fb_id = os.getenv("FB_ID")
def fetch_posts():
    

    print(access_token)
    print(fb_id)
    
    url = f"https://graph.facebook.com/v24.0/{fb_id}/posts"
    params = {
        "access_token": access_token,
        "fields": "id,message,created_time",
        "limit": 25
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        raw_data = response.json().get("data", [])
        clean_posts = []

        for post in raw_data:
           
            if 'message' in post and post['message'].strip():
                clean_posts.append({
                    "id": post.get("id"),
                    "created_time": post.get("created_time"),
                    "message": post.get("message", "")
                })

        return clean_posts

    except requests.exceptions.RequestException as e:
        print(f"Error fetching posts: {e}")
        return []
    
if __name__=="__main__":
    fetch_posts()