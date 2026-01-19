import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from workflow import CodeExplainWorkflow
from activities import generate_example_usage


async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="code-explainer",
        workflows=[CodeExplainWorkflow],
        activities=[generate_example_usage],
    )

    print("Temporal worker running…")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
