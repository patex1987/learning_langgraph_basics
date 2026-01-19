import asyncio
import uuid
from datetime import datetime

from temporalio.client import Client

from plan_then_execute.di.factories.default import create_planner_chat_model
from plan_then_execute.executor.workflow import CodeExplainWorkflow
from plan_then_execute.planner_graph import ExecutionPlanner

CODE = """
def retry(fn, retries=3):
    for i in range(retries):
        try:
            return fn()
        except Exception:
            if i == retries - 1:
                raise
"""


async def main():
    # ---------- LangGraph planning ----------
    planner = ExecutionPlanner(planner_llm=create_planner_chat_model())
    graph = planner.compile_planner_graph()
    # TODO: yeah, i know i should use a logger, but that is not the point of this learning
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print(f'[{timestamp}] graph constructed')

    state = await graph.ainvoke(
        {
            "code": CODE,
            "iteration": 0,
            "approved": False,
        },
        # config={"configurable": {"model": "gpt-4o-mini"}},
    )

    explanation = state["explanation"]
    plan = state["plan"]

    print("\nFINAL EXPLANATION (from LangGraph):\n")
    print(explanation)

    print("\nLLM prepared the following plan:\n")
    print(plan)

    # ---------- Temporal execution ----------
    # TODO: missing configuration
    client = await Client.connect("localhost:7233")
    workflow_id = f"code-explain-{uuid.uuid4()}"

    handle = await client.start_workflow(
        CodeExplainWorkflow.run,
        args=[CODE, plan, explanation],
        id=workflow_id,
        task_queue="code-explainer",
    )


    print("Do you want to approve the llm tool usage?\n")
    print("[y]- Ask a question")
    print("[n]- Exit")
    choice = input("Enter your choice: ")
    if choice in ["y", "yes", "Y", "YES"]:
        await handle.signal(
            signal=CodeExplainWorkflow.approve,
            args=["user approved"],
        )
        result = await handle.result()

        print("\n--- FINAL RESULT ---\n")
        for k, v in result.items():
            print(f"\n{k}: {v}")

    elif choice in ["n", "no", "N", "NO"]:
        print("Cancelling workflow...")
        await handle.cancel()
        print("Workflow cancelled. Goodbye!")
        exit()
    else:
        print("Invalid choice")
        # start()

    # Simulated human approval

if __name__ == "__main__":
    asyncio.run(main())
