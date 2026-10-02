import os

from langchain_core.documents import Document
from langchain_groq import ChatGroq

SYSTEM_INSTRUCTION = """You are a document question-answering assistant.
Answer only from the provided context.
If the context does not contain enough information, say:
"I couldn't find that information in the uploaded documents."
Do not invent facts.
Keep answers clear and concise.
"""


def _format_context(docs: list[Document]) -> str:
    blocks = []
    for doc in docs:
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "?")
        blocks.append(f"[Source: {source}, Page: {page}]\n{doc.page_content}")
    return "\n\n---\n\n".join(blocks)


def _source_labels(docs: list[Document]) -> list[str]:
    seen = set()
    result = []
    for doc in docs:
        label = f"{doc.metadata.get('source', 'Unknown')} — page {doc.metadata.get('page', '?')}"
        if label not in seen:
            seen.add(label)
            result.append(label)
    return result


def answer_question(question: str, vector_store, chat_history: list = None, k: int = 5, filter_files: list = None):
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY is not set.")

    # Apply filtering logic if files are selected
    search_kwargs = {"k": k}
    if filter_files:
        # FAISS in Langchain supports a callable filter function
        search_kwargs["filter"] = lambda metadata: metadata.get("source") in filter_files

    docs = vector_store.similarity_search(question, **search_kwargs)
    context = _format_context(docs)

    history_text = ""
    if chat_history:
        history_text = "Previous Conversation:\n"
        for msg in chat_history[-6:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

    prompt = f"""{SYSTEM_INSTRUCTION}

{history_text}

Context:
{context}

Question:
{question}

Answer:
"""

    model = ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0,
        max_tokens=800,
    )
    
    stream = model.stream(prompt)
    sources = _source_labels(docs)
    
    return stream, sources

def compare_documents(doc1_name: str, doc2_name: str, vector_store):
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY is not set.")

    # Extract relevant contexts from both docs using vector similarity
    query = "What are the key terms, purpose, summary, and clauses of this document?"
    
    docs1 = vector_store.similarity_search(query, k=8, filter=lambda m: m.get("source") == doc1_name)
    context1 = _format_context(docs1)

    docs2 = vector_store.similarity_search(query, k=8, filter=lambda m: m.get("source") == doc2_name)
    context2 = _format_context(docs2)

    prompt = f"""You are a professional analyst. 
Compare the following two documents based on their extracted content.

DOCUMENT 1 ({doc1_name}):
{context1}

DOCUMENT 2 ({doc2_name}):
{context2}

Please provide a detailed side-by-side comparison matrix and highlight the key differences, additions, or missing clauses between the two documents. Format your response clearly in Markdown with tables and bullet points.
"""

    model = ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0.2,
        max_tokens=800,
    )
    
    stream = model.stream(prompt)
    return stream
