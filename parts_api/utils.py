import asyncio
from asyncio import Task
from typing import AsyncGenerator, Coroutine, Any, TypeVar

T = TypeVar("T")


async def parallelize(
    coroutine_generator: AsyncGenerator[Coroutine[Any, Any, T], Any],
    parallel_task_count: int,
) -> AsyncGenerator[Task[T], None]:
    tasks = set()
    async for coroutine in coroutine_generator:
        new_task = asyncio.create_task(coroutine)
        tasks.add(new_task)
        if len(tasks) < parallel_task_count:
            continue

        done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            yield task

    if tasks:
        done, _ = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
        for task in done:
            yield task
