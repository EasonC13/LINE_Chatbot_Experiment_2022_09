from lib.common import line_bot_api, doThreading


from google.cloud import speech
import sys, pathlib
from pydub import AudioSegment
import requests
import json
import os
import uuid
import datetime
import numpy as np

import io


def voice_reco(client, filename):
    with io.open(filename, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="zh-TW",
    )
    response = client.recognize(config=config, audio=audio)
    try:
        text = response.results[0].alternatives[0].transcript
    except:
        text = ""
    return text


def process_voice_file(file_path):
    text = ""
    try:
        # Instantiates a client
        client = speech.SpeechClient.from_service_account_json(
            os.getenv("GOOGLE_SERVICE_JSON_PATH")
        )
        # Detects speech in the audio file
        wav = AudioSegment.from_wav(f"{file_path}.wav")
        if wav.duration_seconds < 60:
            text = voice_reco(client, f"{file_path}.wav")

            all_texts = [text]
        else:
            text = "too long... can't recognize..."
            wav_files = []
            while wav.duration_seconds > 60:
                temp_filename = str(uuid.uuid4())
                temp_filename = f"{file_path}.wav"
                slice_wav = wav[0:59]
                slice_wav.export(temp_filename, format="wav")
                wav_files.append(temp_filename)
                wav = wav[57:]
            temp_filename = str(uuid.uuid4())
            temp_filename = f"{file_path}.wav"
            wav.export(temp_filename, format="wav")
            wav_files.append(temp_filename)
            all_texts = []
            for wav_file in wav_files:
                text = voice_reco(client, wav_file)
                all_texts.append(text)
                os.remove(wav_file)

            # response = client.long_running_recognize(config=config, audio=audio)
            # response = operation.result(timeout=90)
            # text = response.results[0].alternatives[0].transcript
        # AAA.append(response)
        text = "".join(all_texts)

        os.remove(f"{file_path}.wav")
        os.remove(f"{file_path}")
    except ValueError as e:
        import traceback
        import sys

        exc_type, exc_value, exc_tb = sys.exc_info()
        text = "[ERROR]\n" + "".join(
            traceback.format_exception(exc_type, exc_value, exc_tb)
        )
        """if update.message.chat.id in User_List:
            result = "[ERROR]\n" + "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            bot.edit_message_text(text = result, message_id=reply_msg.message_id, chat_id= reply_msg.chat_id)
        else:
            result = "Error, Might be no detectable text in the voice message. If you think this is an error otherwise, please contect the author @EasonC13"
            bot.edit_message_text(text = result, message_id=reply_msg.message_id, chat_id= reply_msg.chat_id)"""

    return text


from lib.chat_zh_handler import send_GPT3_response
import subprocess


def process_voice_message(event):
    # AAA.append(event)
    file_path = f"/tmp/{uuid.uuid4()}"

    message_content = line_bot_api.get_message_content(event.message.id)

    with open(file_path, "wb") as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    subprocess.call(
        f"ffmpeg -i {file_path} {file_path}.wav",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    text = process_voice_file(file_path)
    send_GPT3_response(text=text, event=event)
