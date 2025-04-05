from fastapi import FastAPI, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from twilio.rest import Client
from helper import invoke_gpt, send_sms

app = FastAPI()

# env
load_dotenv('.env')
key = os.getenv("OPENAI_API_KEY", "MISSING")

TWILIO_API_SID = os.getenv("TWILIO_API_SID", "Missing")
TWILIO_API_SECRET = os.getenv("TWILIO_API_SECRET", "Missing")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "Missing")

SENDER_NUMBER = os.getenv("PHONE_NUMBER_FROM", "Missing")

# clients
gpt = OpenAI(api_key=key)
twilio_client = Client(username=TWILIO_API_SID,password=TWILIO_API_SECRET,account_sid=TWILIO_ACCOUNT_SID)

# Server
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/headlines", response_model=str)
def summarize_news(type: str = '', receiver: str = '') -> str:
    input = f"Can you give me a summary of the headlines regarding: {type}"
    result = invoke_gpt(input, gpt)
    send_sms(result, SENDER_NUMBER, "+1" + receiver, twilio_client)
    print('Delivered the message!')

    return result
