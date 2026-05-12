import pytest
from pydantic import ValidationError

from app.core.settings import Settings


def test_settings_rejects_overlap_greater_than_chunk_size() -> None:
    with pytest.raises(ValidationError, match="CHUNK_OVERLAP must be smaller than CHUNK_SIZE"):
        Settings(chunk_size=200, chunk_overlap=200)
