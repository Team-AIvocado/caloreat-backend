import os
import uuid
import shutil
from fastapi import UploadFile
from typing import Optional

# FileManager tmp lifecycle CRUD


class FileManager:
    """
    임시 파일의 저장 및 정리를 관리
    """

    @staticmethod
    # 임시파일저장
    async def save_tmp_image(file: UploadFile) -> str:
        """
        업로드된 파일을 UUID 파일명을 사용하여 임시 경로에 저장

        Returns:
            str: 저장된 임시 파일의 절대 경로
        """
        # 임시 디렉토리 설정 (없으면 생성)
        tmp_dir = "/tmp/caloreat_images"
        os.makedirs(tmp_dir, exist_ok=True)

        # 원본 파일명에서 확장자 추출
        file_ext = file.filename.split(".")[-1] if file.filename else "jpg"

        # 상태유지 이미지 식별자 (UUID)
        image_id = str(uuid.uuid4())

        # 저장될 파일명 (unique)
        filename = f"{image_id}.{file_ext}"
        file_path = os.path.join(tmp_dir, filename)

        # 파일 저장
        try:
            with open(file_path, "wb") as buffer:
                # shutil 로직: 대용량 파일도 버퍼링을 통해 복사
                shutil.copyfileobj(file.file, buffer)
                # TODO: ★★★★★★★ 반드시 기록저장 클릭시 1.s3로직+ 2.tmp cleanup 로직 추가 필요 ★★★
        except Exception as e:
            # 파일 저장 실패 시 에러 처리 (로그 등)
            raise e
        finally:
            await file.seek(0)  # 파일 포인터 초기화 (필요 시)

        return file_path

    @staticmethod
    async def delete_tmp_image(file_path: str) -> None:
        """
        로컬 파일 시스템에서 파일을 삭제

        Args:
            file_path (str): 삭제할 파일의 절대 경로
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError as e:
            # 삭제 실패 시 로그 남기기 (여기서는 print로 대체하거나 logging 모듈 사용)
            print(f"Error deleting file {file_path}: {e}")
            # 필요에 따라 예외를 다시 발생시키지 않고 넘어갈 수 있음
            pass

    @staticmethod
    async def save_by_bytes(image_data: bytes, filename: str) -> str:
        """
        바이트 데이터를 임시 경로에 저장
        """
        tmp_dir = "/tmp/caloreat_images"
        os.makedirs(tmp_dir, exist_ok=True)

        file_path = os.path.join(tmp_dir, filename)

        try:
            with open(file_path, "wb") as f:
                f.write(image_data)
        except Exception as e:
            raise e

        return file_path

    # 식단 저장, S3 업로드 flow
    @staticmethod
    def get_tmp_file_path(image_id: str) -> str:
        """
        이미지 ID로부터 임시 파일 경로를 반환

        Args:
            image_id (str): 업로드된 이미지의 UUID

        Returns:
            str: 임시 파일의 절대 경로
        """
        tmp_dir = "/tmp/caloreat_images"

        # 저장 시 원본 확장자를 유지하므로 (예: {uuid}.png),
        # UUID만으로는 확장자를 알 수 없어 디렉토리 검색이 필요함.

        # 해당 ID로 시작하는 파일 찾기 스캔
        try:
            for filename in os.listdir(tmp_dir):
                # UUID가 정확히 매칭되는지 확인 (파일명: {uuid}.{ext})
                if filename.startswith(image_id) and filename[len(image_id)] == ".":
                    return os.path.join(tmp_dir, filename)
        except FileNotFoundError:
            # tmp 디렉토리가 없는 경우 등
            raise FileNotFoundError(f"Image directory not found: {tmp_dir}")

        # 파일을 찾지 못한 경우 명시적 에러 발생
        raise FileNotFoundError(f"Image file not found for ID: {image_id}")
