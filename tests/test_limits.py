import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.ratelimit import RateLimiter
from tests.test_chat import FakeClient, text, use

client = TestClient(app)


def ask(messages: list[dict]) -> int:
    return client.post("/api/chat", json={"messages": messages}).status_code


def user(content: str) -> dict:
    return {"role": "user", "content": content}


@pytest.fixture
def fake() -> FakeClient:
    return use(FakeClient([[text("Hi.")]] * 20))


def test_over_long_message_is_rejected(fake: FakeClient) -> None:
    assert ask([user("x" * settings.max_message_chars)]) == 200
    assert ask([user("x" * (settings.max_message_chars + 1))]) == 422


def test_earlier_twin_reply_may_exceed_visitor_limit(fake: FakeClient) -> None:
    reply = {"role": "assistant", "content": "x" * (settings.max_message_chars + 1)}

    assert ask([user("Hi"), reply, user("More?")]) == 200


def test_over_long_history_is_rejected(fake: FakeClient) -> None:
    history = [user("Hi")] * settings.max_history_messages

    assert ask(history) == 200
    assert ask([*history, user("Hi")]) == 422


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"messages": []},
        {"messages": [{"role": "user"}]},
        {"messages": [{"role": "user", "content": ""}]},
        {"messages": "Hi"},
    ],
)
def test_malformed_body_is_rejected(fake: FakeClient, body: dict) -> None:
    assert client.post("/api/chat", json=body).status_code == 422


def test_invalid_json_is_rejected(fake: FakeClient) -> None:
    response = client.post(
        "/api/chat", content="{not json", headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422


def test_requests_above_rate_limit_get_429(fake: FakeClient) -> None:
    statuses = [ask([user("Hi")]) for _ in range(settings.rate_limit_per_minute)]
    response = client.post("/api/chat", json={"messages": [user("Hi")]})

    assert statuses == [200] * settings.rate_limit_per_minute
    assert response.status_code == 429
    assert 0 < int(response.headers["Retry-After"]) <= 60


def test_response_tokens_are_capped(fake: FakeClient) -> None:
    ask([user("Hi")])

    assert fake.requests[0]["max_tokens"] == settings.max_response_tokens


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_rate_limiter_minute_window() -> None:
    clock = Clock()
    limiter = RateLimiter([(2, 60)], clock)

    assert limiter.hit("a") is None
    clock.now += 10
    assert limiter.hit("a") is None
    assert limiter.hit("a") == 50
    assert limiter.hit("b") is None
    clock.now += 50
    assert limiter.hit("a") is None


def test_rate_limiter_day_window() -> None:
    clock = Clock()
    limiter = RateLimiter([(10, 60), (3, 86400)], clock)

    for _ in range(3):
        assert limiter.hit("a") is None
        clock.now += 120
    assert limiter.hit("a") == 86400 - 360
