import json
import re

def filter_interruption():
    try:
        with open(
            "data/bronze/try_posts.json","r",encoding="utf-8") as f:
            data = json.load(f)

    except FileNotFoundError:
        print("File not found")
        return
    except json.JSONDecodeError:
        print("Invalid JSON file")
        return

    matches = []

    for post in data:
        text = post.get("message", "")
        if re.search("INTERRUPTION", text, re.IGNORECASE):
            matches.append(post)

    if matches:
        try:
            with open("data/bronze/filtered data.json", "w", encoding="utf-8") as f:
                json.dump(matches, f, indent=4, ensure_ascii=False)
            print("File successfully added")

        except Exception as e:
            print(f"Error saving file: {e}")
    else:
        print("No matching posts found")
if __name__=="__main__":
    filter_interruption()