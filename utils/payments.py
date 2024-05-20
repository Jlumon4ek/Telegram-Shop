import asyncio
import aiohttp
from datetime import datetime
from .config import crypto_cloud_token, shop_id
from db.mongo_db import update_user_balance, record_balance_history


async def create_invoice(amount):
    print("[INFO] Creating invoice")
    url = "https://api.cryptocloud.plus/v2/invoice/create"
    headers = {
        "Authorization": f"Token {crypto_cloud_token}"
    }

    data = {
        "shop_id": f"{shop_id}",
        "amount": str(amount),
        "currency": "USD",
    }

    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                data = await response.json()
                uuid = data['result']['uuid']
                link = data['result']['link']
                print("[INFO] Invoice created")
                return uuid, link
            else:
                return None, None


async def invoice_cancel(uuid):
    url = "https://api.cryptocloud.plus/v2/invoice/merchant/canceled"
    headers = {
        "Authorization": f"Token {crypto_cloud_token}"
    }
    data = {
        "uuid": f"{uuid}"
    }

    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.post(url, headers=headers, json=data, verify_ssl=False) as response:
            if response.status == 200:
                return "Success:", await response.json()
            else:
                return "Fail:", await response.text()


async def check_payment_status(mongo, uuid, user_id, username, fullname, bot, attempt=0):
    while attempt < 20:
        url = "https://api.cryptocloud.plus/v2/invoice/merchant/info"
        headers = {
            "Authorization": f"Token {crypto_cloud_token}"
        }
        data = {
            "uuids": [f"{uuid}"]
        }

        invoice_status = None
        received_usd = 0

        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(url, headers=headers, json=data, verify_ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    invoice = data['result'][0]
                    invoice_status = invoice['invoice_status']
                    received_usd = invoice.get('amount_paid_usd')

        if invoice_status == "success" and received_usd > 0:
            try:
                await record_balance_history(mongo, user_id, received_usd, username, fullname, uuid[4:])
            except Exception as e:
                print(
                    f"[ERROR] An error occurred while recording the balance history: {e}. [USER INFO]: {user_id}, {username}, {fullname}")
                await bot.send_message(user_id, "An error occurred while processing the payment. Please contact the administrator.")
                break

            await update_user_balance(mongo, user_id, received_usd)
            await bot.send_message(
                user_id,
                f"The payment was successfully processed. Your balance has been replenished by {
                    received_usd}$"
            )

            break
        else:
            print(
                f"[INFO] Payment status: {invoice_status}, Received USD: {received_usd}. Attempt: {attempt + 1}")
            await asyncio.sleep(60)
        attempt += 1
