import requests
from dotenv import load_dotenv
import os

load_dotenv()
access_token = os.getenv("ACCESS_TOKEN")
fb_id = os.getenv("FB_ID")

print(access_token)