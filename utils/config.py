import os
from dotenv import load_dotenv

load_dotenv("files/envs/.env")

TOKEN = os.getenv("TOKEN")
api_key = os.getenv('api_key')
crypto_cloud_token = os.getenv('crypto_cloud_token')
shop_id = os.getenv('shop_id')

# MongoDB
db_username = os.getenv('db_username')
db_password = os.getenv('db_password')
db_auth_source = os.getenv('db_auth_source')
