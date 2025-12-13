import aio_pika
import json
import asyncio
from auth_service.src.core.config import settings


async def get_user_task_stats(user_id: int) -> dict:
    """Делает request-reply в task_service и возвращает статистику задач"""
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()

        callback_queue = await channel.declare_queue(exclusive=True)

        response = None
        correlation_id = str(id(asyncio.get_event_loop()))

        async def on_response(message: aio_pika.IncomingMessage):
            nonlocal response
            if message.correlation_id == correlation_id:
                response = json.loads(message.body)

        await callback_queue.consume(on_response, no_ack=True)

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps({"user_id": user_id}).encode(),
                content_type="application/json",
                correlation_id=correlation_id,
                reply_to=callback_queue.name,
            ),
            routing_key="task_service.rpc.stats",
        )


        for _ in range(100):
            if response is not None:
                return response
            await asyncio.sleep(0.1)

        raise TimeoutError("task-service не ответил за 10 сек")