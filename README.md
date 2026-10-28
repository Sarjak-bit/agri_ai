# Agri AI Service (FastAPI + Gemini)

The farmer uploads one crop photo. A single Gemini call checks for both plant
diseases and nutrient deficiencies. This is LLM inference, not a trained model.

## Run

    python -m venv .venv && .venv\Scripts\activate     # Windows
    pip install -r requirements.txt
    copy .env.example .env                              # then put your real key in .env
    uvicorn app.main:app --reload

Open http://127.0.0.1:8000/docs to try it.

## Endpoint

`POST /analyze` (multipart/form-data)

| Field     | Required | Notes                                                  |
|-----------|----------|--------------------------------------------------------|
| `image`   | yes      | JPEG/PNG/WebP, max 5 MB                                |
| `context` | no       | JSON string of `AnalysisContext` (crop, stage, weather, soil values, notes) |

Everything in `context` is optional. With only an image, Gemini identifies the crop itself.

Response: `assessment` (image check, crop, overall health, visible symptoms,
disease findings, nutrient findings, alternative causes, actions,
confirmation tests, data gaps) plus `meta` (model, disclaimer).

Example from a script:

    curl -X POST http://127.0.0.1:8000/analyze -F "image=@leaf.jpg" \
         -F 'context={"crop":"tomato","humidity_pct":88}'

## Layout

    app/
      main.py             app + router registration
      config.py           settings from .env
      prompts.py          system prompt + prompt builder
      schemas/
        common.py         shared types, ResponseMeta, ErrorResponse
        analysis.py       AnalysisContext (input), CropAssessment (Gemini output), AnalysisResponse
      services/gemini.py  only file that calls Gemini (temperature 0, JSON schema)
      routers/analysis.py POST /analyze

## Notes

- Call this service from your Django backend, never from the browser; keep the API key server-side.
- Findings are likelihood levels, not probabilities. LLM confidence is not calibrated.
- A photo alone cannot confirm a nutrient deficiency or a specific disease. The prompt forces alternative causes and confirmation tests.
- Gemini failure returns 502; fall back to your rule-based result in Django.
- Before claiming accuracy, test on 20-50 labeled photos (e.g. PlantVillage) and measure agreement.
