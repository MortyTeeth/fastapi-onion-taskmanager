import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from task_service.src.broker.connection import get_rabbitmq_channel
from task_service.src.repositories.task import TaskRepository
from task_service.src.utils.unit_of_work import UnitOfWork
import json
import logging

logger = logging.getLogger(__name__)

QUEUE_NAME = "task_service.rpc.stats"


async def _handle_user_stats_request(message: AbstractIncomingMessage):
    async with message.process():
        try:
            body = message.body.decode()
            data = json.loads(body)
            user_id = int(data["user_id"])

            logger.info(f"Received task stats request for user_id={user_id}")

            async with UnitOfWork() as uow:
                task_repo = TaskRepository(uow.session)


                executor_count = await task_repo.count_by_assignee(user_id)


                watcher_count = await task_repo.count_watcher_tasks(user_id)

            response = {
                "executor_tasks_count": executor_count,
                "watcher_tasks_count": watcher_count,
            }

            logger.info(f"Responding: {response}")

            return aio_pika.Message(
                body=json.dumps(response).encode(),
                correlation_id=message.correlation_id,
                content_type="application/json",
            )
        except Exception as e:
            logger.exception("Error processing RPC request")
            return aio_pika.Message(
                body=json.dumps({"error": str(e)}).encode(),
                correlation_id=message.correlation_id,
            )


async def start_rpc_server():
    channel = await get_rabbitmq_channel()


    queue = await channel.declare_queue(QUEUE_NAME, durable=True)


    await queue.consume(_handle_user_stats_request, no_ack=False)

    logger.info(f"RPC Server started: listening on queue '{QUEUE_NAME}'")
    return queue
