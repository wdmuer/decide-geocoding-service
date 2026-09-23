import pytest
from decide_ai_service_base.sparql_config import GRAPHS

from . import tasks

TASK_URI = "http://example.org/test/task/empty-expression"
EMPTY_CONTENT_MESSAGE = "empty content, nothing was processed"

ERROR_MESSAGES = """
SELECT ?message WHERE {
  GRAPH <%s> {
    ?error a <http://mu.semte.ch/vocabularies/ext/ErrorMessage> ;
           <http://purl.org/dc/terms/description> ?message
  }
}
"""


def test_empty_expression_content_fails_the_task_and_logs_an_error():
    tasks.seed("empty_expression")

    with pytest.raises(RuntimeError, match=EMPTY_CONTENT_MESSAGE):
        tasks.run(TASK_URI)

    assert tasks.status(TASK_URI) == tasks.FAILED
    rows = tasks.bindings(ERROR_MESSAGES % GRAPHS["data_containers"])
    assert any(EMPTY_CONTENT_MESSAGE in r["message"]["value"] for r in rows), rows
