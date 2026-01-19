from typing import Literal, Optional, TypedDict
from pydantic import BaseModel


class PlannerInput(BaseModel):
    code: str
    history: list[str]
    step_budget_remaining: int


class Step(BaseModel):
    kind: Literal["explain", "improve", "example", "human_approval", "done"]
    reason: str
    idempotency_key: str


class PlannerOutput(BaseModel):
    step: Step


class PlannerDecision(BaseModel):
    """Structured output from the LLM for deciding next step."""
    kind: Literal["explain", "improve", "human_approval", "done"]
    reason: str


class ExecutionState(BaseModel):
    explanation: Optional[str] = None
    improvements: Optional[str] = None
    approved: bool = False


class PlannerState(TypedDict):
    code: str
    history: list[str]
    step: Step | None
