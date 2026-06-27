from typing import TYPE_CHECKING

from types_aiobotocore_s3 import S3Client  # noqa: TC002

if TYPE_CHECKING:
    from typing import BinaryIO

    from aiobotocore.response import StreamingBody


class S3Storage:
    def __init__(self, s3_client: S3Client, bucket_name: str) -> None:
        self._client = s3_client
        self._bucket = bucket_name

    async def upload_file(self, key: str, file_obj: BinaryIO, content_type: str) -> None:
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
