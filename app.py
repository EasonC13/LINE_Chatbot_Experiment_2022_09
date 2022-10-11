import os
from sys import prefix
from dotenv import load_dotenv

load_dotenv()
load_dotenv("/eason/.server.env")

import pymongo

MongoClient = pymongo.MongoClient(
    f"mongodb://{os.getenv('mongo_user')}:{os.getenv('mongo_pw')}@localhost:27081"
)

DB_NAME = "chatbot_experiment_2022_09"
GPT3_chat_history_col = MongoClient[DB_NAME]["GPT3_Chat"]
GPT3_chat_user_col = MongoClient[DB_NAME]["Users"]
GPT3_chat_bots_col = MongoClient[DB_NAME]["Bots"]


from translate import translate

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
)


from fastapi import FastAPI, Depends, status, Header, Request
import pymongo
from starlette.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from typing import Any, Dict, AnyStr, List, Union
import asyncio
import subprocess


app = FastAPI(title="Chatbot Experience", version=1, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from lib.common import line_bot_api, handler, doThreading


@app.post("/api/v1/line_bot")
async def callback(request: Request):
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = await request.body()

    # handle webhook body
    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Missing Parameter")

    return "OK"


from lib.logic_handler import process_text_message
from lib.voice import process_voice_message


@handler.add(MessageEvent, message=TextMessage)
def handleTextMessage(event):
    doThreading(process_text_message, args=(event))


# @handler.add(MessageEvent, message=AudioMessage)
# def handleAudioMessage(event):
#     doThreading(process_voice_message, args=(event))


from api.routes import router as api_v1_router

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/api/v1/status")
def get_status():
    user_count = GPT3_chat_user_col.estimated_document_count()
    chat_count = GPT3_chat_history_col.estimated_document_count()
    return {"user_count": user_count, "chat_count": chat_count}


from fastapi.staticfiles import StaticFiles

app.mount(
    "/",
    StaticFiles(
        directory="/home/eason/Python/WEB/service/LINE_Bot/2022_09_chatbot_experiment/frontend/dist",
        html=True,
    ),
)

if __name__ == "__main__":
    app.run(port=os.getenv("API_PORT"))
