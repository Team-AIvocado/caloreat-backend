from PIL import Image
import io

# use TM's boilerplate


def resize_image(
    image_bytes: bytes, size: tuple = (640, 640), format: str = "JPEG"
) -> bytes:
    """
    AI 모델 입력을 위해 이미지를 리사이징합니다.
    지정된 포맷의 바이트를 반환합니다.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))

        # RGB로 변환 (채널 표준화 - AI 모델 입력용)
        if image.mode != "RGB":
            image = image.convert("RGB")

        # 고품질 리샘플링을 사용하여 리사이즈
        image = image.resize(size, Image.Resampling.LANCZOS)

        # 버퍼에 저장
        buffer = io.BytesIO()
        image.save(buffer, format=format, quality=85)  # TODO
        buffer.seek(0)

        return buffer.getvalue()
    except Exception as e:
        # 리사이징 실패 시 로그를 남기거나 다시 발생시킵니다. 현재는 다시 발생시킵니다.
        raise ValueError(f"이미지 처리 실패: {str(e)}")
