#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from dotenv import load_dotenv

load_dotenv()


# In[2]:


from google.cloud import speech
import sys, pathlib
from pydub import AudioSegment
import requests
import json
import os
import uuid
import datetime

import io
def voice_reco(client, filename):
    with io.open(filename, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content = content)


    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="zh-TW"
    )
    response = client.recognize(config=config, audio=audio)
    try:
        text = response.results[0].alternatives[0].transcript
    except:
        text = ""
    return text

def process_voice_file(file_path):
    text = ""
    try:
        # Instantiates a client
        client = speech.SpeechClient.from_service_account_json(os.getenv('GOOGLE_SERVICE_JSON_PATH'))
        # Detects speech in the audio file
        wav = AudioSegment.from_wav(f'{file_path}.wav')
        if wav.duration_seconds < 60:
            text = voice_reco(client, f'{file_path}.wav')

            all_texts = [text]
        else:
            text = "too long... can't recognize..."
            wav_files = []
            while wav.duration_seconds > 60:
                temp_filename = str(uuid.uuid4())
                temp_filename = f'{file_path}.wav'
                slice_wav = wav[0:59]
                slice_wav.export(temp_filename, format="wav")
                wav_files.append(temp_filename)
                wav = wav[57:]
            temp_filename = str(uuid.uuid4())
            temp_filename = f'{file_path}.wav'
            wav.export(temp_filename, format="wav")
            wav_files.append(temp_filename)
            all_texts = []
            for wav_file in wav_files:
                text = voice_reco(client, wav_file)
                all_texts.append(text)
                os.remove(wav_file)

            #response = client.long_running_recognize(config=config, audio=audio)
            #response = operation.result(timeout=90)
            #text = response.results[0].alternatives[0].transcript
        #AAA.append(response)
        text = "".join(all_texts)
        

        os.remove(f'{file_path}.wav')
        os.remove(f'{file_path}')
    except ValueError as e:
        import traceback
        import sys
        exc_type, exc_value, exc_tb = sys.exc_info()
        text = "[ERROR]\n" + "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        '''if update.message.chat.id in User_List:
            result = "[ERROR]\n" + "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            bot.edit_message_text(text = result, message_id=reply_msg.message_id, chat_id= reply_msg.chat_id)
        else:
            result = "Error, Might be no detectable text in the voice message. If you think this is an error otherwise, please contect the author @EasonC13"
            bot.edit_message_text(text = result, message_id=reply_msg.message_id, chat_id= reply_msg.chat_id)'''
        
    return text


# In[3]:


import threading
import time
def doThreading(func, args, waitingTime = 0):
    time.sleep(waitingTime)
    t = threading.Thread(target = func, args = (args, ))
    t.start()


# In[4]:


def generate_text_response(input_text):
    result = requests.post(os.getenv('API_URL'), 
                      headers = {'accept': 'application/json',
                                 'Content-Type': 'application/json'},
                      data = json.dumps({
                          "email": os.getenv('API_USER'),
                          "secret": os.getenv('API_SECRET'),
                          "text": input_text,
                          "emotion": 1,
                          "response_count": 1,
                      }))
    response_text = result.json()["responses"][0]

    return response_text
    print(f"{text} => {response_text}")


# In[6]:


def process_voice_message(event):
    file_path = f'/tmp/{uuid.uuid4()}'
    
    message_content = line_bot_api.get_message_content(event.message.id)

    with open(file_path, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    subprocess.call(
            f'ffmpeg -i {file_path} {file_path}.wav',
            shell=True)

    text = process_voice_file(file_path)
    response_text = generate_text_response(text)
    print(f'{text} => {response_text}')

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response_text))

    user_profile = line_bot_api.get_profile(event.source.user_id)
    col.insert_one({
        'input_text': text,
        'response_text': response_text,
        'event_message_id': event.message.id,
        'user': {
            "display_name": user_profile.display_name,
            "user_id": event.source.user_id
        },
        "time": datetime.datetime.now(),
        "input_type": 'voice',
    })


# In[7]:


def process_text_message(event):
    text = event.message.text
    response_text = generate_text_response(text)
    print(f'{text} => {response_text}')

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response_text))

    user_profile = line_bot_api.get_profile(event.source.user_id)
    col.insert_one({
        'input_text': text,
        'response_text': response_text,
        'event_message_id': event.message.id,
        'user': {
            "display_name": user_profile.display_name,
            "user_id": event.source.user_id
        },
        "time": datetime.datetime.now(),
        "input_type": 'text',
    })


# In[8]:


import os
from dotenv import load_dotenv

load_dotenv()


# In[ ]:


from flask import Flask, request, abort
import subprocess

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, AudioMessage, AudioSendMessage
)

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

import pymongo
MongoClient = pymongo.MongoClient(os.getenv('MONGODB_URI'))
col = MongoClient["Service_Log"]["LINE_Accompany_Chat"]

@app.route("/service_learning", methods=['POST'])
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
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handleTextMessage(event):
    doThreading(process_text_message, args = (event))
    
@handler.add(MessageEvent, message=AudioMessage)
def handleAudioMessage(event):
    doThreading(process_voice_message, args = (event))
    

    

AAA = []
if __name__ == "__main__":
    app.run(port=32004)


# In[ ]:




