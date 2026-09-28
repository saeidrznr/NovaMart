from supabase import create_client

from core.config import settings
from .storage.base import Storage
from .storage.local import LocalStorage
from .storage.cloud import CloudStorage


def _get_supabase():
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_storage() -> Storage:
    if settings.ENVIRONMENT == "development":
        return LocalStorage("uploads","http://127.0.0.1:8000/uploads")

    supabase = _get_supabase()
    return CloudStorage(supabase, "product-images")
