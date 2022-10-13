import secrets
from tokenize import tabsize
from lib.common import line_bot_api, handler, doThreading
from lib.db import (
    GPT3_chat_user_col,
    GPT3_chat_bots_col,
    GPT3_chat_history_col,
    get_user,
    Total_Conditions_Count,
    Resting_Notify_col,
    TAG_col,
    ALL_STATUS,
)
from lib.imp import *
import requests
import time
import json
from lib.common import process_tag
from lib.chat_zh_handler import send_GPT3_response as send_zh_GPT3_response
from lib.chat_en_handler import send_GPT3_response as send_en_GPT3_response


def process_text_message(event):
    text = event.message.text

    if process_command(event, text):
        return True

    print("QQQQQQQ")


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


def get_how_many_tasks_left(user):
    tasks = list(filter(lambda x: "Condition_" in x and "_Finish" in x, ALL_STATUS))
    user_finished = list(
        filter(lambda x: "Condition_" in x and "_Finish" in x, user["status_history"])
    )
    user_finished.append(user["status"])
    return len(set(tasks) - set(user_finished))


def randomly_get_next_task(user):
    tasks = list(filter(lambda x: "Condition_" in x and "_Pretest" in x, ALL_STATUS))
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
        alt_text=f"請使用支援的裝置繼續",
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
                                        "text": "稍微休息一下，然後再次開始實驗吧！休息的目的是要放鬆身心，排除先前實驗對後續實驗的干擾。系統將於三分鐘後主動提醒您繼續實驗。您也可選擇「跳過休息」直接開始下一階段",
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


def get_final_flexmsg(user):
    return FlexSendMessage(
        alt_text=f"最終問卷",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "最終量表測驗與資料填寫",
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
                                        "text": "點選下方「進行最終問卷」並填寫，之後點選「結束」結束所有實驗流程",
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
                            "label": "進行最終問卷",
                            "uri": f"https://exp1.eason.best/final?id={user['user_id']}&test=Final_Test",
                        },
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": "結束",
                            "text": "我已完成所有實驗流程",
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
    "刷新",
]
change_topic_command_en = ["change topic"]


def increase_chat_sn(user_id):
    GPT3_chat_user_col.update_one({"user_id": user_id}, {"$inc": {"sn": 1}})


