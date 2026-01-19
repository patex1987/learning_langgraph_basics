import asyncio
import uuid

from temporalio.client import Client

from adaptive_execution.executor.workflow import AdaptiveCodeExplainWorkflow

# CODE = """
# def retry(fn, retries=3):
#     for i in range(retries):
#         try:
#             return fn()
#         except Exception:
#             if i == retries - 1:
#                 raise
# """

with open("/home/patex1987/.config/JetBrains/PyCharm2025.3/scratches/ai_code_prompter.py") as f:
    CODE = f.read()

async def main():
    client = await Client.connect("localhost:7233")

    handle = await client.start_workflow(
        AdaptiveCodeExplainWorkflow.run,
        args=[CODE],
        id=f"adaptive_execution-{uuid.uuid4()}",
        task_queue="adaptive_execution",
    )

    await asyncio.sleep(10)
    await handle.signal(AdaptiveCodeExplainWorkflow.approve)

    result = await handle.result()
    for k, v in result.items():
        print(f"------\n ################ {k} ###############\n------\n")
        # History is a list of strings, print all of them
        if k == "history":
            if isinstance(v, list):
                print("\n".join(v))
            else:
                print(v)
            continue
        # For explanation and improvements, handle dict or string
        if isinstance(v, list) and len(v) > 0:
            if isinstance(v[0], dict) and "text" in v[0]:
                print(v[0]["text"])
            else:
                print(v[0])
        elif isinstance(v, str):
            print(v)
        else:
            print(v)

if __name__ == "__main__":
    asyncio.run(main())
