# KnowFlow AI

> A multi-user, agentic RAG platform that answers questions from your private documents and the live web — with intelligent query routing and persistent conversation memory.

**Live Demo:** [knowflow-ai-one.vercel.app](https://knowflow-ai-one.vercel.app)

---

## What It Does

Most "Chat with PDF" tools are single-user demos. KnowFlow AI gives each user a **private workspace**.

- **Upload PDFs** — documents are automatically parsed, chunked, embedded, and indexed into a private vector store.
- **Ask questions** — answers are grounded in your own documents with similarity-based retrieval.
- **Go beyond documents** — general questions are answered using live web search when relevant.
- **Intelligent routing** — an LLM decides whether each query needs your documents, the web, or both.
- **Persistent memory** — conversations are stored and resumed across sessions from any device.
- **Complete isolation** — every user's documents, embeddings, and chats are separated at the database level.

---


## Architecture Flow

### 1. User Authentication
- User logs in using **Supabase Auth**.
- Backend verifies the **JWT token** before processing any request.
- Every request is associated with the authenticated user.

⬇️

### 2. Document Upload
- User uploads one or more PDF documents.
- FastAPI extracts the text from each PDF.
- Text is split into overlapping chunks.
- Each chunk is converted into a vector embedding using **Jina AI Embeddings**.
- Chunks and embeddings are stored in **Supabase PostgreSQL + pgvector**.

⬇️

### 3. User Sends a Question
- User asks a question from the chat interface.
- Backend loads recent chat history for context.

⬇️

### 4. Query Routing
- A **Router Agent (LLM)** classifies the query as:
  - **Local** → Answer using uploaded documents.
  - **Web** → Use live web search.
  - **Both** → Combine document retrieval and web search.

⬇️

### 5. Local Retrieval (if needed)
- Backend searches **pgvector** using cosine similarity.
- Only chunks above the similarity threshold are retrieved.
- Weak matches are discarded.

⬇️

### 6. Web Search (if needed)
- Relevant information is fetched using **LangSearch API**.
- Used when the query requires external knowledge or local retrieval is insufficient.

⬇️

### 7. Response Generation
- Retrieved document chunks.
- Web search results (if any).
- Recent conversation history.

These are combined and sent to the **Groq LLM** to generate a grounded response.

⬇️

### 8. Save Conversation
- User message and assistant response are stored in PostgreSQL.
- Route information (`local`, `web`, or `both`) and source references are also saved.

⬇️

### 9. Return Response
The frontend displays:
- AI response
- Source references
- Route badge (Local / Web / Both)
- Updated conversation history


**Query Flow:**

1. User sends a message → backend verifies JWT → loads chat history
2. **Router agent** classifies the query as `local`, `web`, or `both`
3. **Local retrieval** searches pgvector for relevant document chunks (with similarity threshold)
4. **Web fallback** triggers if local retrieval finds nothing useful
5. **Answer generator** produces a grounded response using retrieved context + chat history
6. Response, route, and sources are returned and persisted to the database

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | FastAPI, Uvicorn, Python 3.11 |
| **Database** | Supabase (PostgreSQL + pgvector) |
| **Auth** | Supabase Auth (JWT) |
| **LLM** | Groq (`openai/gpt-oss-20b`) |
| **Embeddings** | Jina AI (`jina-embeddings-v3`, 1024-dim) |
| **Web Search** | LangSearch API |
| **Frontend** | React 18, Vite, Tailwind CSS v4 |
| **Hosting** | Render (backend), Vercel (frontend) |

---

## Key Features

**Agentic Query Routing**
Every query is classified by an LLM as `local`, `web`, or `both`. If local retrieval returns weak matches, the system automatically falls back to web search — no silent failures.

**RAG with Real Retrieval Quality**
PDFs are parsed, chunked with overlap, and embedded using task-aware Jina embeddings. Retrieval runs server-side via a Postgres RPC function with an ivfflat cosine index. A similarity threshold filters out weak context before it reaches the LLM.

**True Multi-User Isolation**
Row Level Security is enabled on every table. Even a bug in the backend cannot leak another user's documents, embeddings, or conversations.

**Persistent Conversation Memory**
Chats and messages are stored in Postgres. Recent history is passed to both the router (for context-aware routing) and the generator (for follow-up resolution).

**Transparent Sources**
Every assistant reply includes a route badge (`local` / `web` / `fallback`) and source previews — document similarity scores or web URLs.

---

## Local Setup

### Backend(Runs on http://localhost:8000. Interactive docs at /docs.)


cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

### Frontend (Runs on http://localhost:5173.)



cd frontend
npm install
cp .env.example .env
npm run dev
