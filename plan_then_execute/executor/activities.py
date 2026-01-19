from temporalio import activity

EXAMPLE_USAGE_PROMPT_TEMPLATE = """
Generate a short example usage for the following code:

CODE:
{code}
"""


@activity.defn
async def generate_example_usage(code: str) -> str:
    from plan_then_execute.di.factories.default import create_executor_chat_model

    llm = create_executor_chat_model()

    prompt = EXAMPLE_USAGE_PROMPT_TEMPLATE.format(code=code)

    result = await llm.ainvoke(prompt)
    return result.content
