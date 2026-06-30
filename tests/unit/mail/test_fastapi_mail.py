from typing import cast
from unittest.mock import AsyncMock

import pytest
from fastapi_mail import FastMail
from fastapi_mail import MessageSchema
from fastapi_mail import MessageType
from pydantic import NameEmail

from app.constants.messages.mail import MailErrorMessage
from app.exceptions.mail import MissingEmailContentError
from app.mail.fastapi_mail import FastAPIMailService
from tests.factories.mail import EmailMessageFactory


@pytest.fixture
def mock_fast_mail() -> AsyncMock:
    return AsyncMock(spec=FastMail)


@pytest.fixture
def fastapi_mail_service(mock_fast_mail: AsyncMock) -> FastAPIMailService:
    return FastAPIMailService(fast_mail=mock_fast_mail)


class TestFastAPIMailService:
    async def test_send_email_raises_error_when_no_body_and_no_template(
        self,
        fastapi_mail_service: FastAPIMailService,
        mock_fast_mail: AsyncMock,
    ) -> None:
        message = EmailMessageFactory.build(body=None, template_name=None)

        with pytest.raises(
            MissingEmailContentError, match=MailErrorMessage.MISSING_CONTENT
        ):
            await fastapi_mail_service.send_email(message)

        mock_fast_mail.send_message.assert_not_called()

    async def test_send_email_parses_recipients_correctly(
        self,
        fastapi_mail_service: FastAPIMailService,
        mock_fast_mail: AsyncMock,
    ) -> None:
        message = EmailMessageFactory.build(
            recipients=["john.doe@example.com", "admin@test.com"],
            body="Some body",
            template_name=None,
        )

        await fastapi_mail_service.send_email(message)

        mock_fast_mail.send_message.assert_awaited_once()
        sent_message = cast(
            "MessageSchema", mock_fast_mail.send_message.call_args.args[0]
        )

        assert len(sent_message.recipients) == 2  # noqa: PLR2004

        recipient_1 = sent_message.recipients[0]
        assert isinstance(recipient_1, NameEmail)
        assert recipient_1.name == "john.doe"
        assert recipient_1.email == "john.doe@example.com"

        recipient_2 = sent_message.recipients[1]
        assert isinstance(recipient_2, NameEmail)
        assert recipient_2.name == "admin"
        assert recipient_2.email == "admin@test.com"

    async def test_send_email_sends_plain_text_message(
        self,
        fastapi_mail_service: FastAPIMailService,
        mock_fast_mail: AsyncMock,
    ) -> None:
        message = EmailMessageFactory.build(
            body="Plain text content",
            is_html=False,
            template_name=None,
        )

        await fastapi_mail_service.send_email(message)

        mock_fast_mail.send_message.assert_awaited_once()
        sent_message = cast(
            "MessageSchema", mock_fast_mail.send_message.call_args.args[0]
        )

        assert sent_message.body == message.body
        assert sent_message.subtype == MessageType.plain
        assert "template_name" not in mock_fast_mail.send_message.call_args.kwargs

    async def test_send_email_sends_html_message(
        self,
        fastapi_mail_service: FastAPIMailService,
        mock_fast_mail: AsyncMock,
    ) -> None:
        message = EmailMessageFactory.build(
            body="<h1>HTML content</h1>",
            is_html=True,
            template_name=None,
        )

        await fastapi_mail_service.send_email(message)

        mock_fast_mail.send_message.assert_awaited_once()
        sent_message = cast(
            "MessageSchema", mock_fast_mail.send_message.call_args.args[0]
        )

        assert sent_message.body == message.body
        assert sent_message.subtype == MessageType.html

    async def test_send_email_sends_message_with_template(
        self,
        fastapi_mail_service: FastAPIMailService,
        mock_fast_mail: AsyncMock,
    ) -> None:
        context_data = {"user_name": "Test User"}
        message = EmailMessageFactory.build(
            body=None,
            template_name="welcome.html",
            context=context_data,
        )

        await fastapi_mail_service.send_email(message)

        mock_fast_mail.send_message.assert_awaited_once()

        sent_message = cast(
            "MessageSchema", mock_fast_mail.send_message.call_args.args[0]
        )
        kwargs = mock_fast_mail.send_message.call_args.kwargs

        assert sent_message.template_body == context_data
        assert kwargs.get("template_name") == "welcome.html"
