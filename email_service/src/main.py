import asyncio
import logging
import aio_pika

from email_service.src.broker.consumer import EmailConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672/"


async def main():
    logger.info("Запуск email-service...")

    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)

        consumer = EmailConsumer(channel)
        await consumer.start()

        logger.info("email-service успешно запущен и ожидает события")
        await asyncio.Future()  # держим сервис живым


if __name__ == "__main__":
    asyncio.run(main())
