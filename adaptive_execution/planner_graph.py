from langchain_core.language_models import BaseChatModel
from langgraph.constants import END
from langgraph.graph import StateGraph

from adaptive_execution.domain.contracts import Step, PlannerState, PlannerDecision

PLANNER_PROMPT_TEMPLATE = """
You are deciding the NEXT STEP in a code explainer workflow.

Rules:
- You may return ONE step only.
- If explanation is missing → explain
- If explanation exists but no improvements → improve
- If explanation + improvements exist and no human approval → human_approval
- If everything done → done

History:
{history}

CODE:
{code}
"""


class PlannerActivityGraph:

    def __init__(self, planner_llm: BaseChatModel):
        self.planner_llm = planner_llm

    def compile_planner_graph(self):
        g = StateGraph(PlannerState)
        g.add_node("decide", self.decide)
        g.set_entry_point("decide")
        g.add_edge("decide", END)

        graph = g.compile()
        return graph

    async def decide(self, state: PlannerState):
        prompt = PLANNER_PROMPT_TEMPLATE.format(
            history=state["history"],
            code=state["code"]
        )
        
        structured_llm = self.planner_llm.with_structured_output(PlannerDecision)
        decision = await structured_llm.ainvoke(prompt)

        return {
            "step": Step(
                kind=decision.kind,
                reason=decision.reason,
                idempotency_key=f"{decision.kind}-{len(state['history'])}",
            )
        }
