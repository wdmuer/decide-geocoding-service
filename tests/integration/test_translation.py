from . import tasks

TASK_URI = "http://example.org/test/task/translation"
TRANSLATED = "The municipal council decides on works in the Kerkstraat in Ghent."


def test_translation_writes_annotation_and_succeeds(stub_llm):
    stub_llm(TRANSLATED)
    tasks.seed("translation")

    tasks.run(TASK_URI)

    assert tasks.status(TASK_URI) == tasks.SUCCESS
    values = tasks.ai_graph_values()
    assert TRANSLATED in values, values
