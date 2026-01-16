import requests

def fetch_posts():
    access_token = 'EAAW0omOwcTgBQLh6wpwjtXZAMWOjDTulBWDvxRDqc0mwlztL2bO5lYFtLw9019D3oLkg8IMqufrrABv1OGyZAVjaAG6Xfu7Xm3NZCIojLCH4vdJOCpKZAl5xW6ebK5kaC475skkoZCYaMCZCvwQ4hJJy95PLQmSGzNcGVyME2EVgP2GVkykDZBS5FbXRWZBzlPBoy83WohCK'
    fb_id = "828975863643614"

    url = f"https://graph.facebook.com/v24.0/{fb_id}/posts"
    params = {
        "access_token": access_token,
        "fields": "message,created_time,id"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # raise error if status code != 200
        data = response.json().get("data", [])  # get list of posts
        posts = []

        for item in data:
            post = {
                "id": item.get("id"),
                "message": item.get("message"),
                "created_time": item.get("created_time")
            }
            posts.append(post)

        return posts

    except requests.ConnectionError:
        print("Error: Could not connect to Facebook API.")
        return []
    except requests.Timeout:
        print("Error: Request timed out.")
        return []
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return []
    except requests.RequestException as e:
        print(f"Some error occurred: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

# Example usage
posts = fetch_posts()
for p in posts:
    print(p)
