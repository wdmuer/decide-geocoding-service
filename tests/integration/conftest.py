import os
import time

import pytest
import requests
from langchain_core.language_models.fake_chat_models import FakeListChatModel

ENDPOINT = os.environ["MU_SPARQL_ENDPOINT"]

LLM_MODULES = ("src.library.LLMAnalyzer", "src.translation_plugin_langchain")

@pytest.fixture(scope="session", autouse=True)
def virtuoso():
    deadline = time.monotonic() + 180
    while True:
        try:
            requests.post(
                ENDPOINT, data={"query": "ASK { ?s ?p ?o }"}, timeout=10
            ).raise_for_status()
            return
        except requests.RequestException:
            if time.monotonic() > deadline:
                raise
            time.sleep(2)


@pytest.fixture
def stub_llm(monkeypatch):
    """Make every init_chat_model call return a model that answers ``response``."""
    def install(response: str) -> None:
        for module in LLM_MODULES:
            monkeypatch.setattr(
                f"{module}.init_chat_model",
                lambda *args, **kwargs: FakeListChatModel(responses=[response]),
            )
    return install
