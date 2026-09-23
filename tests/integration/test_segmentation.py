import json

from . import tasks

TASK_URI = "http://example.org/test/task/segmentation"

MOTIVATION = "Overwegende dat de weg beschadigd is,"
DECISION = "Besluit: de werken worden gegund."

# Line numbers refer to the fixture's expressionContent.
LLM_RESPONSE = json.dumps({
    "document_classification": "besluit",
    "spans": [
        {"tag": "decision_title", "start_line": 1, "end_line": 1},
        {"tag": "motivation", "start_line": 3, "end_line": 3},
        {"tag": "decision", "start_line": 4, "end_line": 4},
    ],
})


def test_segmentation_writes_segments_and_succeeds(stub_llm):
    stub_llm(LLM_RESPONSE)
    tasks.seed("segmentation")

    tasks.run(TASK_URI)

    assert tasks.status(TASK_URI) == tasks.SUCCESS
    # The decision_title span is not written as an annotation.
    values = tasks.ai_graph_values()
    assert {MOTIVATION, DECISION} <= values, values
