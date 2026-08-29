from fastapi import UploadFile
from storage3.types import FileOptions

from .base import Storage
from supabase import Client


class CloudStorage(Storage):
    def __init__(self, client: Client, bucket: str):
        self.client = client
        self.bucket = bucket

    async def upload(self, file: UploadFile, path: str):
        content = await file.read()
        self.client.storage.from_(self.bucket).upload(path, content, FileOptions(
            **{"content-type": file.content_type, "upsert": False}))
        return self.client.storage.from_(self.bucket).get_public_url(path)

    async def delete(self, path: str):
        self.client.storage.from_(self.bucket).remove(path)
