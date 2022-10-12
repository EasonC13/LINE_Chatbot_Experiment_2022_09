#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from dotenv import load_dotenv

load_dotenv()
load_dotenv("/eason/.server.env")

import pymongo

MongoClient = pymongo.MongoClient(
    f"mongodb://{os.getenv('mongo_user')}:{os.getenv('mongo_pw')}@localhost:27081"
)

GPT3_chat_history_col = MongoClient["GPT3_Chatbot"]["GPT3_Chat"]
GPT3_chat_user_col = MongoClient["GPT3_Chatbot"]["Users"]
GPT3_chat_bots_col = MongoClient["GPT3_Chatbot"]["Bots"]


# In[2]:


from translate import translate


# In[3]:


import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


# In[4]:


from google.cloud import speech
import sys, pathlib
from pydub import AudioSegment
import requests
import json
import os
import uuid
import datetime
import numpy as np

import io


def voice_reco(client, filename):
    with io.open(filename, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="zh-TW",
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
        client = speech.SpeechClient.from_service_account_json(
            os.getenv("GOOGLE_SERVICE_JSON_PATH")
        )
        # Detects speech in the audio file
        wav = AudioSegment.from_wav(f"{file_path}.wav")
        if wav.duration_seconds < 60:
            text = voice_reco(client, f"{file_path}.wav")

            all_texts = [text]
        else:
            text = "too long... can't recognize..."
            wav_files = []
            while wav.duration_seconds > 60:
                temp_filename = str(uuid.uuid4())
                temp_filename = f"{file_path}.wav"
                slice_wav = wav[0:59]
                slice_wav.export(temp_filename, format="wav")
                wav_files.append(temp_filename)
                wav = wav[57:]
            temp_filename = str(uuid.uuid4())
            temp_filename = f"{file_path}.wav"
            wav.export(temp_filename, format="wav")
            wav_files.append(temp_filename)
            all_texts = []
            for wav_file in wav_files:
                text = voice_reco(client, wav_file)
                all_texts.append(text)
                os.remove(wav_file)

            # response = client.long_running_recognize(config=config, audio=audio)
            # response = operation.result(timeout=90)
            # text = response.results[0].alternatives[0].transcript
        # AAA.append(response)
        text = "".join(all_texts)

        os.remove(f"{file_path}.wav")
        os.remove(f"{file_path}")
    except ValueError as e:
        import traceback
        import sys

        exc_type, exc_value, exc_tb = sys.exc_info()
        text = "[ERROR]\n" + "".join(
            traceback.format_exception(exc_type, exc_value, exc_tb)
        )
        """if update.message.chat.id in User_List:
            result = "[ERROR]\n" + "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            bot.edit_message_text(text = result, message_id=reply_msg.message_id, chat_id= reply_msg.chat_id)
        else:
            result = "Error, Might be no detectable text in the voice message. If you think this is an error otherwise, please contect the author @EasonC13"
            bot.edit_message_text(text = result, message_id=reply_msg.message_id, chat_id= reply_msg.chat_id)"""

    return text


# In[5]:


import threading
import time


def doThreading(func, args, waitingTime=0):
    time.sleep(waitingTime)
    try:
        if len(args) == 1:
            t = threading.Thread(target=func, args=(args,))
        else:
            t = threading.Thread(target=func, args=(args))
    except:
        t = threading.Thread(target=func, args=(args,))
    t.start()
    return t


# In[ ]:


# In[6]:


def process_voice_message(event):
    # AAA.append(event)
    file_path = f"/tmp/{uuid.uuid4()}"

    message_content = line_bot_api.get_message_content(event.message.id)

    with open(file_path, "wb") as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    subprocess.call(
        f"ffmpeg -i {file_path} {file_path}.wav",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    text = process_voice_file(file_path)
    send_GPT3_response(text=text, event=event)


# In[7]:


from bson.objectid import ObjectId


def create_prompt(prompt, prev_msgs, text, num=-3):
    prompt = (prompt + "\n") if prompt[-1] != "\n" else prompt
    for msg in prev_msgs[num:]:
        prompt += f"You: {msg['input_text_en']}\nFriend: {msg['response_text_en']}\n"
    prompt += f"You: {text}\nFriend: "
    return prompt


# In[ ]:


# In[8]:


def get_user(event):
    user_profile = line_bot_api.get_profile(event.source.user_id)

    user = GPT3_chat_user_col.find_one({"user_id": event.source.user_id})
    if user == None:
        user = {
            "user_id": event.source.user_id,
            "display_name": user_profile.display_name,
            "bots": ["欠嗆貓", "Stonk_Guy", "LLENN", "棒男孩", "Gawr_Gura"],
            "sn": 0,
        }
        GPT3_chat_user_col.insert_one(user)

    print("YEEE", user)
    return user


# In[9]:


# 以棄用
def update_pre_prompt():
    """def update_pre_prompt(user_id, text):
        GPT3_chat_user_col.update_one({
                "user_id": user_id
            },{
                "$set": {"pre_prompt": text}
            })

    def update_chat_with(user_id, chat_with, chat_from = "You"):
        GPT3_chat_user_col.update_one({
                "user_id": user_id
            },{"$set":{
                "chat_with": chat_with,
                "chat_from": chat_from,
            }})"""


pass


# In[10]:


def generate_GPT3_response(event, text, bot):

    user = get_user(event)

    prev_msgs = GPT3_chat_history_col.find(
        {
            "user.user_id": event.source.user_id,
            "user.sn": user["sn"],  # serial number
            "bot_id": bot["id"],
        }
    )
    prev_msgs = list(prev_msgs)
    prev_msgs.sort(key=lambda x: x["time"])

    prompt = create_prompt(bot["prefix"], prev_msgs, text, -3)

    have_second_chance = True
    max_try = 4

    for i in range(max_try):
        response = openai.Completion.create(
            engine="text-davinci-001",
            prompt=prompt,
            temperature=0.6 + 0.1 * i,
            max_tokens=120,
            top_p=1.0,
            frequency_penalty=0.5 + 0.5 * i,
            presence_penalty=0.5 + 0.5 * i,
            stop=["You:"],
        )

        response_text = response.choices[0].text.replace("\n", "")
        if i != 0:
            print(f"{i}th try  => {response_text}", end="\n---\n")

        prev_responses = list(map(lambda x: x["response_text_en"], prev_msgs[-3:]))
        count = np.unique(prev_responses, return_counts=True)[1]
        if response_text in prev_responses and sum(count > 1):
            if have_second_chance == True:
                have_second_chance = False
            elif i == max_try - 2:
                # print("Last Try")
                prompt = create_prompt(bot["prefix"], [], text, -1)
            else:
                prompt = create_prompt(bot["prefix"], prev_msgs, text, -1)
            # print("New Prompt: ", prompt)
        else:
            break
    print("--GPT3 Input/Output--")
    print(prompt + response_text, end="\n")

    return response_text


# In[11]:


def norm_text(text):
    text = text.replace("&#39;", "'")
    return text


# In[12]:


from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    TemplateSendMessage,
    MessageTemplateAction,
    ButtonsTemplate,
    PostbackEvent,
    PostbackTemplateAction,
    AudioMessage,
    AudioSendMessage,
    Sender,
)


# In[ ]:


# In[13]:


def process_text_message(event):
    text = event.message.text

    if process_command(event, text):
        return True

    send_GPT3_response(text, event)


# In[ ]:


# In[14]:


def get_bots(bot_id):
    return GPT3_chat_bots_col.find_one({"id": bot_id})


# In[ ]:


# In[15]:


def send_GPT3_response(text, event):

    user = get_user(event)
    user_profile = line_bot_api.get_profile(event.source.user_id)

    translated_result = translate(text, target="en")

    text_en = translated_result["translatedText"]
    text_en = norm_text(text_en)
    text_source = translated_result["detectedSourceLanguage"]

    bots_id = user["bots"]
    if len(bots_id) == 0:
        bots_id = ["棒男孩"]
    bots = list(map(get_bots, bots_id))

    message = []
    tasks = []  # TODO: 如果需要照順序回要改成寫 mapping
    for bot in bots:
        t = doThreading(
            thread_GPT3,
            args=(message, event, text, text_en, bot, user_profile, user, text_source),
        )
        tasks.append(t)
        # thread_GPT3(message, event, text, text_en, bot, user_profile, user, text_source)
    for t in tasks:
        t.join()

    line_bot_api.reply_message(event.reply_token, message)


# In[16]:


def thread_GPT3(message, event, text, text_en, bot, user_profile, user, text_source):
    response_text = ""
    while response_text == "":
        response_text_en = generate_GPT3_response(event, text_en, bot)
        response_text_en = norm_text(response_text_en)

        if text_source[:2] == "zh":
            response_text = translate(response_text_en, target="zh-TW")[
                "translatedText"
            ]
        elif text_source != "en":
            response_text = translate(response_text_en, target=text_source)[
                "translatedText"
            ]
        else:
            response_text = response_text_en

    print("----")
    print(f"From: {bot['id']}")
    print("--Origin--")
    print(f"{text_en} => {response_text_en}")
    print("--Translated--")
    print(f"{text} => {response_text}")
    print("========")

    GPT3_chat_history_col.insert_one(
        {
            "input_text": text,
            "input_text_en": text_en,
            "response_text_en": response_text_en,
            "response_text": response_text,
            "event_message_id": event.message.id,
            "user": {
                "display_name": user_profile.display_name,
                "user_id": event.source.user_id,
                "sn": user["sn"],
            },
            "bot_id": bot["id"],
            "time": datetime.datetime.now(),
            "input_type": "text",
        }
    )

    message.append(
        TextSendMessage(
            text=response_text,
            sender=Sender(name=bot["name"].replace("_", " "), icon_url=bot["img_url"]),
        )
    )


# In[17]:


change_topic_command_zh = [
    "刷新",
]
change_topic_command_en = ["change topic"]


def increase_chat_sn(user_id):
    GPT3_chat_user_col.update_one({"user_id": user_id}, {"$inc": {"sn": 1}})


def process_command(event, text):
    user_id = event.source.user_id
    user = get_user(event)

    if text in change_topic_command_zh:
        increase_chat_sn(user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="""讓我們繼續聊天吧～\n如果我又持續說重複的話，請輸入「刷新」以繼續對話"""),
        )
        return True
    elif text in change_topic_command_en:
        increase_chat_sn(user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text="""Topic changed, let's continue chatting.\nIf I keep saying weird things again, please enter 'change topic'."""
            ),
        )
        return True

    return False


# In[18]:


from flask import Flask, request, abort, render_template, send_from_directory
import subprocess


app = Flask(__name__, template_folder="dist")

line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))


@app.route("/api/v1/line_bot", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handleTextMessage(event):
    doThreading(process_text_message, args=(event))


@handler.add(MessageEvent, message=AudioMessage)
def handleAudioMessage(event):
    doThreading(process_voice_message, args=(event))


# In[19]:


@app.route("/api/v1/status", methods=["GET"])
def get_status():
    user_count = GPT3_chat_user_col.estimated_document_count()
    chat_count = GPT3_chat_history_col.estimated_document_count()
    return {"user_count": user_count, "chat_count": chat_count}


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


AAA = []
if __name__ == "__main__":
    from flask_cors import CORS

    CORS(app)
    app.run(port=os.getenv("API_PORT"))


# In[ ]:


# os.system('cd ../frontend && rm -rf dist && unzip -qq dist && echo "Update Frontend Success"')


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:
