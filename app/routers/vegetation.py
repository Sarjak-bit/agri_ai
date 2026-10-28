from fastapi import APIRouter

from app import prompts
from app.config import get_settings
from app.schemas.common import ErrorResponse, ResponseMeta
from app.schemas.vegetation import (
    VegetationAssessment,
    VegetationRequest,
    VegetationResponse,
)
from app.services.gemini import generate_structured

router = APIRouter(tags=["vegetation"])


@router.post(
    "/vegetation",
    response_model=VegetationResponse,
    responses={502: {"model": ErrorResponse}},
)
def vegetation(req: VegetationRequest) -> VegetationResponse:
    """Satellite index values in; vegetation condition out."""
    assessment = generate_structured(
        system=prompts.VEGETATION_SYSTEM,
        prompt=prompts.vegetation_prompt(req),
        schema=VegetationAssessment,
    )
    return VegetationResponse(
        assessment=assessment,
        meta=ResponseMeta(
            model=get_settings().gemini_model,
            disclaimer=(
                "LLM-generated interpretation of satellite index values, not a "
                "validated diagnosis. Confirm with a field inspection."
            ),
        ),
    )