def process_command(event, text):
    user_id = event.source.user_id
    user = get_user(user_id)

    if user["status"] == "New_Starter":
        if text == "我已完成初始階段":
            res = requests.get(
                f"https://exp1.eason.best/api/v1/starter/isfinish?userId={user['user_id']}"
            )
            isFinish = res.json()["isFinish"]
            if isFinish:
                user["status"] = randomly_get_next_task(user)
                update_user_status(user["user_id"], user["status"])
                pre_test_info = get_pre_test_info(user)
                line_bot_api.reply_message(event.reply_token, pre_test_info)
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="""偵測到您尚未完成閱讀，請閱讀完所有內容後於最下方點選「開始實驗」，收到頁面告知可以回來才算完成喔！"""
                    ),
                )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                [
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
                                                        "text": "點選下方「進行初始階段」觀看實驗說明並勾選同意，並且填寫資料，之後點選「下一步」繼續實驗",
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
                                            "label": "進行初始階段",
                                            "uri": f"https://exp1.eason.best/starter?id={user_id}&test=New_Starter",
                                        },
                                    },
                                    {
                                        "type": "button",
                                        "style": "link",
                                        "height": "sm",
                                        "action": {
                                            "type": "message",
                                            "label": "下一步",
                                            "text": "我已完成初始階段",
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
                    TextSendMessage("歡迎來到此聊天機器人實驗，請先點選上方「閱讀實驗指引」並完成，之後選擇「下一步」開始實驗"),
                ],
            )
        return True
    elif "Condition_" in user["status"] and "_Pretest" in user["status"]:
        if text == "我已完成前測":
            res = requests.get(
                f"https://exp1.eason.best/api/v1/pretest/isfinish?userId={user['user_id']}&status={user['status']}"
            )
            isFinish = res.json()["isFinish"]
            if isFinish:
                user["status"] = user["status"].replace("_Pretest", "_Chatting")
                update_user_status(user["user_id"], user["status"])
                update_user_round(user, round=0)
                line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text="請開始十輪的聊天"),
                        # TextSendMessage(text="此為純文字聊天，不建議使用貼圖與表情符號"),
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
                TextSendMessage(text="偵測到您尚未完成前測"),
            ],
        )
        return True
    elif "Condition_" in user["status"] and "_Finish" in user["status"]:
        if text == "我決定跳過休息":
            notify = sorted(
                list(Resting_Notify_col.find()),
                key=lambda x: x["timeStamp"],
                reverse=True,
            )[0]
            Resting_Notify_col.update_one(notify, {"$set": {"skip": True}})
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
                    get_final_flexmsg(user),
                ],
            )
    elif "Condition_" in user["status"] and "_Posttest" in user["status"]:
        if text == "我已完成後測":
            res = requests.get(
                f"https://exp1.eason.best/api/v1/posttest/isfinish?userId={user['user_id']}&status={user['status']}"
            )
            isFinish = res.json()["isFinish"]
            if isFinish:
                user["status"] = user["status"].replace("_Posttest", "_Finish")
                update_user_status(user["user_id"], user["status"])

                finish_info = get_finish_info(user)
                tasks_left_num = get_how_many_tasks_left(user)
                line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(
                            text=f"感謝您的參與，請稍微休息一下，您還有 {tasks_left_num } 輪聊天實驗要完成"
                        ),
                        finish_info,
                    ],
                )
                from datetime import datetime

                now = datetime.now()
                Resting_Notify_col.insert_one(
                    {
                        "user_id": user["user_id"],
                        "user_status": user["status"],
                        "timeStamp": now,
                        "skip": False,
                    }
                )
                time.sleep(60 * 3)
                res = Resting_Notify_col.find_one(
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
            event.reply_token,
            [
                post_test_info,
                TextSendMessage(text="請依照上方卡片指示，點選「進行後測」，之後點選「下一步」繼續實驗"),
            ],
        )
        return True
    elif "Finish" == user["status"]:
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text="感謝您完成所有實驗流程，受試者報酬將於一週後匯款給您。"),
                TextSendMessage(text="如有任何疑問或其他回饋請 Email 至主持人 eason.tw.chen@gmail.com"),
            ],
        )
    elif "Final_Test" == user["status"]:
        res = requests.get(
            f"https://exp1.eason.best/api/v1/final/isfinish?userId={user['user_id']}&status={user['status']}"
        )
        isFinish = res.json()["isFinish"]
        if isFinish:
            update_user_status(user["user_id"], "Finish")
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text="感謝您完成所有實驗流程，受試者報酬將於一週後匯款給您。"),
                ],
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                [
                    get_final_flexmsg(user),
                    TextSendMessage(
                        text="偵測到您尚未完成最終資料填寫，請點選上方之「進行最終問卷」並填寫完成送出，才能完成實驗收到受試者報酬喔～"
                    ),
                ],
            )
        pass
    elif text in change_topic_command_zh:
        requests.post(
            "https://exp1.eason.best/api/v1/behavior/changeTopic",
            data=json.dumps({"userId": user_id}),
        )
        increase_chat_sn(user_id)
        update_user_round(user, round=user["round"] - 1)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="""讓我們繼續聊天吧～\n如果聊天對象又持續說重複的話，請輸入「刷新」以繼續對話"""),
        )
        return True
    # elif text.lower() in change_topic_command_en:
    #     increase_chat_sn(user_id)
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(
    #             text="""Topic changed, let's continue chatting.\nIf I keep saying weird things again, please enter 'change topic'."""
    #         ),
    #     )
    #     return True
    elif "Condition_" in user["status"] and "_Chatting" in user["status"]:
        if "＠" == text[0] and process_tag(user, event):
            return True
        user["round"] += 1
        update_user_round(user, round=user["round"])

        if "Z_Chatting" in user["status"]:

            send_zh_GPT3_response(text, event)
        else:
            send_en_GPT3_response(text, event)
        if user["round"] == 10:
            start_posttest(user)
        return True

    return True


def start_posttest(user):
    user["status"] = user["status"].replace("_Chatting", "_Posttest")
    post_test_info = get_post_test_info(user)
    line_bot_api.push_message(user["user_id"], post_test_info)
    update_user_status(user["user_id"], user["status"])
