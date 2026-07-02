from __future__ import annotations

from typing import TYPE_CHECKING

from types_aiobotocore_ses.type_defs import BodyTypeDef

from app.constants.messages.mail import MailErrorMessage
from app.exceptions.mail import MissingEmailContentError
from app.mail.base import EmailService

if TYPE_CHECKING:
    from jinja2 import Environment
    from types_aiobotocore_ses import SESClient

    from app.schemas.mail import EmailMessage


class SESMailService(EmailService):
    def __init__(
        self, ses_client: SESClient, sender: str, jinja_env: Environment
    ) -> None:
        self._client = ses_client
        self._sender = sender
        self._jinja_env = jinja_env

    async def send_email(self, message: EmailMessage) -> None:
        if not message.body and not message.template_name:
            raise MissingEmailContentError(MailErrorMessage.MISSING_CONTENT)

        content_data = message.body or ""

        if message.template_name:
            template = self._jinja_env.get_template(message.template_name)
            content_data = template.render(**(message.context or {}))

        if message.is_html:
            message_body = BodyTypeDef(Html={"Data": content_data, "Charset": "UTF-8"})
        else:
            message_body = BodyTypeDef(Text={"Data": content_data, "Charset": "UTF-8"})

        await self._client.send_email(
            Source=self._sender,
            Destination={"ToAddresses": list(message.recipients)},
            Message={
                "Subject": {
                    "Data": message.subject,
                    "Charset": "UTF-8",
                },
                "Body": message_body,
            },
        )
