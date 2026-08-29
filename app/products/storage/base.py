from abc import ABC, abstractmethod

from fastapi import UploadFile


class Storage(ABC):
    @abstractmethod
    async def upload(self, file: UploadFile, path: str):
        pass

    @abstractmethod
    async def delete(self, path: str):
        pass
