import aio_pika
from task_service.src.core.config import settings
import logging

logger = logging.getLogger(__name__)

_connection = None
_channel = None


async def get_rabbitmq_channel():
    global _connection, _channel
    if _channel is None or _channel.is_closed:
        logger.info("Connecting to RabbitMQ...")
        _connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        _channel = await _connection.channel()
        await _channel.set_qos(prefetch_count=10)
        logger.info("Connected to RabbitMQ")
    return _channel
