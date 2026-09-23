class FakeEntity:
    """Stand-in for a spaCy ``Span``; only ``.text`` and ``.label_`` are read."""

    def __init__(self, text, label):
        self.text = text
        self.label_ = label

    def __repr__(self):
        return f"FakeEntity({self.text!r}, {self.label_!r})"
