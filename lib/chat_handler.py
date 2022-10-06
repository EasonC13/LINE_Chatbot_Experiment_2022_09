import openai
from lib.db import (
    GPT3_chat_user_col,
    GPT3_chat_bots_col,
    GPT3_chat_history_col,
    GPT3_chat_log_col,
    get_user,
    TAG_col,
)
import os
from lib.common import line_bot_api, handler, doThreading

openai.api_key = os.getenv("OPENAI_API_KEY")

from translate import translate

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage,
    TemplateSendMessage,
    MessageTemplateAction,
    ButtonsTemplate,
    PostbackEvent,
    PostbackTemplateAction,
    AudioMessage,
    AudioSendMessage,
    Sender,
    QuickReply,
    QuickReplyButton,
    PostbackAction,
    QuickReplyButton,
    MessageAction,
)
import subprocess

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

from bson.objectid import ObjectId


def create_prompt(prompt, prev_msgs, text, num=-3):
    prompt = (prompt + "\n") if prompt[-1] != "\n" else prompt
    for msg in prev_msgs[num:]:
        prompt += f"You: {msg['input_text_en']}\nFriend: {msg['response_text_en']}\n"
    prompt += f"You: {text}\nFriend: "
    return prompt


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


def generate_GPT3_response(event, text, bot, condition):

    user = get_user(event.source.user_id)

    prev_msgs = GPT3_chat_history_col.find(
        {
            "user.user_id": event.source.user_id,
            "user.sn": user["sn"],  # serial number
            "bot_id": bot["id"],
            "condition": condition,
        }
    )
    prev_msgs = list(prev_msgs)
    prev_msgs.sort(key=lambda x: x["time"])

    prompt = create_prompt(bot["prefix"], prev_msgs, text, -3)

    have_second_chance = True
    max_try = 4

    response = openai.Completion.create(
        engine="text-davinci-001",
        prompt=prompt,
        temperature=0.6,
        max_tokens=120,
        top_p=1.0,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        stop=["You:"],
    )

    response_text = response.choices[0].text.replace("\n", "")

    prev_responses = list(map(lambda x: x["response_text_en"], prev_msgs[-3:]))
    count = np.unique(prev_responses, return_counts=True)[1]

    print(prompt + response_text, end="\n")

    return response_text


def norm_text(text):
    text = text.replace("&#39;", "'")
    return text


def get_bots(bot_id):
    return GPT3_chat_bots_col.find_one({"id": bot_id})


def send_GPT3_response(text, event):

    user = get_user(event.source.user_id)
    user_profile = line_bot_api.get_profile(event.source.user_id)

    translated_result = translate(text, target="en")

    text_en = translated_result["translatedText"]
    text_en = norm_text(text_en)
    text_source = translated_result["detectedSourceLanguage"]
    if text_source == "und":
        text_source = "zh-tw"

    condition = user["status"].split("_")[1]
    bots = list(GPT3_chat_bots_col.find({"condition": condition}))

    reply_to = TAG_col.find_one_and_update(
        {
            "user": {
                "user_id": event.source.user_id,
                "sn": user["sn"],
                "status": user["status"],
            },
            "expired": False,
        },
        {"$set": {"expired": True}},
    )

    message = []
    tasks = []
    now = datetime.datetime.now()
    responses_log = []

    for bot in bots:
        t = doThreading(
            thread_GPT3,
            args=(
                message,
                event,
                text,
                text_en,
                bot,
                user_profile,
                user,
                text_source,
                now,
                responses_log,
                bots,
                reply_to,
            ),
        )
        tasks.append(t)
        # thread_GPT3(message, event, text, text_en, bot, user_profile, user, text_source)
    for t in tasks:
        t.join()

    # print(message)

    line_bot_api.reply_message(event.reply_token, message)
    data = {
        "user": user,
        "condition": user["status"],
        "input_text": text,
        "input_text_en": text_en,
        "responses": responses_log,
        "time": datetime.datetime.now(),
        "user_id": event.source.user_id,
        "event_message_id": event.message.id,
        "reply_to": reply_to["tag"] if reply_to else None,
        "reply_to_id": str(reply_to["_id"]) if reply_to else None,
    }
    GPT3_chat_log_col.insert_one(data)


def thread_GPT3(
    message,
    event,
    text,
    text_en,
    bot,
    user_profile,
    user,
    text_source,
    now,
    responses_log,
    bots,
    reply_to,
):
    response_text = ""
    while response_text == "":
        response_text_en = generate_GPT3_response(event, text_en, bot, user["status"])
        response_text_en = norm_text(response_text_en)
        # print(f"response_text_en = {response_text_en}, text_source = {text_source}")

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

    # print("----")
    # print(f"From: {bot['id']}")
    # print("--Origin--")
    # print(f"{text_en} => {response_text_en}")
    # print("--Translated--")
    # print(f"{text} => {response_text}")
    # print("========")

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
            "condition": user["status"],
            "reply_to": reply_to["tag"] if reply_to else None,
            "reply_to_id": str(reply_to["_id"]) if reply_to else None,
        }
    )
    responses_log.append(
        {
            "input_text": text,
            "input_text_en": text_en,
            "response_text_en": response_text_en,
            "response_text": response_text,
            "bot_id": bot["id"],
            "bot_img": bot["img_url"],
            "bot_name": bot["name"],
        }
    )
    buttons = []
    for b in bots:
        buttons.append(
            QuickReplyButton(
                action=MessageAction(label=f"＠{b['name']}", text=f"＠{b['name']}")
            ),
        )
    message.append(
        TextSendMessage(
            text=response_text,
            sender=Sender(name=bot["name"].replace("_", " "), icon_url=bot["img_url"]),
            quick_reply=QuickReply(items=buttons),
        )
    )


def process_tag(user, event):
    import datetime

    TAG_col.find_one_and_update(
        {
            "user": {
                "user_id": event.source.user_id,
                "sn": user["sn"],
                "status": user["status"],
            },
            "expired": False,
        },
        {"$set": {"expired": True}},
    )
    TAG_col.insert_one(
        {
            "tag": event.message.text.replace("＠", ""),
            "user": {
                "user_id": event.source.user_id,
                "sn": user["sn"],
                "status": user["status"],
            },
            "time": datetime.datetime.now(),
            "expired": False,
        }
    )
    return True
