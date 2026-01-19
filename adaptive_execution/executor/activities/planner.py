from temporalio import activity


from adaptive_execution.domain.contracts import PlannerInput, PlannerOutput
from adaptive_execution.planner_graph import PlannerActivityGraph


@activity.defn
async def plan_next_step(inp: PlannerInput) -> PlannerOutput:
    """
    Pure planning activity:
    - no side effects
    - returns one step
    """
    from adaptive_execution.di.factories.default import create_planner_chat_model
    llm = create_planner_chat_model()
    graph = PlannerActivityGraph(llm).compile_planner_graph()
    
    out = await graph.ainvoke({
        "code": inp.code,
        "history": inp.history,
        "step": None,
    })

    return PlannerOutput(step=out["step"])
