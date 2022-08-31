import os
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
Tmp_Resting_col = MongoClient[DB_NAME]["Waiting"]

from lib.common import line_bot_api, handler, doThreading

Total_Conditions_Count = 3
ALL_STATUS = [
    "New Starter",
    "Ready to go",
    "Condition_A_Pretest",
    "Condition_A_Chatting",
    "Condition_A_Posttest",
    "Condition_A_Finish",
    "Condition_B_Pretest",
    "Condition_B_Chatting",
    "Condition_B_Posttest",
    "Condition_B_Finish",
    "Condition_C_Pretest",
    "Condition_C_Chatting",
    "Condition_C_Posttest",
    "Condition_C_Finish",
    "Final_Test",
]


def get_user(user_id):
    user_profile = line_bot_api.get_profile(user_id)

    user = GPT3_chat_user_col.find_one({"user_id": user_id})
    if user == None:
        user = {
            "user_id": user_id,
            "display_name": user_profile.display_name,
            "sn": 0,
            "round": 0,
            "status": ALL_STATUS[0],
            "status_history": [],
        }
        GPT3_chat_user_col.insert_one(user)

    return user
