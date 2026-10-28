from google import genai
from google.genai import types
from app.config import get_settings

s = get_settings()
client = genai.Client(
    api_key=s.gemini_api_key,
    http_options=types.HttpOptions(timeout=20000),
)

names = [
    m.name.removeprefix("models/")
    for m in client.models.list()
    if "generateContent" in (m.supported_actions or [])
    and ("flash" in m.name or "pro" in m.name)
    and "image" not in m.name and "tts" not in m.name
]

for name in names:
    try:
        r = client.models.generate_content(model=name, contents="Say hi")
        print("OK  ", name, "->", r.text.strip()[:30])
    except Exception as e:
        print("FAIL", name, "->", str(e)[:80])