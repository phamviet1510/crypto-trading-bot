#!/usr/bin/env python3
from pyrogram import Client
from pyrogram import filters
import os
import sys
import json
from function import detect_parameters, send_futures_order, send_slack_msg
from config.env import TELEGRAM_ACCOUNT, PHONE_NR, API_ID, API_HASH
from config.const import SOURCE_MAP


app = Client(
    TELEGRAM_ACCOUNT,
    phone_number=PHONE_NR,
    api_id=API_ID,
    api_hash=API_HASH
)


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
     | filters.regex("(Binance)")
     )
    & (filters.chat(-1001756782614) | filters.chat(-1001639229723) | filters.chat(-1001686155182))
)


def my_handler(client, message):
    msg_id = None
    print(f"Message from {message.chat.title} id {message.chat.id}: {message.text}")

    if SOURCE_MAP[message.chat.id] is None:
        print("Skip follow signals")
    
    print(f"Message from {message.chat.title} id {message.chat.id}: {message.text}")
    payload = detect_parameters(message.text, SOURCE_MAP[message.chat.id])

    if message.reply_to_message_id is not None:
        msg_id = message.reply_to_message_id
        try:
            f_content = open(f"./signals/signal_{message.chat.id}_{msg_id}.json", "r")
            send_slack_msg(message.text)
        except:
            print("An exception occurred")

        return "Done"
            

    if payload is not None:
        msg_id = message.id
        data = {
            "id": message.id,
            "text": message.text
        }
        with open(f"signals/signal_{message.chat.id}_{msg_id}.json", "w") as outfile:
            json.dump(data, outfile)

        print(f"payload: {payload}")

        if payload is not None:
            res = send_futures_order(payload)
            
            #receive res order id & find position
            #769143012352856749
            if SOURCE_MAP[message.chat.id] == "alwaystrade":
                send_slack_msg(message.text)
            else:
                send_slack_msg(payload['full_signals'])

        return "Done"
    

app.run()
