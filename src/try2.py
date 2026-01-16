
import requests


access_token = 'EAAW0omOwcTgBQLh6wpwjtXZAMWOjDTulBWDvxRDqc0mwlztL2bO5lYFtLw9019D3oLkg8IMqufrrABv1OGyZAVjaAG6Xfu7Xm3NZCIojLCH4vdJOCpKZAl5xW6ebK5kaC475skkoZCYaMCZCvwQ4hJJy95PLQmSGzNcGVyME2EVgP2GVkykDZBS5FbXRWZBzlPBoy83WohCK'
fb_id = "828975863643614"

url = f"https://graph.facebook.com/v24.0/{fb_id}/posts"

param = {
    'access_token':access_token,
    'fields':'messages,created_time,id'
}
try:
    response = requests.get(url,params = param)
    data = response.json()
    print(data)
except requests.ConnectionError:
    print('Error')
