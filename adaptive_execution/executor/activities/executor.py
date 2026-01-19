
from temporalio import activity

from adaptive_execution.domain.contracts import Step


@activity.defn
async def execute_step(step: Step, code: str) -> str:
    from adaptive_execution.di.factories.default import create_executor_chat_model
    llm = create_executor_chat_model()

    if step.kind == "explain":
        prompt = f"Explain this code:\n{code}"
    elif step.kind == "improve":
        prompt = f"Suggest improvements for this code:\n{code}"
    elif step.kind == "example":
        prompt = f"Give an example usage of this code:\n{code}"
    else:
        return ""

    result = await llm.ainvoke(prompt)
    return result.content
