from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

if TYPE_CHECKING:
    from types_aiobotocore_ses.type_defs import BodyTypeDef

from app.constants.messages.mail import MailErrorMessage
from app.exceptions.mail import MissingEmailContentError
from app.mail.ses import SESMailService
from tests.factories.mail import EmailMessageFactory


@pytest.fixture
def mock_ses_client() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_jinja_env() -> MagicMock:
    env = MagicMock()
    mock_template = MagicMock()
    env.get_template.return_value = mock_template
    return env


@pytest.fixture
def sender_email() -> str:
    return "noreply@mycompany.com"


@pytest.fixture
def ses_mail_service(
    mock_ses_client: AsyncMock,
    sender_email: str,
    mock_jinja_env: MagicMock,
) -> SESMailService:
    return SESMailService(
        ses_client=mock_ses_client,
        sender=sender_email,
        jinja_env=mock_jinja_env,
    )


class TestSESMailService:
    async def test_send_email_raises_error_when_no_body_and_no_template(
        self,
        ses_mail_service: SESMailService,
        mock_ses_client: AsyncMock,
    ) -> None:
        message = EmailMessageFactory.build(body=None, template_name=None)

        with pytest.raises(
            MissingEmailContentError, match=MailErrorMessage.MISSING_CONTENT
        ):
            await ses_mail_service.send_email(message)

        mock_ses_client.send_email.assert_not_called()

    async def test_send_email_sends_plain_text_correctly(
        self,
        ses_mail_service: SESMailService,
        mock_ses_client: AsyncMock,
        sender_email: str,
    ) -> None:
        body_text = "This is a plain text email."
        message = EmailMessageFactory.build(
            body=body_text,
            is_html=False,
            template_name=None,
            recipients=["test1@example.com", "test2@example.com"],
        )

        expected_body: BodyTypeDef = {"Text": {"Data": body_text, "Charset": "UTF-8"}}

        await ses_mail_service.send_email(message)

        mock_ses_client.send_email.assert_awaited_once_with(
            Source=sender_email,
            Destination={"ToAddresses": list(message.recipients)},
            Message={
                "Subject": {
                    "Data": message.subject,
                    "Charset": "UTF-8",
                },
                "Body": expected_body,
            },
        )

    async def test_send_email_sends_html_correctly(
        self,
        ses_mail_service: SESMailService,
        mock_ses_client: AsyncMock,
        sender_email: str,
    ) -> None:
        html_content = "<h1>Welcome!</h1>"
        message = EmailMessageFactory.build(
            body=html_content,
            is_html=True,
            template_name=None,
        )

        expected_body: BodyTypeDef = {"Html": {"Data": html_content, "Charset": "UTF-8"}}

        await ses_mail_service.send_email(message)

        mock_ses_client.send_email.assert_awaited_once_with(
            Source=sender_email,
            Destination={"ToAddresses": list(message.recipients)},
            Message={
                "Subject": {
                    "Data": message.subject,
                    "Charset": "UTF-8",
                },
                "Body": expected_body,
            },
        )

    async def test_send_email_uses_jinja_template_when_provided(
        self,
        ses_mail_service: SESMailService,
        mock_ses_client: AsyncMock,
        mock_jinja_env: MagicMock,
        sender_email: str,
    ) -> None:
        template_name = "welcome.html"
        context_data = {"username": "JohnDoe"}
        rendered_html = "<h1>Welcome, JohnDoe!</h1>"

        mock_template = mock_jinja_env.get_template.return_value
        mock_template.render.return_value = rendered_html

        message = EmailMessageFactory.build(
            body=None,
            is_html=True,
            template_name=template_name,
            context=context_data,
        )

        expected_body: BodyTypeDef = {
            "Html": {"Data": rendered_html, "Charset": "UTF-8"}
        }

        await ses_mail_service.send_email(message)

        mock_jinja_env.get_template.assert_called_once_with(template_name)
        mock_template.render.assert_called_once_with(**context_data)

        mock_ses_client.send_email.assert_awaited_once_with(
            Source=sender_email,
            Destination={"ToAddresses": list(message.recipients)},
            Message={
                "Subject": {
                    "Data": message.subject,
                    "Charset": "UTF-8",
                },
                "Body": expected_body,
            },
        )

    async def test_send_email_uses_empty_dict_for_context_if_none_provided(
        self,
        ses_mail_service: SESMailService,
        mock_jinja_env: MagicMock,
    ) -> None:
        mock_template = mock_jinja_env.get_template.return_value
        mock_template.render.return_value = "Output"

        message = EmailMessageFactory.build(
            body=None,
            template_name="test.txt",
            context=None,
        )

        await ses_mail_service.send_email(message)

        mock_template.render.assert_called_once_with()
