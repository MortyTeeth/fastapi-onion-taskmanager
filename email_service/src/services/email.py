import logging

logger = logging.getLogger(__name__)


class EmailService:
    async def send_welcome_email(self, user_id: int, email: str):
        """
        Мок отправки email.
        Здесь в будущем можно подключить:
        - SMTP
        - SendGrid
        - Amazon SES
        """

        logger.info("==== Отправка письма ====")
        logger.info(f"Кому: {email}")
        logger.info(f"User ID: {user_id}")
        logger.info("Тема: Добро пожаловать!")
        logger.info("Тело: Спасибо за регистрацию 🚀")
        logger.info("==== Письмо отправлено (мок) ====")
