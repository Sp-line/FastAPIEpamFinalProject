from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_mail import FastMail
from fastapi_mail import MessageSchema
from fastapi_mail import MessageType
from pydantic import NameEmail

from app.constants.messages.mail import MailErrorMessage
from app.exceptions.mail import MissingEmailContentError
from app.mail.base import EmailService

if TYPE_CHECKING:
    from app.schemas.mail import EmailMessage


class FastAPIMailService(EmailService):
    def __init__(self, fast_mail: FastMail) -> None:
        self._fast_mail = fast_mail

    async def send_email(self, message: EmailMessage) -> None:
        if not message.body and not message.template_name:
            raise MissingEmailContentError(MailErrorMessage.MISSING_CONTENT)

        valid_recipients = [
            NameEmail(name=email.split("@")[0], email=email)
            for email in message.recipients
        ]

        fastapi_message = MessageSchema(
            subject=message.subject,
            recipients=valid_recipients,
            body=message.body,
            template_body=message.context,
            subtype=MessageType.html if message.is_html else MessageType.plain,
        )

        if message.template_name:
            await self._fast_mail.send_message(
                fastapi_message, template_name=message.template_name
            )
        else:
            await self._fast_mail.send_message(fastapi_message)
