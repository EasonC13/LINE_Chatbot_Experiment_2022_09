import secrets
from tokenize import tabsize
from lib.common import line_bot_api, handler, doThreading
from lib.db import (
    GPT3_chat_user_col,
    GPT3_chat_bots_col,
    GPT3_chat_history_col,
    get_user,
    Total_Conditions_Count,
    Tmp_Resting_col,
)
from lib.imp import *

import time
from lib.gpt3_handler import send_GPT3_response


def process_text_message(event):
    text = event.message.text

    if process_command(event, text):
        return True

    send_GPT3_response(text, event)


def update_user_status(user_id, newStatus):
    user = GPT3_chat_user_col.find_one({"user_id": user_id})
    GPT3_chat_user_col.update_one(
        {"user_id": user_id},
        {"$set": {"status": newStatus}, "$push": {"status_history": user["status"]}},
    )


def update_user_round(user, round=None):
    round = round if round != None else user["round"]
    GPT3_chat_user_col.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"round": round}},
    )  # Condition_A_Chatting


user = get_user("Ub830fb81ec2de64d825b4ab2f6b7472e")

user

import random


def randomly_get_next_task(user):
    tasks = ["Condition_A_Pretest", "Condition_B_Pretest", "Condition_C_Pretest"]
    random.shuffle(tasks)
    tasks.append(False)
    for t in tasks:
        if t not in user["status_history"]:
            break
    if t:
        return t
    else:
        return False


def get_pre_test_info(user):
    return FlexSendMessage(
        alt_text=f"歡迎來到此聊天機器人實驗，請先點選下方連結閱讀實驗指引並確認開始實驗\n\nhttps://exp1.eason.best/starter?id={user['user_id']}\n\n完成後請點選「完成」",
        contents={
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://i.imgur.com/ufIifp6.png",
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "前測", "weight": "bold", "size": "xl"},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "點選下方「進行前測」做好感度評估，之後點選「下一步」繼續實驗",
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5,
                                    }
                                ],
                            }
                        ],
                    },
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "進行前測",
                            "uri": f"https://exp1.eason.best/pretest?id={user['user_id']}&test={user['status']}",
                        },
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": "下一步",
                            "text": "我已完成前測",
                        },
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [],
                        "margin": "sm",
                    },
                ],
                "flex": 0,
            },
        },
    )


def get_post_test_info(user):
    return FlexSendMessage(
        alt_text=f"後測",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "後測",
                        "weight": "bold",
                        "size": "xl",
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "點選下方「進行後測」並填寫量表，之後點選「下一步」繼續實驗",
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5,
                                    }
                                ],
                            }
                        ],
                    },
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "進行後測",
                            "uri": f"https://exp1.eason.best/posttest?id={user['user_id']}&test={user['status']}",
                        },
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": "下一步",
                            "text": "我已完成後測",
                        },
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [],
                        "margin": "sm",
                    },
                ],
                "flex": 0,
            },
        },
    )


def get_finish_info(user):
    return FlexSendMessage(
        alt_text=f"休息時間三分鐘",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "休息三分鐘",
                        "weight": "bold",
                        "size": "xl",
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "稍微休息一下，然後再次開始實驗吧。系統將於三分鐘後主動提醒您繼續實驗。您也可選擇「跳過休息」直接開始接下來的實驗",
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5,
                                    }
                                ],
                            }
                        ],
                    },
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": "跳過休息",
                            "text": "我決定跳過休息",
                        },
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [],
                        "margin": "sm",
                    },
                ],
                "flex": 0,
            },
        },
    )


def get_resting_finish_flexmsg(user):
    return FlexSendMessage(
        alt_text=f"休息時間到",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "休息時間到",
                        "weight": "bold",
                        "size": "xl",
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "提醒您，休息時間到了，可以繼續實驗囉，當然想再休息一下也沒問題～",
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5,
                                    }
                                ],
                            }
                        ],
                    },
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": "繼續實驗",
                            "text": "我準備好繼續了",
                        },
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [],
                        "margin": "sm",
                    },
                ],
                "flex": 0,
            },
        },
    )


change_topic_command_zh = [
    "換個話題",
]
change_topic_command_en = ["change topic"]


def increase_chat_sn(user_id):
    GPT3_chat_user_col.update_one({"user_id": user_id}, {"$inc": {"sn": 1}})


