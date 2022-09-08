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

from lib.db import get_database, GPT3_chat_user_col

from datetime import datetime


class acceptTermOfTestBody(BaseModel):
    userId: str
    accept: bool


import json

formTemplate = "FormTemplate"


@router.post("/accept-term-of-test", responses={401: {}, 200: {}})
async def acceptTermOfTest(data: acceptTermOfTestBody):
    res = GPT3_chat_user_col.update_one(
        {"user_id": data.userId}, {"$set": {"acceptTermOfUse": data.accept}}
    )

    return {"res.modified_count": res.modified_count}
