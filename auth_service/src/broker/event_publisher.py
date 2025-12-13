import json
import aio_pika
from auth_service.src.core.config import settings


async def publish_user_registered(user_id: int, email: str):
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps({
                    "type": "user_registered",
                    "data": {
                        "user_id": user_id,
                        "email": email
                    }
                }).encode(),
                content_type="application/json"
            ),
            routing_key="email.notifications"
        )
