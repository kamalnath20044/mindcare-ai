"""Lightweight Supabase REST client — no heavy dependencies.

Drop-in replacement for the official `supabase` Python package.
Uses httpx (already a FastAPI dependency) to call Supabase REST API directly.
Implements the same .table().select().eq().insert() ... .execute() chaining API.
"""

from __future__ import annotations
import httpx
from config import SUPABASE_URL, SUPABASE_KEY  # type: ignore


class _QueryResult:
    """Mimics the Supabase execute() result."""
    def __init__(self, data: list, count: int | None = None):
        self.data = data
        self.count = count


class _QueryBuilder:
    """Chainable query builder that mirrors the supabase-py API."""

    def __init__(self, url: str, headers: dict, table: str):
        self._base = f"{url}/rest/v1/{table}"
        self._headers = headers
        self._params: dict = {}
        self._method = "GET"
        self._body: dict | list | None = None
        self._count_mode: str | None = None

    # --- Chainable methods ---

    def select(self, columns: str = "*", *, count: str | None = None) -> _QueryBuilder:
        self._method = "GET"
        self._params["select"] = columns
        if count:
            self._count_mode = count
            self._headers["Prefer"] = f"count={count}"
        return self

    def insert(self, data: dict | list) -> _QueryBuilder:
        self._method = "POST"
        self._body = data
        self._headers["Prefer"] = "return=representation"
        return self

    def update(self, data: dict) -> _QueryBuilder:
        self._method = "PATCH"
        self._body = data
        self._headers["Prefer"] = "return=representation"
        return self

    def upsert(self, data: dict | list, *, on_conflict: str = "") -> _QueryBuilder:
        self._method = "POST"
        self._body = data
        prefer = "return=representation,resolution=merge-duplicates"
        self._headers["Prefer"] = prefer
        if on_conflict:
            self._params["on_conflict"] = on_conflict
        return self

    def delete(self) -> _QueryBuilder:
        self._method = "DELETE"
        return self

    def eq(self, column: str, value) -> _QueryBuilder:
        self._params[column] = f"eq.{value}"
        return self

    def neq(self, column: str, value) -> _QueryBuilder:
        self._params[column] = f"neq.{value}"
        return self

    def gt(self, column: str, value) -> _QueryBuilder:
        self._params[column] = f"gt.{value}"
        return self

    def gte(self, column: str, value) -> _QueryBuilder:
        self._params[column] = f"gte.{value}"
        return self

    def lt(self, column: str, value) -> _QueryBuilder:
        self._params[column] = f"lt.{value}"
        return self

    def lte(self, column: str, value) -> _QueryBuilder:
        self._params[column] = f"lte.{value}"
        return self

    def order(self, column: str, *, desc: bool = False) -> _QueryBuilder:
        direction = "desc" if desc else "asc"
        self._params["order"] = f"{column}.{direction}"
        return self

    def limit(self, n: int) -> _QueryBuilder:
        self._headers["Range"] = f"0-{n - 1}"
        return self

    def execute(self) -> _QueryResult:
        """Execute the query and return the result."""
        with httpx.Client(timeout=15.0) as client:
            if self._method == "GET":
                resp = client.get(self._base, headers=self._headers, params=self._params)
            elif self._method == "POST":
                resp = client.post(self._base, headers=self._headers, params=self._params, json=self._body)
            elif self._method == "PATCH":
                resp = client.patch(self._base, headers=self._headers, params=self._params, json=self._body)
            elif self._method == "DELETE":
                resp = client.delete(self._base, headers=self._headers, params=self._params)
            else:
                raise ValueError(f"Unknown method: {self._method}")

        resp.raise_for_status()

        data = resp.json() if resp.text else []
        count = None
        if self._count_mode:
            content_range = resp.headers.get("content-range", "")
            if "/" in content_range:
                try:
                    count = int(content_range.split("/")[1])
                except (ValueError, IndexError):
                    count = len(data) if isinstance(data, list) else 0

        return _QueryResult(data=data, count=count)


class SupabaseClient:
    """Lightweight Supabase client using REST API."""

    def __init__(self, url: str, key: str):
        self.url = url.rstrip("/")
        self.key = key

    def table(self, name: str) -> _QueryBuilder:
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }
        return _QueryBuilder(self.url, headers, name)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
_client: SupabaseClient | None = None


def get_supabase() -> SupabaseClient:
    """Return a cached lightweight Supabase client."""
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        _client = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)
    return _client
