from fastapi import Depends
from fastapi.security import APIKeyHeader

API_KEY: APIKeyHeader = APIKeyHeader(name="X-key")
FAKE_KEYS: set[str] = {"security", "secret"}


def get_api_key(key: str = Depends(API_KEY)) -> str:
    if key not in FAKE_KEYS:
