#!/usr/bin/env python3
from pyrogram import Client
from pyrogram import filters
import os
import json
import requests
from function import find_price_in_text, detect_parameters, send_futures_order, send_slack_msg
from config.env import TELEGRAM_ACCOUNT, PHONE_NR, API_ID, API_HASH


app = Client(
    TELEGRAM_ACCOUNT,
    phone_number=PHONE_NR,
    api_id=API_ID,
    api_hash=API_HASH
)


# filters.chat(SOURCE_CHAT)
# -1001756782614 - Alway Win Trade FREE
# -1001639229723 - ZKReceiver
# -1001686155182 ZK(Premium)
@app.on_message(
    (filters.regex("Binance Futures")
     | filters.regex("Kucoin Futures")
     | filters.regex("OKX Futures")
     | filters.regex("ByBit USDT")
     | filters.regex("Take-Profit target")
     | filters.regex("All entry targets achieved")
     | filters.regex("All take-profit targets achieved")
     | filters.regex("Closed at trailing stoploss after reaching take profit")
     | filters.regex("LONG ✳️")
     | filters.regex("SHORT 🛑")
     | filters.regex("Stoploss ⛔")
     | filters.regex("Enjoy ur profits")
     )
    # & (filters.chat(-1001756782614) | filters.chat(-1001639229723))
)

def my_handler(client, message):
    msg_id = None
    payload = detect_parameters(message.text)

    if message.chat.title == 'ZAYK (Premium)':
        print(f"Message from {message.chat.title} id {message.chat.id}: {message.text}")


    if payload is not None and message.chat.id == -1001756782614:
        msg_id = message.id
        data = {
            "id": message.id,
            "text": message.text
        }
        with open(f"signals/signal_{msg_id}.json", "w") as outfile:
            json.dump(data, outfile)

        print(f"payload: {payload}")

        if payload is not None:
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

            res = send_futures_order(order_payload)

            # print(res)
            
            #receive res order id & find position
            #769143012352856749

            send_slack_msg(message.text)

    if message.reply_to_message_id is not None:
        msg_id = message.reply_to_message_id
        try:
            f_content = open(f"./signals/signal_{msg_id}.json", "r")
            send_slack_msg(message.text)
        except:
            print("An exception occurred")


app.run()