def process_command(event, text):
    user_id = event.source.user_id
    user = get_user(user_id)

    if user["status"] == "New Starter":
        if text == "我已完成閱讀":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="""偵測到您尚未完成閱讀，請閱讀完所有內容後於最下方點選「開始實驗」，收到頁面告知可以回來才算完成喔！"""
                ),
            )
        elif text == "Ready to go":
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='''已更新狀態為 "Ready to go"''')
            )
            update_user_status(user["user_id"], "Ready to go")
        else:
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text=f"歡迎來到此聊天機器人實驗，請先點選下方連結閱讀實驗指引並確認開始實驗\n\nhttps://exp1.eason.best/starter?id={user_id}\n\n完成後請點選「完成」",
                    contents={
                        "type": "bubble",
                        "hero": {
                            "type": "image",
                            "url": "https://i.imgur.com/ufIifp6.png",
                            "size": "full",
                            "aspectRatio": "20:13",
                            "aspectMode": "cover",
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "歡迎來到聊天機器人實驗",
                                    "weight": "bold",
                                    "size": "xl",
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "margin": "lg",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "box",
                                            "layout": "baseline",
                                            "spacing": "sm",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "點選下方「閱讀指引」觀看實驗說明並勾選同意，之後點選「下一步」開始實驗",
                                                    "wrap": True,
                                                    "color": "#666666",
                                                    "size": "sm",
                                                    "flex": 5,
                                                }
                                            ],
                                        }
                                    ],
                                },
                            ],
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "button",
                                    "style": "link",
                                    "height": "sm",
                                    "action": {
                                        "type": "uri",
                                        "label": "閱讀實驗指引",
                                        "uri": "https://exp1.eason.best/starter?id=userid",
                                    },
                                },
                                {
                                    "type": "button",
                                    "style": "link",
                                    "height": "sm",
                                    "action": {
                                        "type": "message",
                                        "label": "下一步",
                                        "text": "我已完成閱讀",
                                    },
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [],
                                    "margin": "sm",
                                },
                            ],
                            "flex": 0,
                        },
                    },
                ),
            )
        return True
    elif user["status"] == "Ready to go":
        # Arrange a group
        user["status"] = randomly_get_next_task(user)
        update_user_status(user["user_id"], user["status"])
        pre_test_info = get_pre_test_info(user)
        line_bot_api.reply_message(event.reply_token, pre_test_info)

        return True
    elif "Condition_" in user["status"] and "_Pretest" in user["status"]:
        if text == "我已完成前測":
            # Checking
            if True:
                user["status"] = user["status"].replace("_Pretest", "_Chatting")
                update_user_status(user["user_id"], user["status"])
                update_user_round(user, round=0)
                line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text="請開始十輪的聊天"),
                    ],
                )
                return True
            else:
                pass
        pre_test_info = get_pre_test_info(user)
        line_bot_api.reply_message(
            event.reply_token,
            [
                pre_test_info,
                TextSendMessage(text="請依照上方卡片指示，點選「進行前測」做好感度評估，之後點選「下一步」繼續實驗"),
            ],
        )
        return True
    elif "Condition_" in user["status"] and "_Finish" in user["status"]:
        if text not in ["我準備好繼續了", "我決定跳過休息"]:
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text=f"休息是為達到更好的實驗品質，如要跳過休息請點選上方的「跳過休息」"),
                ],
            )
            return True
        t = randomly_get_next_task(user)
        if t:
            user["status"] = t
            update_user_status(user["user_id"], user["status"])
            pre_test_info = get_pre_test_info(user)
            line_bot_api.reply_message(event.reply_token, pre_test_info)
        else:
            update_user_status(user["user_id"], "Final_Test")
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text=f"進入 Final Test"),
                ],
            )
    elif "Condition_" in user["status"] and "_Posttest" in user["status"]:
        if text == "我已完成後測":
            # Checking
            if True:
                user["status"] = user["status"].replace("_Posttest", "_Finish")
                update_user_status(user["user_id"], user["status"])
                # if (
                #     len(set(filter(lambda x: "_Chatting" in x, user["status_history"])))
                #     == Total_Conditions_Count
                # ):
                #     pass
                finish_info = get_finish_info(user)
                line_bot_api.reply_message(
                    event.reply_token,
                    [
                        finish_info,
                        TextSendMessage(text=f"狀態已更新為 {user['status']}"),
                    ],
                )
                from datetime import datetime

                now = datetime.now()
                Tmp_Resting_col.insert_one(
                    {
                        "user_id": user["user_id"],
                        "user_status": user["status"],
                        "timeStamp": now,
                        "skip": False,
                    }
                )
                time.sleep(10)
                res = Tmp_Resting_col.find_one(
                    {"user_id": user["user_id"], "timeStamp": now}
                )
                if res["skip"] == False:
                    line_bot_api.push_message(
                        user["user_id"],
                        [get_resting_finish_flexmsg(user)],
                    )
                return True
            else:
                pass
        post_test_info = get_post_test_info(user)
        line_bot_api.reply_message(
            user["user_id"],
            [
                post_test_info,
                TextSendMessage(text="請依照上方卡片指示，點選「進行後測」做好感度評估，之後點選「下一步」繼續實驗"),
            ],
        )
        return True
    elif text in change_topic_command_zh:
        increase_chat_sn(user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="""已更換話題，讓我們繼續聊天吧～\n如果我又持續說重複的話，請輸入「換個話題」以繼續對話"""),
        )
        return True
    elif text.lower() in change_topic_command_en:
        increase_chat_sn(user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text="""Topic changed, let's continue chatting.\nIf I keep saying weird things again, please enter 'change topic'."""
            ),
        )
        return True
    elif "Condition_" in user["status"] and "_Chatting" in user["status"]:
        user["round"] += 1
        update_user_round(user, round=user["round"])

        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text="收，但引擎還沒串"),
            ],
        )
        if user["round"] > 5:
            user["status"] = user["status"].replace("_Chatting", "_Posttest")
            post_test_info = get_post_test_info(user)
            line_bot_api.push_message(user["user_id"], post_test_info)
            update_user_status(user["user_id"], user["status"])

        return True

    return True
