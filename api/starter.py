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

from lib.db import GPT3_chat_user_col, Big5_Col, AttachmentStyle_Col

from datetime import datetime


class acceptTermOfTestBody(BaseModel):
    userId: str
    accept: bool


import json

formTemplate = "FormTemplate"


@router.post("/accept-term-of-test", responses={401: {}, 200: {}})
async def acceptTermOfTest(data: acceptTermOfTestBody):
    res = GPT3_chat_user_col.update_one(
        {"user_id": data.userId}, {"$set": {"acceptTermOfTest": data.accept}}
    )

    return {"res.modified_count": res.modified_count}


class big5Body(BaseModel):
    userId: str
    big5: str


@router.post("/big5", responses={401: {}, 200: {}})
async def big5(data: big5Body):
    user = GPT3_chat_user_col.find_one({"user_id": data.userId})
    if user:
        big5 = json.loads(data.big5)
        res = Big5_Col.insert_one(
            {"user_id": data.userId, "Big5": big5, "add_time": datetime.now()}
        )
        done = res.acknowledged
    else:
        done = False

    return {"acknowledged": done}


class attachmentBody(BaseModel):
    userId: str
    style: int


@router.post("/attachment-style", responses={401: {}, 200: {}})
async def big5(data: attachmentBody):
    user = GPT3_chat_user_col.find_one({"user_id": data.userId})
    if user:
        res = AttachmentStyle_Col.insert_one(
            {"user_id": data.userId, "style": data.style, "add_time": datetime.now()}
        )
        done = res.acknowledged
    else:
        done = False

    return {"acknowledged": done}


@router.get("/isfinish")
async def isFinish(userId: str):
    try:
        AttachmentStyle = AttachmentStyle_Col.find_one({"user_id": userId})
        Big5 = Big5_Col.find_one({"user_id": userId})
        Accept = GPT3_chat_user_col.find_one({"user_id": userId})["acceptTermOfTest"]
        return {"isFinish": AttachmentStyle and Big5 and Accept}
    except:
        return {"isFinish": False}
