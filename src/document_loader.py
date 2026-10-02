from pathlib import Path
from typing import Iterable

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def load_documents(paths: Iterable[Path]) -> list[Document]:
    """Load PDF pages and preserve source/page metadata."""
    documents = []
    for path in paths:
        loader = PyPDFLoader(str(path))
        pages = loader.load()
        for page in pages:
            page.metadata["source"] = path.name
            page.metadata["page"] = int(page.metadata.get("page", 0)) + 1
            documents.append(page)
    return documents
