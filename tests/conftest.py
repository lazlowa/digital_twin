from collections.abc import Iterator

import pytest

from app.ratelimit import limiter


@pytest.fixture(autouse=True)
def reset_rate_limit() -> Iterator[None]:
    limiter.hits.clear()
    yield
    limiter.hits.clear()
