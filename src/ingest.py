import requests

def fetch_posts():
    # Replace with your valid Access Token
    access_token = "EAAW0omOwcTgBQLh6wpwjtXZAMWOjDTulBWDvxRDqc0mwlztL2bO5lYFtLw9019D3oLkg8IMqufrrABv1OGyZAVjaAG6Xfu7Xm3NZCIojLCH4vdJOCpKZAl5xW6ebK5kaC475skkoZCYaMCZCvwQ4hJJy95PLQmSGzNcGVyME2EVgP2GVkykDZBS5FbXRWZBzlPBoy83WohCK"
    fb_id = "828975863643614"

    url = f"https://graph.facebook.com/v24.0/{fb_id}/posts"
    params = {
        "access_token": access_token,
        "fields": "id,message,created_time",
        "limit": 25
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Raises an error for 400/500 status codes
        
        raw_data = response.json().get("data", [])
        clean_posts = []

        for post in raw_data:
            # Only keep posts that actually have a message (removes image-only posts)
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