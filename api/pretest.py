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


import json


@router.get("/bots")
async def bots(condition: str):
    bots = list(GPT3_chat_bots_col.find({"condition": condition}, {"_id": False}))
