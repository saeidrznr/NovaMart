from pathlib import Path

from fastapi import UploadFile

from .base import Storage


class LocalStorage(Storage):
    def __init__(self, base_path: str = "uploads", base_url: str = "/uploads"):
        self.base_path = Path(base_path)
        self.base_url = base_url

    async def upload(self, file: UploadFile, path: str):
        file_path = self.base_path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)

        await file.seek(0)

        return f"{self.base_url}/{path}"

    async def delete(self, path: str):
        file_path = self.base_path / path
        if file_path.exists():
            file_path.unlink()
