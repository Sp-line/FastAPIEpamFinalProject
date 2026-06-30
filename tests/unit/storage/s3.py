import io
from typing import TYPE_CHECKING
from typing import BinaryIO
from typing import cast
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import call

import pytest

if TYPE_CHECKING:
    from app.storage.s3 import S3Storage


class TestS3Storage:
    async def test_upload_file_calls_put_object_with_correct_args(
        self,
        s3_storage: S3Storage,
        mock_s3_client: AsyncMock,
        s3_bucket_name: str,
    ) -> None:
        key = "documents/test.pdf"
        file_obj = MagicMock()
        content_type = "application/pdf"

        await s3_storage.upload_file(key, file_obj, content_type)

        mock_s3_client.put_object.assert_awaited_once_with(
            Bucket=s3_bucket_name,
            Key=key,
            Body=file_obj,
            ContentType=content_type,
        )

    async def test_delete_file_calls_delete_object_with_correct_args(
        self,
        s3_storage: S3Storage,
        mock_s3_client: AsyncMock,
        s3_bucket_name: str,
    ) -> None:
        key = "documents/old_test.pdf"

        await s3_storage.delete_file(key)

        mock_s3_client.delete_object.assert_awaited_once_with(
            Bucket=s3_bucket_name,
            Key=key,
        )

    async def test_get_presigned_url_returns_correct_string(
        self,
        s3_storage: S3Storage,
        mock_s3_client: AsyncMock,
        s3_bucket_name: str,
    ) -> None:
        key = "documents/report.docx"
        original_name = "My Report.docx"
        expires_in = 3600
        expected_url = "https://s3.amazonaws.com/test-url"

        mock_s3_client.generate_presigned_url.return_value = expected_url

        result = await s3_storage.get_presigned_url(key, original_name, expires_in)

        assert result == expected_url
        mock_s3_client.generate_presigned_url.assert_awaited_once_with(
            "get_object",
            Params={
                "Bucket": s3_bucket_name,
                "Key": key,
                "ResponseContentDisposition": f'attachment; filename="{original_name}"',
            },
            ExpiresIn=expires_in,
        )

    async def test_get_file_stream_returns_body_and_content_type(
        self,
        s3_storage: S3Storage,
        mock_s3_client: AsyncMock,
        s3_bucket_name: str,
    ) -> None:
        key = "media/image.png"
        mock_body = MagicMock()
        mock_content_type = "image/png"

        mock_s3_client.get_object.return_value = {
            "Body": mock_body,
            "ContentType": mock_content_type,
        }

        body, content_type = await s3_storage.get_file_stream(key)

        assert body == mock_body
        assert content_type == mock_content_type
        mock_s3_client.get_object.assert_awaited_once_with(
            Bucket=s3_bucket_name, Key=key
        )

    async def test_delete_files_returns_early_if_no_keys_provided(
        self,
        s3_storage: S3Storage,
        mock_s3_client: AsyncMock,
    ) -> None:
        await s3_storage.delete_files()

        mock_s3_client.delete_objects.assert_not_called()

    @pytest.mark.parametrize(
        ("num_keys", "expected_api_calls"),
        [
            (5, 1),
            (1000, 1),
            (1005, 2),
            (3000, 3),
        ],
        ids=["under_limit", "exact_limit", "over_limit", "multiple_chunks"],
    )
    async def test_delete_files_chunks_keys_correctly(
        self,
        s3_storage: S3Storage,
        mock_s3_client: AsyncMock,
        s3_bucket_name: str,
        num_keys: int,
        expected_api_calls: int,
    ) -> None:
        keys = [f"file_{i}.txt" for i in range(num_keys)]

        await s3_storage.delete_files(*keys)

        assert mock_s3_client.delete_objects.await_count == expected_api_calls

        last_call_args = mock_s3_client.delete_objects.await_args.kwargs
        assert last_call_args["Bucket"] == s3_bucket_name
        assert "Delete" in last_call_args
        assert "Objects" in last_call_args["Delete"]

        expected_objects_in_last_chunk = num_keys % 1000 or 1000
        assert len(last_call_args["Delete"]["Objects"]) == expected_objects_in_last_chunk

    async def test_upload_files_returns_early_if_no_files_provided(
        self,
        s3_storage: S3Storage,
        mock_s3_client: AsyncMock,
    ) -> None:
        await s3_storage.upload_files([])

        mock_s3_client.put_object.assert_not_called()

    async def test_upload_files_uploads_all_files_concurrently(
        self,
        s3_storage: S3Storage,
        mock_s3_client: AsyncMock,
        s3_bucket_name: str,
    ) -> None:
        file1 = io.BytesIO(b"data1")
        file2 = io.BytesIO(b"data2")

        files_data = [
            ("key1.txt", file1, "text/plain"),
            ("key2.png", file2, "image/png"),
        ]

        await s3_storage.upload_files(
            cast("list[tuple[str, BinaryIO, str]]", files_data)
        )

        assert mock_s3_client.put_object.await_count == 2  # noqa: PLR2004

        expected_calls = [
            call(
                Bucket=s3_bucket_name,
                Key="key1.txt",
                Body=file1,
                ContentType="text/plain",
            ),
            call(
                Bucket=s3_bucket_name,
                Key="key2.png",
                Body=file2,
                ContentType="image/png",
            ),
        ]
        mock_s3_client.put_object.assert_has_awaits(expected_calls, any_order=True)
