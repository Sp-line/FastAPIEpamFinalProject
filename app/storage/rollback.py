from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from botocore.exceptions import BotoCoreError
from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from types import TracebackType
    from typing import Self

    from app.storage.s3 import S3Storage

logger = logging.getLogger(__name__)


class S3Rollback:
    def __init__(
        self,
        storage: S3Storage,
        *keys: str,
    ) -> None:
        self._storage = storage
        self._keys = keys

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            try:
                await self._storage.delete_files(*self._keys)
            except ClientError, BotoCoreError:
                logger.exception(
                    "Failed to rollback S3 files after error. Keys: %s", self._keys
                )
