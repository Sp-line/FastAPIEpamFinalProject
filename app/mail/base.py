from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.mail import EmailMessage


class EmailService(ABC):
    @abstractmethod
    async def send_email(self, message: EmailMessage) -> None: ...
