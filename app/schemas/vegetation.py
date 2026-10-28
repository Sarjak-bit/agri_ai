from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import GrowthStage, ResponseMeta

VegetationCondition = Literal["healthy", "moderate_stress", "severe_stress", "unclear"]


class VegetationRequest(BaseModel):
    ndvi: float = Field(ge=-1, le=1)
    evi: float = Field(ge=-1, le=3)
    ndre: float = Field(ge=-1, le=1)
    ci_rededge: float = Field(ge=-1, le=20)
    ndwi: float = Field(ge=-1, le=1)
    lswi: float = Field(ge=-1, le=1)
    lst: float = Field(ge=-30, le=80, description="Land surface temperature in °C")

    crop: str | None = None
    growth_stage: GrowthStage | None = None


class VegetationAssessment(BaseModel):
    condition: VegetationCondition
    vigor_summary: str
    water_status: Literal["adequate", "low", "unclear"]
    heat_status: Literal["normal", "elevated", "high"]
    reasons: list[str]
    recommended_actions: list[str]
    data_gaps: list[str]


class VegetationResponse(BaseModel):
    assessment: VegetationAssessment
    meta: ResponseMeta