"""``helpers`` and ``escape_helpers`` come from the mu-python-template base
image, not from requirements.txt, so they are stubbed here."""
import sys
import types


def _install_mu_template_stubs():
    if "helpers" not in sys.modules:
        helpers = types.ModuleType("helpers")
        import logging
        helpers.logger = logging.getLogger("test-stub")
        helpers.query = lambda *a, **k: {}
        helpers.update = lambda *a, **k: None
        sys.modules["helpers"] = helpers

    if "escape_helpers" not in sys.modules:
        escape_helpers = types.ModuleType("escape_helpers")
        escape_helpers.sparql_escape_uri = lambda uri: f"<{uri}>"
        escape_helpers.sparql_escape_string = lambda s: f'"""{s}"""'
        sys.modules["escape_helpers"] = escape_helpers


_install_mu_template_stubs()


class FakeEntity:
    """Stand-in for a spaCy ``Span``; only ``.text`` and ``.label_`` are read."""

    def __init__(self, text, label):
        self.text = text
        self.label_ = label

    def __repr__(self):
        return f"FakeEntity({self.text!r}, {self.label_!r})"
