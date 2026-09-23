"""Unit tests for the pure helpers in ``src/helper_functions.py``."""
import pytest

from src.helper_functions import (
    clean_house_number,
    clean_string,
    extract_house_and_bus_number,
    fail_if_no_successes,
    form_addresses,
    form_locations,
    get_start_end_offsets,
    split_addresses,
)
from tests.fakes import FakeEntity


class TestCleanString:
    def test_collapses_newlines_and_repeated_whitespace(self):
        assert clean_string("  Sint-\nPietersnieuwstraat   25 \n") == "Sint- Pietersnieuwstraat 25"

    def test_leaves_a_clean_string_untouched(self):
        assert clean_string("Kerkstraat 1") == "Kerkstraat 1"


class TestCleanHouseNumber:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("1, 2, 3", ["1", "2", "3"]),
            ("1 en 2", ["1", "2"]),
            ("huisnummer 5", ["5"]),
            ("5/7", ["5", "7"]),
        ],
    )
    def test_splits_on_separators(self, raw, expected):
        assert clean_house_number(raw) == expected

    def test_expands_a_short_dash_range_inclusively(self):
        assert clean_house_number("10-12") == ["10", "11", "12"]

    def test_keeps_endpoints_of_an_implausibly_wide_range(self):
        # Ranges of 20 or more are treated as two separate numbers rather than
        # expanded, to avoid generating hundreds of bogus addresses.
        assert clean_house_number("1-100") == [1, 100]

    def test_tot_en_met_range_is_inclusive(self):
        assert clean_house_number("1 tot en met 5") == ["1", "2", "3", "4", "5"]

    def test_tot_range_excludes_the_upper_bound(self):
        assert clean_house_number("1 tot 5") == ["1", "2", "3", "4"]

    def test_does_not_split_a_bus_number_on_the_slash(self):
        assert clean_house_number("12 bus 3") == ["12 bus 3"]


class TestExtractHouseAndBusNumber:
    def test_splits_bus_number(self):
        assert extract_house_and_bus_number("12 bus 3") == {"housenumber": "12", "bus": 3}

    def test_plain_number_has_no_bus(self):
        assert extract_house_and_bus_number("12") == {"housenumber": "12", "bus": None}

    def test_slash_suffix_is_dropped(self):
        assert extract_house_and_bus_number("12/4") == {"housenumber": "12", "bus": None}


class TestGetStartEndOffsets:
    def test_finds_every_occurrence(self):
        assert get_start_end_offsets("aa bb aa", "aa") == [(0, 2), (6, 8)]

    def test_returns_empty_when_absent(self):
        assert get_start_end_offsets("aa bb", "cc") == []

    def test_does_not_loop_forever_on_overlapping_matches(self):
        assert get_start_end_offsets("aaaa", "aa") == [(0, 2), (2, 4)]


class TestFailIfNoSuccesses:
    def test_raises_when_every_item_failed(self):
        with pytest.raises(RuntimeError, match="0/3 succeeded"):
            fail_if_no_successes("Entity mapping", 3, 0, [ValueError("boom")])

    def test_silent_when_at_least_one_succeeded(self):
        fail_if_no_successes("Entity mapping", 3, 1, [ValueError("boom")])

    def test_silent_when_nothing_was_attempted(self):
        fail_if_no_successes("Entity mapping", 0, 0, [])

    def test_message_samples_at_most_three_errors(self):
        errors = [ValueError(f"e{i}") for i in range(10)]
        with pytest.raises(RuntimeError) as excinfo:
            fail_if_no_successes("Entity mapping", 10, 0, errors)
        assert "e3" not in str(excinfo.value)


class TestFormAddresses:
    def test_groups_street_housenumber_and_city_into_one_address(self):
        entities = [
            FakeEntity("Kerkstraat", "STREET"),
            FakeEntity("1", "HOUSENUMBERS"),
            FakeEntity("Gent", "CITY"),
        ]
        addresses = form_addresses(entities)
        assert len(addresses) == 1
        assert addresses[0]["name"] == "Kerkstraat"
        assert addresses[0]["house_numbers"] == ["1"]
        assert addresses[0]["city"] == "Gent"

    def test_falls_back_to_the_default_city(self):
        entities = [FakeEntity("Kerkstraat", "STREET"), FakeEntity("1", "HOUSENUMBERS")]
        assert form_addresses(entities, from_city="Brugge")[0]["city"] == "Brugge"

    def test_a_street_without_a_housenumber_is_not_an_address(self):
        assert form_addresses([FakeEntity("Kerkstraat", "STREET")]) == []


class TestFormLocations:
    def test_a_street_alone_is_a_location(self):
        locations = form_locations([FakeEntity("Kerkstraat", "STREET")])
        assert len(locations) == 1
        assert locations[0]["type"] == "STREET"

    def test_separate_streets_become_separate_locations(self):
        locations = form_locations(
            [FakeEntity("Kerkstraat", "STREET"), FakeEntity("Dorpsstraat", "ROAD")]
        )
        assert [loc["name"] for loc in locations] == ["Kerkstraat", "Dorpsstraat"]


class TestSplitAddresses:
    def test_fans_a_multi_housenumber_address_into_one_per_number(self):
        grouped = [
            {
                "name": "Kerkstraat",
                "house_numbers": ["1", "2"],
                "postcode": "9000",
                "city": "Gent",
                "spacy_entities": [],
            }
        ]
        individual = split_addresses(grouped)
        assert [a["house_number"] for a in individual] == ["1", "2"]
        assert all(a["type"] == "HOUSE" for a in individual)

    def test_carries_the_bus_number_through(self):
        grouped = [
            {
                "name": "Kerkstraat",
                "house_numbers": ["12 bus 3"],
                "postcode": None,
                "city": "Gent",
                "spacy_entities": [],
            }
        ]
        assert split_addresses(grouped)[0]["bus"] == 3
