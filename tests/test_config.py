"""Unit tests for the Pydantic config models in ``src/config.py``."""
import json
import pathlib

import pytest
from pydantic import ValidationError

from src.config import AppConfig, AppSettingsConfig, NerConfig, TranslationConfig

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


class TestRepoConfig:
    def test_repo_config_json_is_valid(self):
        raw = json.loads((REPO_ROOT / "config.json").read_text(encoding="utf-8"))
        config = AppConfig(**raw)
        assert config.ner.language == "nl"

    def test_defaults_alone_produce_a_valid_config(self):
        assert AppConfig().ner.method == "composite"


class TestNormalisation:
    @pytest.mark.parametrize("raw", ["DEBUG", " debug ", "Debug"])
    def test_log_level_is_normalised(self, raw):
        assert AppSettingsConfig(log_level=raw).log_level == "debug"

    def test_translation_provider_is_normalised(self):
        assert TranslationConfig(provider=" LangChain ").provider == "langchain"


class TestValidation:
    @pytest.mark.parametrize("value", [-0.1, 1.1])
    def test_min_confidence_outside_zero_to_one_is_rejected(self, value):
        with pytest.raises(ValidationError):
            NerConfig(min_confidence=value)

    def test_min_confidence_may_be_null_to_disable_filtering(self):
        assert NerConfig(min_confidence=None).min_confidence is None

    def test_unknown_language_is_rejected(self):
        with pytest.raises(ValidationError):
            NerConfig(language="fr")

    def test_unknown_top_level_key_is_rejected(self):
        # AppConfig sets extra="forbid" so a typo in config.json fails loudly
        # at startup rather than being silently ignored.
        with pytest.raises(ValidationError):
            AppConfig(nre={})


class TestSecrets:
    def test_api_key_is_not_exposed_by_repr(self):
        config = AppConfig(segmentation={"llm": {"api_key": "super-secret"}})
        assert "super-secret" not in repr(config)
        assert config.segmentation.llm.api_key.get_secret_value() == "super-secret"
