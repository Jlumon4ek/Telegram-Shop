import os
from dotenv import load_dotenv

load_dotenv("files/envs/.env.dev")

TOKEN = os.getenv("TOKEN")
crypto_cloud_token = os.getenv('crypto_cloud_token')
shop_id = os.getenv('shop_id')

# MongoDB
db_link = os.getenv("db_link")
