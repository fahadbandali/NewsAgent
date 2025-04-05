from typing import List, Optional
from pydantic import BaseModel
from twilio.rest import Client
from openai import OpenAI
from prompt_related import instructions, tools
from requests import get
import json
import os

# Models
class Article(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None


# Functions
def invoke_gpt(input: str, openai_client: OpenAI):
    response = openai_client.responses.create(
        model="gpt-4o-mini",
        instructions=instructions,
        input=input,
        tool_choice="auto",
        max_output_tokens=300,
        tools=tools
    )

    if response.error != None:
        return 'An Error occurred'

    output = response.output[0]

    if output.type == 'function_call':
        arguments = json.loads(output.arguments)
        if output.name == 'get_headlines':
            category = arguments.get('category')
            data = get_headlines(category)
            return invoke_gpt(f"The results from the News API of all headlines regarding the category in english: {str(data)}")
    else:
        return response.output_text

def get_headlines(category: str) -> List[Article]:
    news_key = os.getenv("NEWS_API_KEY", "MISSING")
    response = get(f'https://newsapi.org/v2/top-headlines?category={category}&language=en&apiKey={news_key}')
    if response.status_code == 200:
        decoded_response = response.content.decode('utf8')
        json_response = json.loads(decoded_response)
        articles_to_parse = json_response.get('articles')
        data = [Article(**article_data) for article_data in articles_to_parse]
        return data
    else:
        print("failed to get response")

def send_sms(message: str, sender: str, receiver: str, twilio_client: Client):
    try:
        twilio_client.messages.create(
            from_=sender,
            to=receiver,
            body=message
        )
    except Exception as e:
        print(f"Error sending SMS: {e}")

