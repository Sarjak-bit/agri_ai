from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import ValidationError

from app import prompts
from app.config import get_settings
from app.schemas.analysis import AnalysisContext, AnalysisResponse, CropAssessment
from app.schemas.common import ErrorResponse, ResponseMeta
from app.services.gemini import generate_structured

router = APIRouter(tags=["analysis"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={
        413: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
    },
)
async def analyze(
    image: UploadFile = File(..., description="Photo of the crop (leaf, fruit or plant)"),
    context: str | None = Form(
        default=None, description="Optional AnalysisContext as a JSON string"
    ),
) -> AnalysisResponse:
    """One photo in; disease and nutrient assessment out."""
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(415, "Image must be JPEG, PNG or WebP")

    raw = await image.read()
    if not raw:
        raise HTTPException(422, "Image is empty")
    if len(raw) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "Image larger than 5 MB")

    ctx = None
    if context:
        try:
            ctx = AnalysisContext.model_validate_json(context)
        except ValidationError as exc:
            raise HTTPException(422, f"Invalid `context` JSON: {exc.errors()[0]['msg']}")

    assessment = generate_structured(
        system=prompts.ANALYSIS_SYSTEM,
        prompt=prompts.analysis_prompt(ctx),
        schema=CropAssessment,
        image=(raw, image.content_type),
    )
    return AnalysisResponse(
        assessment=assessment,
        meta=ResponseMeta(model=get_settings().gemini_model),
    )
