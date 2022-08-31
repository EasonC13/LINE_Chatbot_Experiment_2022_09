
import os
from dotenv import load_dotenv
load_dotenv()
load_dotenv('/eason/.server.env')


from linebot import (
    LineBotApi, WebhookHandler
)

line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

import threading
import time

def doThreading(func, args, waitingTime = 0):
    time.sleep(waitingTime)
    try:
        if len(args) >= 2:
            t = threading.Thread(target = func, args = (args))
        else:
            t = threading.Thread(target = func, args = (args, ))
    except:
        t = threading.Thread(target = func, args = (args, ))
    t.start()
    return t
