from typing import TypeVar

from fastapi import HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError

from app.config import get_settings

T = TypeVar("T", bound=BaseModel)

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=get_settings().gemini_api_key)
    return _client


def generate_structured(
    *,
    system: str,
    prompt: str,
    schema: type[T],
    image: tuple[bytes, str] | None = None,
) -> T:
    """Call Gemini and return a validated `schema` instance.

    image: optional (raw_bytes, mime_type).
    Raises HTTPException(502) if Gemini fails or returns invalid output.
    """
    contents: list = [prompt]
    if image is not None:
        data, mime = image
        contents.append(types.Part.from_bytes(data=data, mime_type=mime))

    try:
        resp = _get_client().models.generate_content(
            model=get_settings().gemini_model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system,
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0,
            ),
        )
    except Exception as exc:  # rate limit, auth, network, safety block...
        raise HTTPException(status_code=502, detail=f"Gemini request failed: {exc}")

    if isinstance(resp.parsed, schema):
        return resp.parsed
    try:
        return schema.model_validate_json(resp.text or "")
    except (ValidationError, ValueError):
        raise HTTPException(status_code=502, detail="Gemini returned invalid output")
