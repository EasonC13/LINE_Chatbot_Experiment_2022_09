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

from lib.db import GPT3_chat_user_col, GPT3_chat_bots_col

from datetime import datetime
import random


@router.get("/isfinish")
async def big5(userId: str, condition: str):
    user = GPT3_chat_user_col.find_one({"user_id": userId})
    return {"isfinish": condition in user["status_history"]}


@router.get("/bots")
async def bots(condition: str, shuffle: bool = True):
    condition = condition.split("_")[-1]
    bots = list(GPT3_chat_bots_col.find({"condition": condition}, {"_id": False}))
    random.shuffle(bots)
    return bots
