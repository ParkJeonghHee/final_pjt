import requests
from django.conf import settings

GMS_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"

def gms_chat_completion(messages, model="gpt-5-nano"):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.GMS_KEY}",
    }
    payload = {
        "model": model,
        "messages": messages,
    }

    res = requests.post(
        GMS_URL, 
        headers=headers, 
        json=payload, 
        timeout=(10, 90),
    )
    
    if res.status_code != 200:
        raise Exception(f"GMS OpenAI Error {res.status_code}: {res.text}")

    return res.json()