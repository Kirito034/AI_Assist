from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus,
)
from backend.Model import FirstLayerDMM
from backend.Automation import Automation
from backend.SpeechToText import SpeechRecognition
from backend.Chatbot import ChatBot
from backend.TextToSpeech import TextToSpeech
from backend.RealtimeSearchEngine import RealtimeInformation
from dotenv import dotenv_values
from asyncio import run
from datetime import datetime
from time import sleep
import subprocess
import threading
import json
import os

# Load environment variables
env_vars = dotenv_values(".env")

# Get user and assistant names
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")

# Define the default message
DefaultMessage = f'''{Username}: Hello {Assistantname}, How are you?
{Assistantname}: Welcome {Username}. I am doing well. How may I help you?'''

# Initialize subprocesses and functions
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    with open(r'Data\ChatLog.json', "r", encoding='utf-8') as file:
        if len(file.read().strip()) < 5:
            with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as db_file:
                db_file.write("")
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as resp_file:
                resp_file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def ChatLogIntegration():
    formatted_chatlog = ""
    json_data = ReadChatLogJson()
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"{Username}: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"{Assistantname}: {entry['content']}\n"
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
        Data = file.read()
    if Data:
        with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as resp_file:
            resp_file.write(Data)

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    current_hour = datetime.now().hour
    greeting = (
        "Good Morning" if current_hour < 12 else
        "Good Afternoon" if current_hour < 18 else
        "Good Evening"
    )
    ShowTextToScreen(f"{greeting}, Sir. How can I assist you?")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""
    SetAssistantStatus("Listening ... ")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username}: {Query}")
    SetAssistantStatus("Thinking ... ")
    Decision = FirstLayerDMM(Query)
    print(f"Decision: {Decision}")

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)
    Merged_query = " and ".join(
        " ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")
    )

    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    if not TaskExecution:
        for queries in Decision:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True

    if ImageExecution:
        with open(r"Frontend/Files/ImageGeneratoion.data", "w") as file:
            file.write(f"{ImageGenerationQuery}, True")
        try:
            p1 = subprocess.Popen(
                ['python', r'Backend/ImageGeneration.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False
            )
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")

    if G and R or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeInformation(QueryModifier(Merged_query))
        ShowTextToScreen(f"{Assistantname}: {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True
    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking ...")
                QueryFinal = Queries.replace("general", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                return True

            elif "realtime" in Queries:
                SetAssistantStatus("Searching ...")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeInformation(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                return True

            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                os._exit(1)

def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available...")

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
