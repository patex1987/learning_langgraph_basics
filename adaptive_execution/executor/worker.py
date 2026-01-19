import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from adaptive_execution.executor.activities.executor import execute_step
from adaptive_execution.executor.activities.planner import plan_next_step
from workflow import AdaptiveCodeExplainWorkflow



async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="adaptive_execution",
        workflows=[AdaptiveCodeExplainWorkflow],
        activities=[plan_next_step, execute_step],
    )

    print("Worker running…")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
