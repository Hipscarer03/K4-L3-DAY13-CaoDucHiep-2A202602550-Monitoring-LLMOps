from __future__ import annotations

import time

from .incidents import STATE
from .tracing import get_langfuse_client, tracing_enabled

CORPUS = {
    "refund": ["Refunds are available within 7 days with proof of purchase."],
    "monitoring": ["Metrics detect incidents, logs identify affected requests, traces localize the root cause."],
    "policy": ["Do not expose PII in logs. Use sanitized summaries only."],
}


def retrieve(message: str) -> list[str]:
    """Retrieve context documents for the given message.

    Instrumented as a Langfuse 'retriever' observation so document lookups
    appear as a dedicated child span in the trace.
    """
    langfuse = get_langfuse_client()

    if tracing_enabled():
        with langfuse.start_as_current_observation(
            as_type="span",
            name="document-retrieval",
            input={"query": message},
            metadata={"observation_type_hint": "retriever"},
        ) as retriever_span:
            docs = _do_retrieve(message)
            retriever_span.update(
                output={"documents": docs, "doc_count": len(docs)},
                metadata={
                    "observation_type_hint": "retriever",
                    "corpus_size": len(CORPUS),
                    "matched": len(docs) > 0 and docs[0] != "No domain document matched. Use general fallback answer.",
                },
            )
            return docs
    else:
        return _do_retrieve(message)


def _do_retrieve(message: str) -> list[str]:
    """Core retrieval logic, separated for clean instrumentation."""
    if STATE["tool_fail"]:
        raise RuntimeError("Vector store timeout")
    if STATE["rag_slow"]:
        time.sleep(2.5)
    lowered = message.lower()
    for key, docs in CORPUS.items():
        if key in lowered:
            return docs
    return ["No domain document matched. Use general fallback answer."]
