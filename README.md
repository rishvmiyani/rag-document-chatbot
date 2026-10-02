# 🤖 RAG Document Q&A Chatbot

A production-style beginner-friendly **Retrieval-Augmented Generation (RAG)** chatbot built with Python, LangChain, FAISS, Hugging Face embeddings, Groq (Qwen) and Streamlit.

The application lets users upload PDF documents, indexes their content, retrieves the most relevant chunks for a question, and asks an LLM to generate a grounded answer with source/page references.

## Features

- Upload one or multiple PDFs
- PDF text extraction with PyPDF
- Recursive text chunking
- Local semantic embeddings with `all-MiniLM-L6-v2`
- FAISS vector similarity search
- Ultra-Fast LLM-based answer generation via Groq
- Source and page references
- Hallucination-aware prompt
- Streamlit chat interface
- Automated unit tests

## Architecture

```text
PDF Upload
   ↓
PyPDFLoader
   ↓
Text Chunks
   ↓
Hugging Face Embeddings
   ↓
FAISS Vector Store
   ↓
User Question
   ↓
Similarity Search
   ↓
Top Relevant Chunks
   ↓
OpenAI LLM
   ↓
Grounded Answer + Sources
```

## Project Structure

```text
rag-chatbot/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── src/
│   ├── __init__.py
│   ├── document_loader.py
│   ├── vector_store.py
│   └── chatbot.py
└── tests/
    └── test_rag.py
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Rishv-Miyani/rag-document-chatbot.git
cd rag-document-chatbot
```

### 2. Configure the API key

Create a `.env` file in the root directory (or copy from `.env.example`) and add your Groq API key:

```text
GROQ_API_KEY=your_api_key_here
```

Never commit `.env` to GitHub.

### 3. Run the application (Windows)

The easiest way to run the project on Windows is using the provided `run.bat` script. It automatically sets up the virtual environment, installs dependencies, and launches the app.

```bash
.\run.bat
```

### Alternative Setup (Manual approach for any device)

If you don't use `run.bat` or are on macOS/Linux, follow these terminal commands:

#### Mac/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

#### Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Once running, open the local URL shown by Streamlit in your browser.

## How RAG works here

### 1. Retrieval

The uploaded PDF is split into smaller chunks. Each chunk is converted into an embedding and stored in FAISS.

When the user asks a question, the question is also represented semantically. FAISS finds the most relevant document chunks.

### 2. Augmentation

The retrieved chunks are placed into the LLM prompt as context.

### 3. Generation

The LLM generates an answer using that context. The prompt explicitly tells the model not to invent information when the answer is absent from the documents.

## Example

Upload a company policy PDF and ask:

> What is the leave policy?

The system retrieves the relevant pages and produces an answer such as:

> Employees are entitled to ...

Sources:
- company_policy.pdf — page 4

## Testing

Run:

```bash
pytest
```

## Important security notes

- Keep API keys in `.env`
- Do not upload `.env` to GitHub
- `vectorstore/` is ignored because it can contain generated local data
- Review uploaded documents before sharing the application publicly

## Future Improvements

- Conversation-aware retrieval
- Hybrid keyword + semantic search
- Reranking
- Streaming responses
- Persistent user sessions
- PostgreSQL/pgvector
- Authentication
- Docker deployment
- Evaluation metrics such as retrieval precision and answer faithfulness
