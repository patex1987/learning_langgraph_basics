from typing import Literal

from openai import BaseModel


class CodeExplainPlan(BaseModel):
    """
    How to execute the code explanation.
    """
    explanation_type: Literal["concise", "verbose"]
    focus_area: Literal["performance", "quality", "readability"]


class CritiqueResult(BaseModel):
    """
    Result of critiquing an explanation.
    """
    approved: bool
    feedback: str | None = None


class ExecutionDraft(BaseModel):
    explanation: str
    approved: bool = False
    reviewer_notes: str | None = None