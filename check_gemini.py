from google import genai
from app.config import get_settings

s = get_settings()
print("model:", s.gemini_model, "| key starts with:", s.gemini_api_key[:4], "| key length:", len(s.gemini_api_key))
client = genai.Client(api_key=s.gemini_api_key)
print(client.models.generate_content(model=s.gemini_model, contents="Say hi").text)