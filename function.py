import jwt
import re
import requests
from config.env import SLACK_WEBHOOK, FUTURES_PLACE_ORDER_API, JWT_ISS_CODE, FUTURES_AUTHORIZATION_TOKEN, SLACK_ENABLED, BITCASTLE_ENABLE
from config.const import SOURCE_MAP


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
            "i ss": JWT_ISS_CODE,
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


def detect_parameters(text, source = None):
    detect = None
    full_signals = ""

    try:
        print(f"Detect Parameters: {source}")
        if source == "alwaystrade":
            if len(re.findall(".* SHORT", text)):
                detect = re.findall(".* SHORT", text)[0].split()

            if len(re.findall(".* LONG", text)):
                detect = re.findall(".* LONG", text)[0].split()

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
    
        # elif source == "zaykpremium":
        #     return None
        else:
            if (len(re.findall("#(.*) \(Binance\)", text))):
                coin = re.findall("#(.*) \(Binance\)", text)[0]
                pair = f"{coin}/USDT"
                currency = "USDT"
                full_signals = f"#{pair} \n"

            if (len(re.findall("Buy Between +\d+.\d+ - +\d+.\d+", text))):
                entry = re.findall("Buy Between +\d+.\d+ - +\d+.\d+", text)
                entry = re.findall("\d+.\d+ - +\d+.\d", entry[0])
                full_signals += f"Entry: {entry[0]} \n"

            if (len(re.findall("Targets +\d.* - +\d+.\d+", text))):
                targets = re.findall("Targets +\d.* - +\d+.\d+", text)
                target_price = re.findall("\d.* - +\d+.\d+", targets[0])[0].split(" - ")

                for index, price in enumerate(target_price):
                    index = index+1
                    full_signals += f"Target{index}: {price} \n"

            sl_price = find_price_in_text("Stop Loss", text)

            if sl_price is not None:
                full_signals += f"\nStopLoss: {sl_price}"

            if (len(re.findall("http[s]*\S+", text))):
                url = re.findall("http[s]*\S+", text)
                full_signals += f"\n{url[0]}"

            return {
                "coin": coin,
                "pair": pair,
                "currency": currency,
                "side": 1,
                "entry_price": 0,
                "price": 0,
                "full_signals": full_signals
            }

    except Exception as e:
        print(e)
        return None
    

def send_futures_order(payload):
    if BITCASTLE_ENABLE is False:
        return None
    
    order_payload = {
        "coin": payload["coin"],
        "currency": payload["currency"],
        "side": payload["side"],
        "type": 2,
        "mode": 1,
        "amount": str(round(1000 / float(payload["price"]), 2)),
        "price": payload["price"],
        "leverage": 20,
        "collateral": 1
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': FUTURES_AUTHORIZATION_TOKEN
    }

    try:
        response = requests.post(
            FUTURES_PLACE_ORDER_API,
            headers=headers,
            json=order_payload
        )
        if response.status_code == 200:
            print(f"Place Futures Order Success: {order_payload}")

        return order_payload
    except Exception as e:
        print(e)
        return None

# print(generate_token("41375"))