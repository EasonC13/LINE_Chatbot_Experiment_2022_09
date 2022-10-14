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
GPT3_chat_log_col = MongoClient[DB_NAME]["GPT3_Chat_log"]
GPT3_chat_user_col = MongoClient[DB_NAME]["Users"]
GPT3_chat_bots_col = MongoClient[DB_NAME]["Bots"]
Resting_Notify_col = MongoClient[DB_NAME]["Resting_Notify"]
Big5_Col = MongoClient[DB_NAME]["Users_Big5"]
AttachmentStyle_Col = MongoClient[DB_NAME]["Users_AttachmentStyle"]
Bots_Rating_Col = MongoClient[DB_NAME]["Bots_Rating"]
Posttest_Questionnaire_Col = MongoClient[DB_NAME]["Posttest_Questionnaire"]
SUS_Col = MongoClient[DB_NAME]["SUS"]
EXP_SUS_Col = MongoClient[DB_NAME]["EXP_SUS"]
TAM_Col = MongoClient[DB_NAME]["TAM"]
Final_Survey_Col = MongoClient[DB_NAME]["Final_Survey"]
TAG_col = MongoClient[DB_NAME]["GPT3_Chat_Tag"]
Behavior_col = MongoClient[DB_NAME]["Behavior"]
ERROR_col = MongoClient[DB_NAME]["Errors"]
INIT_MSG_col = MongoClient[DB_NAME]["init_msg"]


def get_database():
    return MongoClient[DB_NAME]


from lib.common import line_bot_api, handler, doThreading

Total_Conditions_Count = 3
ALL_STATUS = [
    "New_Starter",
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
    "Condition_D_Pretest",
    "Condition_D_Chatting",
    "Condition_D_Posttest",
    "Condition_D_Finish",
    "Condition_E_Pretest",
    "Condition_E_Chatting",
    "Condition_E_Posttest",
    "Condition_E_Finish",
    "Final_Test",
    "Finish",
]


def get_user(user_id, want_id=False):
    user_profile = line_bot_api.get_profile(user_id)

    user = GPT3_chat_user_col.find_one({"user_id": user_id}, {"_id": want_id})
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
