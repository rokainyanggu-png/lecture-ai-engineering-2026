from types import SimpleNamespace

import app.ask as ask_module


class FakeChat:
    def __init__(self):
        self.questions = []

    def send_message(self, question):
        self.questions.append(question)
        return SimpleNamespace(
            text=f"回答: {question}",
            usage_metadata=SimpleNamespace(
                prompt_token_count=3,
                candidates_token_count=5,
            ),
        )


def test_interactive_mode_reuses_chat_for_follow_up_questions(monkeypatch, capsys):
    chat = FakeChat()
    client = SimpleNamespace(
        chats=SimpleNamespace(
            create=lambda model: chat,
        )
    )
    monkeypatch.setattr(ask_module.genai, "Client", lambda api_key: client)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(
        "sys.argv",
        ["app.ask", "--interactive", "最初の質問"],
    )
    questions = iter(["続けて質問", "/exit"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(questions))

    ask_module.main()

    assert chat.questions == ["最初の質問", "続けて質問"]
    output = capsys.readouterr().out
    assert "回答: 最初の質問" in output
    assert "回答: 続けて質問" in output
    assert output.count("[usage] input=3 output=5") == 2