import requests
from config import crypto_cloud_token


url = "https://api.cryptocloud.plus/v2/invoice/merchant/info"
headers = {
    "Authorization": f"Token {crypto_cloud_token}"
}
data = {
    "uuids": ["INV-MN9K71PO"]
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    print("Success:", response.json())
else:
    print("Fail:", response.status_code, response.text)
