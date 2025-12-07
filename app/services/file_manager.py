import os
from fastapi import UploadFile
from typing import Optional


class FileManager:
    """
    임시 파일의 저장 및 정리를 관리
    """

    @staticmethod
    async def save_tmp_image(file: UploadFile) -> str:
        """
        업로드된 파일을 UUID 파일명을 사용하여 임시 경로에 저장

        Returns:
            str: 저장된 임시 파일의 절대 경로
        """
        pass

    @staticmethod
    async def delete_tmp_image(file_path: str) -> None:
        """
        로컬 파일 시스템에서 파일을 삭제

        Args:
            file_path (str): 삭제할 파일의 절대 경로
        """
        pass
