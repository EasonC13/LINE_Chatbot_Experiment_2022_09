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

from lib.db import GPT3_chat_user_col, GPT3_chat_bots_col, Bots_Rating_Col

from datetime import datetime


import json


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
                "from": "pretest_api",
            }
        )
        done = res.acknowledged
    else:
        done = False

    return {"acknowledged": done}


@router.get("/isfinish")
async def big5(userId: str, status: str):
    try:
        Bots_Rating = Bots_Rating_Col.find_one({"user_id": userId, "status": status})
        return {"isFinish": bool(Bots_Rating)}
    except:
        return {"isFinish": False}
