from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import GrowthStage, Likelihood, ResponseMeta

OverallHealth = Literal["healthy", "mild_issue", "moderate_issue", "severe_issue", "unclear"]
Nutrient = Literal["nitrogen", "phosphorus", "potassium", "magnesium", "iron", "other"]


# ---------- request: everything except the image is optional ----------
class AnalysisContext(BaseModel):
    """Optional extra info. The farmer can skip all of it."""

    crop: str | None = Field(default=None, examples=["tomato"])
    growth_stage: GrowthStage | None = None
    notes: str | None = Field(default=None, max_length=500)

    temp_c: float | None = Field(default=None, ge=-30, le=60)
    humidity_pct: float | None = Field(default=None, ge=0, le=100)
    rainfall_7d_mm: float | None = Field(default=None, ge=0)

    soil_n_mg_kg: float | None = Field(default=None, ge=0)
    soil_p_mg_kg: float | None = Field(default=None, ge=0)
    soil_k_mg_kg: float | None = Field(default=None, ge=0)
    soil_ph: float | None = Field(default=None, ge=0, le=14)


# ---------- what Gemini must return (used as response_schema) ----------
# No default values here: Gemini's schema support is stricter than Pydantic's.
class ImageCheck(BaseModel):
    is_plant_image: bool
    usable: bool = Field(description="True if the photo is clear enough to assess")
    issues: list[str] = Field(description="e.g. blurry, too dark, no leaf visible")


class DiseaseFinding(BaseModel):
    name: str
    likelihood: Likelihood
    evidence: list[str] = Field(description="Symptoms actually visible in the photo")


class NutrientFinding(BaseModel):
    nutrient: Nutrient
    likelihood: Likelihood
    evidence: list[str]


class CropAssessment(BaseModel):
    image_check: ImageCheck
    crop_identified: str = Field(description="'unknown' if it cannot be told")
    overall_health: OverallHealth
    visible_symptoms: list[str]
    diseases: list[DiseaseFinding]
    nutrient_issues: list[NutrientFinding]
    alternative_causes: list[str] = Field(
        description="Other causes (water stress, pests, sunburn, herbicide) that "
        "could explain the same signs"
    )
    recommended_actions: list[str]
    confirmation_tests: list[str]
    data_gaps: list[str]


# ---------- what the API returns ----------
class AnalysisResponse(BaseModel):
    assessment: CropAssessment
    meta: ResponseMeta
