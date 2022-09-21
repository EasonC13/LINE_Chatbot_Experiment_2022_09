from xmlrpc.client import boolean
from fastapi import APIRouter, Response, status

router = APIRouter()

from typing import Optional
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
    GPT3_chat_bots_col,
    Bots_Rating_Col,
    GPT3_chat_log_col,
    UEQ_Col,
)

from datetime import datetime


import json


@router.get("/bots")
async def bots(condition: str):
    condition = condition.split("_")[-1]
    bots = list(GPT3_chat_bots_col.find({"condition": condition}, {"_id": False}))
    return bots


class ratingBody(BaseModel):
    userId: str
    ratings: str
    condition: str
    status: str


@router.post("/ratings", responses={401: {}, 200: {}})
async def ratings(data: ratingBody):
    user = GPT3_chat_user_col.find_one({"user_id": data.userId})
    if user:
        ratings = json.loads(data.ratings)
        res = Bots_Rating_Col.insert_one(
            {
                "user_id": data.userId,
                "ratings": ratings,
                "condition": data.condition,
                "status": data.status,
                "add_time": datetime.now(),
                "from": "posttest_api",
            }
        )
        done = res.acknowledged
    else:
        done = False

    return {"acknowledged": done}


@router.get("/chat_history")
async def get_chat_history(
    userId: str = "Ub830fb81ec2de64d825b4ab2f6b7472e",
    condition: str = "Condition_B",
):
    condition = condition + "_Chatting"
    res = GPT3_chat_log_col.find(
        {"user_id": userId, "condition": condition}, {"_id": False}
    )
    res = list(res)
    for r in res:
        del r["user"]["_id"]
    return {"chats": res}


class ueqBody(BaseModel):
    all_ueq: str
    userId: str
    condition: str
    status: str


@router.post("/ueq")
async def add_ueq_result(data: ueqBody):
    all_ueq = json.loads(data.all_ueq)
    all_ueq_list = []
    for key, value in all_ueq.items():
        all_ueq_list.append(value)
    UEQ_Col.insert_one(
        {
            "user_id": data.userId,
            "condition": data.condition,
            "status": data.status,
            "all_ueq": all_ueq,
            "all_ueq_list": all_ueq_list,
        }
    )
    pass


@router.get("/isfinish")
async def big5(userId: str):
    # TODO
    return {"isFinish": True}
