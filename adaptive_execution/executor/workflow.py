from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

from adaptive_execution.domain.contracts import ExecutionState, PlannerInput

MAX_STEPS = 6

@workflow.defn
class AdaptiveCodeExplainWorkflow:
    def __init__(self):
        self.state = ExecutionState()
        self.history: list[str] = []

    @workflow.run
    async def run(self, code: str) -> dict:
        for i in range(MAX_STEPS):
            planner_output = await workflow.execute_activity(
                "plan_next_step",
                PlannerInput(
                    code=code,
                    history=self.history,
                    step_budget_remaining=MAX_STEPS - i,
                ),
                start_to_close_timeout=timedelta(seconds=30),
            )

            planned_step = planner_output["step"]

            planned_step_kind = planned_step["kind"]

            self.history.append(planned_step_kind)

            if planned_step_kind == "done":
                break

            if planned_step_kind == "human_approval":
                await workflow.wait_condition(lambda: self.state.approved)
                continue

            execute_step_output = await workflow.execute_activity(
                "execute_step",
                args=[planned_step, code],
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )

            if planned_step_kind == "explain":
                self.state.explanation = execute_step_output
            elif planned_step_kind == "improve":
                self.state.improvements = execute_step_output

        return {
            "explanation": self.state.explanation,
            "improvements": self.state.improvements,
            "history": self.history,
        }

    @workflow.signal
    async def approve(self):
        self.state.approved = True