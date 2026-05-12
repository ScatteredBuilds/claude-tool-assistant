from typing import Literal

from pydantic import BaseModel, Field


RiskLevel = Literal["low", "medium", "high"]


class AssistantResult(BaseModel):
    summary: str = Field(description="Short summary of the user request or incident note.")
    risk_level: RiskLevel
    reasoning: str = Field(description="Brief explanation for the classification.")
    tool_used: bool
    raw_response_path: str
