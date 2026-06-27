from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from types_aiobotocore_s3 import S3Client  # noqa: TC002

if TYPE_CHECKING:
    from typing import BinaryIO

    from aiobotocore.response import StreamingBody
    from types_aiobotocore_s3.type_defs import ObjectIdentifierTypeDef

type S3Key = str
type FileContentType = str


class S3Storage:
    def __init__(self, s3_client: S3Client, bucket_name: str) -> None:
        self._client = s3_client
        self._bucket = bucket_name

    async def upload_file(
        self, key: S3Key, file_obj: BinaryIO, content_type: FileContentType
    ) -> None:
        await self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=file_obj,
            ContentType=content_type,
        )

    async def delete_file(self, key: str) -> None:
        await self._client.delete_object(Bucket=self._bucket, Key=key)

    async def get_presigned_url(
        self, key: str, original_name: str, expires_in: int
    ) -> str:
        url = await self._client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self._bucket,
                "Key": key,
                "ResponseContentDisposition": f'attachment; filename="{original_name}"',
            },
            ExpiresIn=expires_in,
        )
        return str(url)

    async def get_file_stream(self, key: str) -> tuple[StreamingBody, str]:
        response = await self._client.get_object(Bucket=self._bucket, Key=key)
        return response["Body"], response["ContentType"]

    async def delete_files(self, *keys: str) -> None:
        if not keys:
            return

        for i in range(0, len(keys), 1000):
            chunk = keys[i : i + 1000]
            objects_to_delete: list[ObjectIdentifierTypeDef] = [
                {"Key": key} for key in chunk
            ]

            await self._client.delete_objects(
                Bucket=self._bucket,
                Delete={"Objects": objects_to_delete},
            )

    async def upload_files(
        self,
        files_data: list[tuple[S3Key, BinaryIO, FileContentType]],
    ) -> None:
        if not files_data:
            return

        async with asyncio.TaskGroup() as tg:
            for key, file_obj, content_type in files_data:
                tg.create_task(
                    self.upload_file(
                        key=key, file_obj=file_obj, content_type=content_type
                    )
                )
