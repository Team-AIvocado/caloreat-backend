import os
import shutil
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
from typing import Optional

# FileManager tmp lifecycle CRUD


class FileManager:
    """
    임시 파일의 저장 및 정리를 관리
    """

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
            pass

        # def _delete():
        #     try:
        #         if os.path.exists(file_path):
        #             os.remove(file_path)
        #     except OSError as e:
        #         # 삭제 실패 시 로그 남기기 (여기서는 print로 대체하거나 logging 모듈 사용)
        #         print(f"Error deleting file {file_path}: {e}")
        #         pass

        # await run_in_threadpool(_delete)

    @staticmethod
    async def save_tmp_image(image_data: bytes, filename: str) -> str:
        """
        바이트 데이터를 임시 경로에 저장 (Non-blocking)
        """
        tmp_dir = "/tmp/caloreat_images"
        os.makedirs(tmp_dir, exist_ok=True)

        file_path = os.path.join(tmp_dir, filename)

        # TODO:
        # def _write():
        #     with open(file_path, "wb") as f:
        #         f.write(image_data)
        #     return file_path

        # return await run_in_threadpool(_write)

        with open(file_path, "wb") as f:
            f.write(image_data)
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
