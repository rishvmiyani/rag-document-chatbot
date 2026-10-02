from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_DIR = Path("vectorstore")


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def build_vector_store(documents: list[Document]) -> FAISS:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    store = FAISS.from_documents(chunks, get_embeddings())
    VECTOR_DIR.mkdir(exist_ok=True)
    store.save_local(str(VECTOR_DIR))
    return store


def load_vector_store() -> FAISS:
    return FAISS.load_local(
        str(VECTOR_DIR),
        get_embeddings(),
        allow_dangerous_deserialization=True,
    )
