import os
from tweepy import OAuthHandler, API
from dotenv import load_dotenv

# 환경변수 load
load_dotenv()

# 환경변수
consumer_key = os.getenv('consumer_key')
consumer_secret = os.getenv('consumer_secret')
access_token = os.getenv('access_token')
access_token_secret = os.getenv('access_token_secret')


# Tweepy 연결
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = API(auth)

# 연결 확인
try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")
