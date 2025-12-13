import json
import logging
import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from email_service.src.services.email import EmailService

logger = logging.getLogger(__name__)

QUEUE_NAME = "email.notifications"


class EmailConsumer:
    def __init__(self, channel: aio_pika.Channel):
        self.channel = channel
        self.email_service = EmailService()

    async def start(self):
        queue = await self.channel.declare_queue(
            QUEUE_NAME,
            durable=True,
        )

        await queue.consume(self.handle_message)
        logger.info(f"EmailConsumer слушает очередь '{QUEUE_NAME}'")

    async def handle_message(self, message: AbstractIncomingMessage):
        async with message.process():
            try:
                payload = json.loads(message.body)
                event_type = payload.get("type")
                data = payload.get("data", {})

                logger.info(f"Получено событие: {event_type}")

                if event_type == "user_registered":
                    await self.handle_user_registered(data)
                else:
                    logger.warning(f"Неизвестный тип события: {event_type}")

            except Exception:
                logger.exception("Ошибка при обработке сообщения")

    async def handle_user_registered(self, data: dict):
        user_id = data.get("user_id")
        email = data.get("email")

        if not user_id or not email:
            logger.error("Некорректные данные события user_registered")
            return

        await self.email_service.send_welcome_email(
            user_id=user_id,
            email=email,
        )
