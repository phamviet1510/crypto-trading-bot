import os
from dotenv import load_dotenv

load_dotenv(verbose=True, override=True)

# https://my.telegram.org/auth?to=apps
API_ID=os.getenv('API_ID')
API_HASH=os.getenv('API_HASH')

# TELEGRAM EVN
SOURCE_CHAT=os.getenv('SOURCE_CHAT')
TARGET_CHAT=os.getenv('TARGET_CHAT')
TELEGRAM_ACCOUNT=os.getenv('TELEGRAM_ACCOUNT')
PHONE_NR=os.getenv('PHONE_NR')

#SLACK 
SLACK_WEBHOOK=os.getenv('SLACK_WEBHOOK', 0)
JWT_ISS_CODE=os.getenv("JWT_ISS_CODE")
SLACK_ENABLED=os.getenv("SLACK_ENABLED")

#Exchange Integrate
BITCASLE_ENDPOINT=os.getenv("BITCASLE_ENDPOINT", "")
FUTURES_PLACE_ORDER_API=os.getenv('FUTURES_PLACE_ORDER_API')
FUTURES_AUTHORIZATION_TOKEN=os.getenv("FUTURES_AUTHORIZATION_TOKEN")
