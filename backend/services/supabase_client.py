"""Supabase client singleton."""

from supabase import create_client, Client  # type: ignore
from config import SUPABASE_URL, SUPABASE_KEY  # type: ignore

_client: Client | None = None


def get_supabase() -> Client:
    """Return a cached Supabase client instance."""
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_KEY must be set in the .env file."
            )
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client
