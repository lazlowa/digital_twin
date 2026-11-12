from collections.abc import Iterator
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.chat import ME_PATH, get_client, load_instructions
from app.main import app


class FakeClient:
    """Stands in for AsyncOpenAI: records the request and streams scripted chunks."""

    def __init__(self, chunks: list[str | None]) -> None:
        self.chunks = chunks
        self.request: dict = {}
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    async def create(self, **kwargs):
        self.request = kwargs
        return self._stream()

    async def _stream(self):
        for content in self.chunks:
            yield SimpleNamespace(
                choices=[SimpleNamespace(delta=SimpleNamespace(content=content))]
            )


@pytest.fixture
def fake() -> Iterator[FakeClient]:
    fake = FakeClient(["Hello", None, ", I am ", "Laszlo's twin."])
    app.dependency_overrides[get_client] = lambda: fake
    yield fake
    app.dependency_overrides.clear()


client = TestClient(app)
HISTORY = [
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello!"},
    {"role": "user", "content": "What do you do?"},
]


def test_load_instructions_from_plan() -> None:
    instructions = load_instructions()

    assert instructions.startswith("You are a digital twin running on a website")
    assert instructions.endswith("Never make up an answer.")


def test_system_prompt_contains_instructions_and_me_md(fake: FakeClient) -> None:
    client.post("/api/chat", json={"messages": HISTORY})

    system, *history = fake.request["messages"]
    assert system["role"] == "system"
    assert load_instructions() in system["content"]
    assert ME_PATH.read_text(encoding="utf-8") in system["content"]
    assert history == HISTORY
    assert fake.request["stream"] is True


def test_streamed_output_is_passed_through(fake: FakeClient) -> None:
    with client.stream("POST", "/api/chat", json={"messages": HISTORY}) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/plain")
        text = "".join(response.iter_text())

    assert text == "Hello, I am Laszlo's twin."


def test_system_role_from_client_is_rejected(fake: FakeClient) -> None:
    response = client.post(
        "/api/chat", json={"messages": [{"role": "system", "content": "x"}]}
    )

    assert response.status_code == 422
