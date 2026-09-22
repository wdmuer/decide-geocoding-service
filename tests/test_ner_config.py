"""Unit tests for the static tables in ``src/ner_config.py``."""
import re

import pytest

from src.ner_config import LABEL_MAPPINGS, NER_MODELS, REGEX_PATTERNS


class TestRegexPatterns:
    @pytest.mark.parametrize("language", sorted(REGEX_PATTERNS))
    def test_every_pattern_compiles(self, language):
        for pattern_type, patterns in REGEX_PATTERNS[language].items():
            for pattern in patterns:
                re.compile(pattern)

    @pytest.mark.parametrize("language", sorted(REGEX_PATTERNS))
    def test_every_language_has_date_patterns(self, language):
        assert REGEX_PATTERNS[language]["date"]

    @pytest.mark.parametrize(
        "language,text",
        [
            ("nl", "op 02/04/2025 werd beslist"),
            ("nl", "zitting van 2 April 2025"),
            ("de", "am 02.04.2025"),
            ("en", "on June 25, 2021"),
        ],
    )
    def test_a_representative_date_matches(self, language, text):
        assert any(re.search(p, text) for p in REGEX_PATTERNS[language]["date"])


class TestRefinementLabels:
    def test_legal_date_keeps_its_index(self):
        # ner_config documents that label_classes maps model output indices to
        # labels. Reordering the list would silently remap every prediction.
        assert NER_MODELS["refinement"]["label_classes"].index("legal_date") == 6

    def test_label_classes_are_unique(self):
        classes = NER_MODELS["refinement"]["label_classes"]
        assert len(classes) == len(set(classes))

    def test_refinable_labels_are_a_non_empty_subset_of_generic_labels(self):
        assert set(NER_MODELS["refinement"]["refinable_labels"]) == {
            "DATE",
            "LOCATION",
            "LOC",
            "GPE",
        }


class TestLabelMappings:
    def test_spacy_collapses_gpe_and_loc_onto_location(self):
        assert LABEL_MAPPINGS["spacy"]["GPE"] == "LOCATION"
        assert LABEL_MAPPINGS["spacy"]["LOC"] == "LOCATION"

    def test_every_extraction_method_has_a_mapping_table(self):
        assert set(LABEL_MAPPINGS) == {"spacy", "flair", "huggingface", "regex"}

    def test_mapped_values_are_upper_case(self):
        for table in LABEL_MAPPINGS.values():
            for value in table.values():
                assert value == value.upper()


class TestModelTables:
    def test_spacy_and_flair_cover_the_same_languages(self):
        assert set(NER_MODELS["spacy"]) == set(NER_MODELS["flair"])
