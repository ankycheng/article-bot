# -*- coding: utf-8 -*-
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import recommend
import json,random, requests

from flask_apscheduler import APScheduler
from datetime import datetime

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi()
# Channel Secret
handler = WebhookHandler('')

# 監聽所有來自 /callback 的 Post Request


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    t = event.message.text
    if '推薦' in t:
        t_input = t[2:]
        ret = recommend.getarticle(t_input)
        # rpy = json.dumps(ret, ensure_ascii=False)

        message = [TextSendMessage(text= ret[0]['title']+' '+ret[0]['url']),
                   TextSendMessage(text=ret[1]['title']+' '+ret[1]['url']),
                   TextSendMessage(text=ret[2]['title']+' '+ret[2]['url'])
                   ]

    else:
        message = TextSendMessage(text=t)
    line_bot_api.reply_message(event.reply_token, message)

class Config(object):
    JOBS = [
            {
               'id':'job1',
               'func':'app:job',
               'args': '',
               'trigger': 'interval',
               'seconds': 600
             }
        ]
       
    SCHEDULER_API_ENABLED = True

def job():
    try:
        url = 'https://design-articles.herokuapp.com/'
        requests.get(url)
    except LineBotApiError as e:
        print(e)
    # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"call")

import os
if __name__ == "__main__":

    app.config.from_object(Config())
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
