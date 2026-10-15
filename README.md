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

## Architecture
                                   KnowFlow AI Architecture

+----------------------------------------------------------------------------------+
|                                  React + Vite                                    |
|                          Tailwind CSS • Hosted on Vercel                         |
+----------------------------------------------------------------------------------+
                                      |
                                      | HTTPS + JWT
                                      v
+----------------------------------------------------------------------------------+
|                              FastAPI Backend (Render)                            |
|                                                                                  |
|  +----------------+   +----------------+   +----------------------------------+ |
|  | Authentication |   | Chat Service   |   |      Document Service            | |
|  | JWT Validation |   | Save/Retrieve  |   | Upload • Parse • Chunk • Embed   | |
|  +----------------+   +----------------+   +----------------------------------+ |
|                                                                                  |
|                     +-------------------------------------------+                |
|                     |          Router Agent (LLM)               |                |
|                     |   Classifies Query → local / web / both   |                |
|                     +----------------------+--------------------+                |
|                                            |                                     |
|                         +------------------+------------------+                  |
|                         |                                     |                  |
|                         v                                     v                  |
|              +------------------------+            +------------------------+    |
|              |   Local RAG Pipeline    |            |    Web Search Tool     |    |
|              |  pgvector Similarity    |            |      LangSearch        |    |
|              +-----------+-------------+            +-----------+------------+    |
|                          |                                      |                 |
|                          +------------------+-------------------+                 |
|                                             |                                     |
|                                             v                                     |
|                            +-------------------------------+                      |
|                            |      Answer Generator (LLM)   |                      |
|                            | Uses Context + Chat History   |                      |
|                            +---------------+---------------+                      |
|                                            |                                      |
|                                            v                                      |
|                            Response + Sources + Route Badge                       |
+--------------------------------------------+-------------------------------------+
                                             |
                                             v
+----------------------------------------------------------------------------------+
|                                Supabase (PostgreSQL)                             |
|                                                                                  |
|  • Authentication (JWT)                                                          |
|  • Users                                                                         |
|  • Chats & Messages                                                              |
|  • Documents                                                                     |
|  • Embeddings (pgvector + ivfflat cosine index)                                  |
|  • Row Level Security (User Isolation)                                           |
+----------------------------------------------------------------------------------+

                        External AI Services
                        --------------------
                        • Groq → Router + Answer Generation
                        • Jina AI → Embedding Generation
                        • LangSearch → Live Web Search

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
