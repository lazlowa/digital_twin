import json
import smtplib
from collections.abc import Iterator
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app import tools
from app.chat import ME_PATH, get_client, load_instructions
from app.main import app


def text(content: str | None) -> SimpleNamespace:
    return SimpleNamespace(content=content, tool_calls=None)


def tool_call(index: int, id: str | None, name: str | None, args: str):
    function = SimpleNamespace(name=name, arguments=args)
    call = SimpleNamespace(index=index, id=id, function=function)
    return SimpleNamespace(content=None, tool_calls=[call])


class FakeClient:
    """Stands in for AsyncOpenAI: records requests and streams one scripted round
    of deltas per request."""

    def __init__(self, rounds: list[list[SimpleNamespace]]) -> None:
        self.rounds = rounds
        self.requests: list[dict] = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    async def create(self, **kwargs):
        self.requests.append({**kwargs, "messages": list(kwargs["messages"])})
        return self._stream(self.rounds[len(self.requests) - 1])

    async def _stream(self, deltas):
        for delta in deltas:
            yield SimpleNamespace(choices=[SimpleNamespace(delta=delta)])


def use(fake: FakeClient) -> FakeClient:
    app.dependency_overrides[get_client] = lambda: fake
    return fake


@pytest.fixture(autouse=True)
def reset_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def fake() -> FakeClient:
    return use(FakeClient([[text("Hello"), text(None), text(", I am "), text("X.")]]))


@pytest.fixture
def sent(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, str]]:
    sent: list[tuple[str, str]] = []
    monkeypatch.setattr(tools, "send_email", lambda *email: sent.append(email))
    return sent


def unknown_question_rounds() -> list[list[SimpleNamespace]]:
    question = json.dumps({"question": "What is your favourite dish?"})
    return [
        [
            tool_call(0, "call_1", "record_unknown_question", question[:10]),
            tool_call(0, None, None, question[10:]),
        ],
        [text("I don't "), text("know.")],
    ]


client = TestClient(app)
HISTORY = [
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello!"},
    {"role": "user", "content": "What is your favourite dish?"},
]


def chat_text() -> str:
    with client.stream("POST", "/api/chat", json={"messages": HISTORY}) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/plain")
        assert response.headers["x-content-type-options"] == "nosniff"
        return "".join(response.iter_text())


def test_load_instructions_from_plan() -> None:
    instructions = load_instructions()

    assert instructions.startswith("You are a digital twin running on a website")
    assert instructions.endswith("Never make up an answer.")


def test_system_prompt_contains_instructions_and_me_md(fake: FakeClient) -> None:
    client.post("/api/chat", json={"messages": HISTORY})

    system, *history = fake.requests[0]["messages"]
    assert system["role"] == "system"
    assert load_instructions() in system["content"]
    assert ME_PATH.read_text(encoding="utf-8") in system["content"]
    assert history == HISTORY
    assert fake.requests[0]["stream"] is True


def test_streamed_output_is_passed_through(fake: FakeClient) -> None:
    assert chat_text() == "Hello, I am X."


def test_tools_are_offered_on_every_request(sent: list) -> None:
    fake = use(FakeClient(unknown_question_rounds()))

    chat_text()

    assert len(fake.requests) == 2
    for request in fake.requests:
        names = [tool["function"]["name"] for tool in request["tools"]]
        assert names == ["record_unknown_question", "record_visitor_contact"]


def test_tool_call_runs_and_result_goes_back_to_model(sent: list) -> None:
    fake = use(FakeClient(unknown_question_rounds()))

    reply = chat_text()

    [(subject, body)] = sent
    assert "What is your favourite dish?" in body
    *_, assistant, result = fake.requests[1]["messages"]
    assert assistant["tool_calls"][0]["id"] == "call_1"
    assert assistant["tool_calls"][0]["function"]["name"] == "record_unknown_question"
    assert result == {
        "role": "tool",
        "tool_call_id": "call_1",
        "content": tools.RECORDED,
    }
    assert reply == "I don't know."


def test_smtp_failure_does_not_break_chat(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(*args, **kwargs):
        raise smtplib.SMTPConnectError(421, "unavailable")

    monkeypatch.setattr(tools.smtplib, "SMTP_SSL", refuse)
    fake = use(FakeClient(unknown_question_rounds()))

    reply = chat_text()

    assert fake.requests[1]["messages"][-1]["content"] == tools.FAILED
    assert reply == "I don't know."


def test_system_role_from_client_is_rejected(fake: FakeClient) -> None:
    response = client.post(
        "/api/chat", json={"messages": [{"role": "system", "content": "x"}]}
    )

    assert response.status_code == 422
