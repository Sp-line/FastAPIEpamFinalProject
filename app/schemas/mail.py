from collections.abc import Sequence  # noqa: TC003
from typing import Any

from pydantic import BaseModel


class EmailMessage(BaseModel):
    subject: str
    recipients: Sequence[str]
    is_html: bool
    body: str | None = None
    template_name: str | None = None
    context: dict[str, Any] | None = None
