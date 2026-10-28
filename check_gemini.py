from google import genai
from app.config import get_settings
from google.genai import types

s = get_settings()
print("model:", s.gemini_model, "| key starts with:", s.gemini_api_key[:4], "| key length:", len(s.gemini_api_key))
client = genai.Client(api_key=s.gemini_api_key)
print(client.models.generate_content(model=s.gemini_model, contents="Say hi").text)


client = genai.Client(
    api_key=s.gemini_api_key,
    http_options=types.HttpOptions(timeout=30000),  # milliseconds = 30 s
)