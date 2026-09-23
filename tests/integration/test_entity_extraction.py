from . import tasks

TASK_URI = "http://example.org/test/task/entity-extraction"


def test_entity_extraction_writes_annotations_and_succeeds():
    tasks.seed("entity_extraction")

    tasks.run(TASK_URI)

    assert tasks.status(TASK_URI) == tasks.SUCCESS
    values = tasks.ai_graph_values()
    assert any("Kerkstraat 25" in v for v in values), values
