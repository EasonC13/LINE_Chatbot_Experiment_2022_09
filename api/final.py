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

from lib.db import GPT3_chat_user_col, SUS_Col, TAM_Col, Final_Survey_Col, EXP_SUS_Col

from datetime import datetime


import json


class susBody(BaseModel):
    userId: str
    sus: str
    feeling: str
    vision: str


@router.post("/sus")
async def sus(data: susBody):
    sus = json.loads(data.sus)
    res = SUS_Col.insert_one(
        {
            "user_id": data.userId,
            "sus": sus,
            "feeling": data.feeling,
            "vision": data.vision,
        }
    )
    return {"acknowledged": res.acknowledged}


class exp_susBody(BaseModel):
    userId: str
    sus: str
    suggestion: str


@router.post("/exp_sus")
async def sus(data: exp_susBody):
    sus = json.loads(data.sus)
    res = EXP_SUS_Col.insert_one(
        {
            "user_id": data.userId,
            "sus": sus,
            "suggestion": data.suggestion,
        }
    )
    return {"acknowledged": res.acknowledged}


class tamBody(BaseModel):
    userId: str
    tam: str
    other_options: str


@router.post("/tam")
async def tam(data: tamBody):
    tam = json.loads(data.tam)
    res = TAM_Col.insert_one(
        {"user_id": data.userId, "tam": tam, "other_options": data.other_options}
    )
    return {"acknowledged": res.acknowledged}


class finalBody(BaseModel):
    userId: str
    email: str
    gender: str
    age: int
    bank_id: str
    bank_account: str
    feedback: str


@router.post("/final")
async def final_survey(data: finalBody):
    res = Final_Survey_Col.insert_one(
        {
            "user_id": data.userId,
            "email": data.email,
            "gender": data.gender,
            "age": data.age,
            "bank_id": data.bank_id,
            "bank_account": data.bank_account,
            "feedback": data.feedback,
        }
    )
    return {"acknowledged": res.acknowledged}

    # userId: this.$route.query.id,
    # email: this.email,
    # gender: this.gender,
    # age: this.age,
    # bank_id: this.bank_id,
    # bank_account: this.bank_account,
    # feedback: this.feedback,


@router.get("/isfinish")
async def isFinish(userId: str):
    try:
        Final_Survey = Final_Survey_Col.find_one({"user_id": userId})
        TAM = TAM_Col.find_one({"user_id": userId})
        EXP_SUS = EXP_SUS_Col.find_one({"user_id": userId})
        SUS = SUS_Col.find_one({"user_id": userId})
        return {"isFinish": bool(Final_Survey and TAM and EXP_SUS and SUS)}
    except:
        return {"isFinish": False}


class followupBody(BaseModel):
    userId: str
    checked: bool
    questions: str


@router.post("/followup")
async def followup(data: followupBody):

    res = GPT3_chat_user_col.update_one(
        {
            "user_id": data.userId,
        },
        {
            "$set": {
                "want_follow_up": data.checked,
                "follow_up_questions": data.questions,
            }
        },
    )
    return {"acknowledged": res.acknowledged}
