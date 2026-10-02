from langchain_core.documents import Document

from src.chatbot import _format_context, _source_labels


def test_context_contains_document_text():
    docs = [Document(page_content="Python is a programming language.",
                     metadata={"source": "test.pdf", "page": 1})]
    context = _format_context(docs)
    assert "Python is a programming language." in context
    assert "test.pdf" in context


def test_sources_are_unique():
    docs = [
        Document(page_content="A", metadata={"source": "test.pdf", "page": 1}),
        Document(page_content="B", metadata={"source": "test.pdf", "page": 1}),
    ]
    assert _source_labels(docs) == ["test.pdf — page 1"]
