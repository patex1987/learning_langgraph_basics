from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy


# from activities import generate_example_usage
from plan_then_execute.domain.contracts import ExecutionDraft, CodeExplainPlan


@workflow.defn
class CodeExplainWorkflow:
    def __init__(self):
        self.draft: ExecutionDraft | None = None

    @workflow.run
    async def run(
        self,
        code: str,
        plan: CodeExplainPlan,
        explanation: str,
    ) -> dict:
        self.draft = ExecutionDraft(explanation=explanation)

        await workflow.wait_condition(lambda: self.draft.approved)

        example = await workflow.execute_activity(
            "generate_example_usage",
            code,
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

        return {
            "final_explanation": self.draft.explanation,
            "reviewer_notes": self.draft.reviewer_notes,
            "example_usage": example,
        }

    @workflow.signal
    async def approve(self, notes: str | None = None):
        self.draft.approved = True
        self.draft.reviewer_notes = notes

    @workflow.signal
    async def revise(self, new_explanation: str, notes: str | None = None):
        self.draft.explanation = new_explanation
        self.draft.reviewer_notes = notes
