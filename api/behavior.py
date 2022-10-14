from xmlrpc.client import boolean
from fastapi import APIRouter, Response, status

router = APIRouter()

from typing import List, Optional
from pydantic import BaseModel
from typing import Any, Dict, AnyStr, List, Union
from datetime import datetime, timedelta
from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# from passlib.context import CryptContext

import secrets

from lib.db import (
    GPT3_chat_user_col,
    Behavior_col,
)

from datetime import datetime


import json


class changeTopicBody(BaseModel):
    userId: str


@router.post("/changeTopic", responses={401: {}, 200: {}})
async def changeTopic(data: changeTopicBody):
    user = GPT3_chat_user_col.find_one({"user_id": data.userId})
    if user:
        res = Behavior_col.insert_one(
            {
                "user_id": data.userId,
                "round": user["round"],
                "condition": user["status"],
                "behavior": "changeTopic",
                "add_time": datetime.now(),
            }
        )
        done = res.acknowledged
    else:
        done = False

    return {"acknowledged": done}


class openChatHistoryBody(BaseModel):
    userId: str
    botId: str
    duration: float
    bot_orders: List[str]
    at_bot_order: int


@router.post("/openChatHistory", responses={401: {}, 200: {}})
async def changeTopic(data: openChatHistoryBody):
    user = GPT3_chat_user_col.find_one({"user_id": data.userId})
    if user:
        res = Behavior_col.insert_one(
            {
                "user_id": data.userId,
                "bot_id": data.botId,
                "condition": user["status"],
                "behavior": "openChatHistory",
                "bot_orders": data.bot_orders,
                "at_bot_order": data.at_bot_order,
                "duration": data.duration,
                "add_time": datetime.now(),
            }
        )
        done = res.acknowledged
    else:
        done = False

    return {"acknowledged": done}
