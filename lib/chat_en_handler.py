import openai
from lib.db import (
    GPT3_chat_user_col,
    GPT3_chat_bots_col,
    GPT3_chat_history_col,
    GPT3_chat_log_col,
    TAG_col,
    ERROR_col,
    get_user,
)
import os
from lib.common import line_bot_api, handler, doThreading, process_tag

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

from telegram_notifier import send_message


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
from lib.db import GPT3_chat_bots_col


def create_prompt(prompt, prev_msgs, text, bot, num=-3):
    prompt = prompt.replace("{bot_name}", bot["eng_name"])
    prompt = (prompt + "\n") if prompt[-1] != "\n" else prompt
    for msg in prev_msgs[num:]:
        prompt += f"You: {msg['input_text_en']}\nFriend: {msg['response_text_en']}\n"
    prompt += f"You: {text}\nFriend: "
    return prompt


def shorten_prompt(prompt):
    prompt = prompt.split("\n")
    if len(prompt) > 3:
        del prompt[1:3]

    prompt = "\n".join(prompt)
    return prompt


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

    prompt = create_prompt(bot["prefix"], prev_msgs, text, bot, -3)

    have_second_chance = True
    max_try = 5
    for tried in range(max_try):
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

        if (
            len(prev_msgs) == 0 or response_text != prev_msgs[-1]["response_text_en"]
        ) and len(response_text) != 0:
            break
        else:
            prompt = shorten_prompt(prompt)
            # print(
            #     f"\n\nshorten_prompt for {bot['id']} with reply {response_text} on tried {tried}\n\n"
            # )
    print("\n\nAt generate_GPT3_response:\n", prompt + response_text, end="\n")
    # print(
    #     'response_text != prev_msgs[-1]["response_text_en"]: ',
    #     response_text != prev_msgs[-1]["response_text_en"],
    #     response_text,
    #     prev_msgs[-1]["response_text_en"],
    # )
    if response_text == "":
        # print(f"response_text: '{response_text}', {len(response_text) != 0}")
        response_text = "..."
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
    if len(message) == 0:
        send_message(f"[聊天機器人實驗]\n出現回應訊息數為零的錯誤在受試者 ID: {event.source.user_id}")
        ERROR_col.insert_one({"user": user, "time": datetime.datetime.now()})
    try:
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        line_bot_api.push_message(event.source.user_id, message)

    res = GPT3_chat_log_col.find(
        {"user_id": event.source.user_id},
        {"event_message_id": 1, "time": 1},
    )
    res.sort("_id", direction=-1)
    res = list(res)
    if res:
        prev_event_message_id = res[0]["event_message_id"]
    else:
        prev_event_message_id = 0
    data = {
        "user": user,
        "condition": user["status"],
        "input_text": text,
        "input_text_en": text_en,
        "responses": responses_log,
        "time": datetime.datetime.now(),
        "user_id": event.source.user_id,
        "event_message_id": event.message.id,
        "prev_event_message_id": prev_event_message_id,
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
    response_text_en = generate_GPT3_response(event, text_en, bot, user["status"])
    response_text_en = norm_text(response_text_en)
    # print(f"response_text_en = {response_text_en}, text_source = {text_source}")

    if text_source[:2] == "zh":
        response_text = translate(response_text_en, target="zh-TW")["translatedText"]
    elif text_source != "en":
        response_text = translate(response_text_en, target=text_source)[
            "translatedText"
        ]
    else:
        response_text = translate(response_text_en, target="zh-TW")["translatedText"]
        # response_text = response_text_en

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
    buttons = [
        QuickReplyButton(action=MessageAction(label=f"換個話題", text=f"換個話題")),
    ]
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
