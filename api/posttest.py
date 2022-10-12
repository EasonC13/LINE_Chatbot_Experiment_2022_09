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
    Posttest_Questionnaire_Col,
)

from datetime import datetime


import json


class ratingBody(BaseModel):
    userId: str
    ratings: str
    condition: str
    status: str
    cost_time: str


@router.post("/ratings", responses={401: {}, 200: {}})
async def ratings(data: ratingBody):
    user = GPT3_chat_user_col.find_one({"user_id": data.userId})
    if user:
        ratings = json.loads(data.ratings)
        cost_time = json.loads(data.cost_time)
        res = Bots_Rating_Col.insert_one(
            {
                "user_id": data.userId,
                "ratings": ratings,
                "cost_time": cost_time,
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
        try:
            del r["user"]["_id"]
        except:
            pass
    return {"chats": res}


class ueqBody(BaseModel):
    all_rating: str
    userId: str
    condition: str
    status: str
    cost_time: str


@router.post("/questionnaire")
async def add_ueq_result(data: ueqBody, responses={401: {}, 200: {}}):
    user = GPT3_chat_user_col.find_one({"user_id": data.userId})
    if user:
        all_rating = json.loads(data.all_rating)
        cost_time = json.loads(data.cost_time)
        all_rating_list = []
        for key, value in all_rating.items():
            all_rating_list.append(value)

        res = Posttest_Questionnaire_Col.insert_one(
            {
                "user_id": data.userId,
                "condition": data.condition,
                "status": data.status,
                "all_rating": all_rating,
                "all_rating_list": all_rating_list,
                "cost_time": cost_time,
            }
        )
        done = res.acknowledged
    else:
        done = False
    return done


@router.get("/isfinish")
async def isFinish(userId: str, status: str):
    try:
        UEQ_CUQ = Posttest_Questionnaire_Col.find_one(
            {"user_id": userId, "status": status}
        )
        Rating = Bots_Rating_Col.find_one(
            {
                "user_id": userId,
                "status": status,
            }
        )
        return {"isFinish": bool(UEQ_CUQ) and bool(Rating)}
    except:
        return {"isFinish": False}
