import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError
from app.clients.s3_client import S3Client


@pytest.fixture
def mock_boto_client():
    with patch("app.clients.s3_client.boto3.client") as mock:
        yield mock


def test_upload_file_success(mock_boto_client):
    # Given
    file_path = "/tmp/test.jpg"
    object_name = "test_image.jpg"

    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    # We need to simulate the class-level client being our mock
    # Since _client is initialized at import time, we might need to patch it directly on the class
    with patch.object(S3Client, "_client", mock_s3):
        # When
        url = S3Client.upload_file(file_path, object_name)

        # Then
        # Verify that loaded settings (from .env.example) are used
        expected_bucket = "test-bucket"
        expected_region = "ap-northeast-2"

        assert (
            url
            == f"https://{expected_bucket}.s3.{expected_region}.amazonaws.com/{object_name}"
        )
        mock_s3.upload_file.assert_called_once()
        call_args = mock_s3.upload_file.call_args
        assert call_args.kwargs["Filename"] == file_path
        assert call_args.kwargs["Key"] == object_name
        assert call_args.kwargs["Bucket"] == expected_bucket
        assert call_args.kwargs["ExtraArgs"]["ContentType"] == "image/jpeg"


def test_upload_file_failure(mock_boto_client):
    # Given
    file_path = "/tmp/test.jpg"
    object_name = "test_image.jpg"

    mock_s3 = MagicMock()
    error_response = {"Error": {"Code": "500", "Message": "Error Uploading"}}
    mock_s3.upload_file.side_effect = ClientError(error_response, "UploadFile")

    with patch.object(S3Client, "_client", mock_s3):
        # Then
        with pytest.raises(Exception) as excinfo:
            S3Client.upload_file(file_path, object_name)

        assert "S3 Upload Error" in str(excinfo.value)


def test_delete_file_success(mock_boto_client):
    # Given
    object_name = "test_image.jpg"
    mock_s3 = MagicMock()

    with patch.object(S3Client, "_client", mock_s3):
        # When
        S3Client.delete_file(object_name)

        # Then
        mock_s3.delete_object.assert_called_once_with(
            Bucket=S3Client._bucket, Key=object_name
        )


def test_delete_file_failure_logs_error(mock_boto_client):
    # Given
    object_name = "test_image.jpg"
    mock_s3 = MagicMock()
    error_response = {"Error": {"Code": "404", "Message": "Not Found"}}
    mock_s3.delete_object.side_effect = ClientError(error_response, "DeleteObject")

    with (
        patch.object(S3Client, "_client", mock_s3),
        patch("app.clients.s3_client.logger") as mock_logger,
    ):
        # When
        S3Client.delete_file(object_name)

        # Then
        mock_s3.delete_object.assert_called_once()
        # Should not raise exception, but log error
        mock_logger.error.assert_called_once()


def test_convert_to_presigned_url_success(mock_boto_client):
    # Given
    original_url = (
        "https://test-bucket.s3.ap-northeast-2.amazonaws.com/meals/abcd-1234.jpg"
    )
    expected_key = "meals/abcd-1234.jpg"
    presigned_url = "https://s3.params..."

    mock_s3 = MagicMock()
    mock_s3.generate_presigned_url.return_value = presigned_url

    with patch.object(S3Client, "_client", mock_s3):
        # When
        result = S3Client.convert_to_presigned_url(original_url)

        # Then
        assert result == presigned_url
        mock_s3.generate_presigned_url.assert_called_once_with(
            "get_object",
            Params={"Bucket": S3Client._bucket, "Key": expected_key},
            ExpiresIn=3600,
        )


def test_convert_to_presigned_url_failure(mock_boto_client):
    # Given
    original_url = "https://invalid-url.com"

    mock_s3 = MagicMock()
    # Mocking failure inside generate_presigned_url
    error_response = {"Error": {"Code": "500", "Message": "Error Generating"}}
    mock_s3.generate_presigned_url.side_effect = ClientError(
        error_response, "GeneratePresignedUrl"
    )

    with (
        patch.object(S3Client, "_client", mock_s3),
        patch("app.clients.s3_client.logger") as mock_logger,
    ):
        # When
        # Should return original url on failure
        result = S3Client.convert_to_presigned_url(original_url)

        # Then
        assert result == original_url
        mock_logger.error.assert_called_once()


def test_convert_to_presigned_url_empty_input():
    # Given
    original_url = ""

    # When
    result = S3Client.convert_to_presigned_url(original_url)

    # Then
    assert result == ""
