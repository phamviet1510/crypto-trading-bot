import jwt
import re
import requests
from config.env import SLACK_WEBHOOK, FUTURES_PLACE_ORDER_API, JWT_ISS_CODE, FUTURES_AUTHORIZATION_TOKEN, SLACK_ENABLED


def send_slack_msg(message):
    if SLACK_ENABLED:
        try:
            requests.post(SLACK_WEBHOOK, json={
                "text": message,
            })

        except Exception as ex:
            print(f"Error: {ex}")
        

def generate_token(user_id):
    private_key = open('./private-stg-key.txt', 'r').read()
    public_key = open('./public-key.txt', 'r').read()

    return jwt.encode(
        {
            "iss": JWT_ISS_CODE,
            "app_id": 1,
            "device": f"device_{user_id}",
            "uid": user_id,
            "scopes": "all",
            "iat": 1659493427,
            "exp": 1703341069
        },
        private_key,
        algorithm="RS256"
    )


def find_price_in_text(search, txt):
    text = re.findall(f"{search} +\d+.\d+", txt)

    if text[0] is None:
        return None

    num_detect = re.findall("\d+.\d+", text[0])

    return num_detect[0]


def detect_parameters(text):
    detect = None

    try:
        if len(re.findall(".* SHORT", text)):
            detect = re.findall(".* SHORT", text)[0].split()

        if len(re.findall(".* LONG", text)):
            detect = re.findall(".* LONG", text)[0].split()

        if detect is None:
            return None

        pair = re.sub("#", "", detect[0])
        coin = pair.split('/')[0]
        currency = pair.split('/')[1]
        side = 1 if detect[1] == "LONG" else 2
        return {
            "pair": pair,
            "coin": coin.lower(),
            "currency": currency.lower(),
            "side": side,
            "price": find_price_in_text("Entries", text)
        }

    except Exception as e:
        print(e)
        return None
    

def send_futures_order(payload):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': FUTURES_AUTHORIZATION_TOKEN
    }

    try:
        response = requests.post(
            FUTURES_PLACE_ORDER_API,
            headers=headers,
            json=payload
        )
        if response.status_code == 200:
            print(f"Place Futures Order Success: {payload}")

        return payload
    except Exception as e:
        print(e)
        return None

# print(generate_token("41375"))