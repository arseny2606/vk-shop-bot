import uuid
import datetime
import aiohttp
from config import qiwi_token


async def create_payment(money, comment):
    billid = uuid.uuid4()
    time = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S+03:00")
    URL = f"https://api.qiwi.com/partner/bill/v1/bills/{billid}"
    HEADERS = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {qiwi_token}'
    }
    DATA = {"amount": {"currency": "RUB", "value": money}, "comment": comment,
            "expirationDateTime": time, "customer": {}, "customFields": {"themeCode": "Oksana-KatAxJID99"}}
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.put(URL, json=DATA) as resp:
            response = await resp.json()
    return response


async def check_payment(billId):
    URL = f"https://api.qiwi.com/partner/bill/v1/bills/{billId}"
    HEADERS = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {qiwi_token}'
    }
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(URL) as resp:
            response = await resp.json()
    return response
