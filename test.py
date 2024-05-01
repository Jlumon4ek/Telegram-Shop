import requests


crypto_cloud_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1dWlkIjoiTWpBME16ST0iLCJ0eXBlIjoicHJvamVjdCIsInYiOiI2ZTY2MTdiZTA3MDI0NDJkYWZjZTIzM2JiYWNlNjcyOTQwYjRhNzNmZTYyMmZlM2YzYWM5Njg5MzgzNzhlNjg0IiwiZXhwIjo4ODExMjY5OTg5NH0.7e5Zxi5MdTQQjzxqxVq1czHkUYgVf2eYdrxqnQ_1iAM'

url = "https://api.cryptocloud.plus/v2/invoice/merchant/info"
headers = {
    "Authorization": f"Token {crypto_cloud_token}"
}
data = {
    "uuids": ["INV-1FN7D5DB"]
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    print("Success:", response.json())
else:
    print("Fail:", response.status_code, response.text)
