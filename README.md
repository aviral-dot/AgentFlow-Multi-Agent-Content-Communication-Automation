# 🚀 AgentFlow — Multi-Agent Content & Communication Automation

> An agentic AI automation platform with a **Streamlit frontend**, **FastAPI backend**, **LangGraph multi-agent orchestration**, **MCP-based Gmail integration**, **Groq LLM inference**, and **NVIDIA content-safety guardrails**.

---

## 📌 Overview

**AgentFlow** is a multi-agent AI automation system that allows users to interact with specialized AI workflows through a web-based **Streamlit interface**.

Instead of sending every request directly to a single LLM chain, AgentFlow uses a **Supervisor-based LangGraph architecture** to understand the user's request and route it to the appropriate specialized agent.

Currently, the system supports:

* ✍️ **Blog Generation**
* 📧 **Gmail Email Automation**
* 🛡️ **Input Content Safety**
* 🛡️ **Output Content Safety**
* 🔌 **MCP-based Gmail Tool Integration**
* 🧠 **Structured LLM Outputs**
* ⚡ **FastAPI Backend**
* 🎨 **Streamlit Frontend**

---

# 🏗️ System Architecture

The application follows a frontend → API → agent orchestration architecture:

```text
                         ┌──────────────────────┐
                         │        User          │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Streamlit Frontend │
                         │        UI            │
                         └──────────┬───────────┘
                                    │
                                    │ HTTP
                                    ▼
                         ┌──────────────────────┐
                         │    FastAPI Backend   │
                         │       /chat          │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Input Safety Layer  │
                         │       NVIDIA        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      LangGraph       │
                         │      Supervisor      │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
             ┌──────────────┐               ┌──────────────┐
             │  Blog Agent  │               │  Email Agent │
             └───────┬──────┘               └───────┬──────┘
                     │                              │
                     ▼                              ▼
              Blog Generation                  Structured Email
                                                    │
                                                    ▼
                                               MCP Tool
                                                    │
                                                    ▼
                                            Gmail MCP Server
                                                    │
                                                    ▼
                                                Gmail API
                    │                              │
                    └──────────────┬───────────────┘
                                   ▼
                         ┌──────────────────────┐
                         │ Output Safety Layer  │
                         │       NVIDIA        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   FastAPI Response   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Streamlit Frontend │
                         │    Display Result    │
                         └──────────────────────┘
```

---

# 🎨 Streamlit Frontend

AgentFlow provides a dedicated **Streamlit frontend** for interacting with the multi-agent system.

The frontend acts as the user-facing layer while FastAPI handles the backend API and agent execution.

### Frontend capabilities

* 💬 Interactive chat interface
* ✍️ Blog generation requests
* 📧 Email automation requests
* 🤖 Agent workflow interaction
* 📋 Structured response rendering
* ⚠️ Error handling
* 🔄 API request handling
* 🎨 Markdown response rendering
* 🧩 Separation between frontend and backend

### User interaction flow

```text
                    User
                     │
                     ▼
            ┌─────────────────┐
            │ Streamlit Chat  │
            │      UI         │
            └────────┬────────┘
                     │
                     │ HTTP POST
                     ▼
            ┌─────────────────┐
            │ FastAPI /chat   │
            └────────┬────────┘
                     │
                     ▼
              Agent Workflow
                     │
                     ▼
               Final Result
                     │
                     ▼
            ┌─────────────────┐
            │ Streamlit UI    │
            │ Render Response │
            └─────────────────┘
```

---

# ✨ Key Features

## 🎨 1. Streamlit AI Interface

The Streamlit application provides a simple conversational interface for interacting with AgentFlow.

Users can enter natural-language requests such as:

```text
Write a blog about the future of AI agents.
```

or:

```text
Send an email to rahul@example.com about tomorrow's meeting.
```

The frontend sends the request to the FastAPI backend and displays the resulting response.

---

## 🧠 2. Supervisor-Based Multi-Agent Architecture

AgentFlow uses **LangGraph** to orchestrate specialized workflows.

The Supervisor analyzes the user's request and selects the appropriate agent:

```text
                    User Request
                         │
                         ▼
                    Supervisor
                         │
                  ┌──────┴──────┐
                  ▼             ▼
               Blog Agent   Email Agent
```

This makes the system modular and easier to extend with additional agents.

---

# ✍️ 3. Blog Generation Agent

The Blog Agent follows a multi-step workflow:

```text
User Request
     │
     ▼
Title Generation
     │
     ▼
Content Generation
     │
     ▼
Final Blog
```

### Capabilities

* Generates blog titles
* Produces detailed blog content
* Supports Markdown-formatted output
* Separates title generation from content generation
* Maintains state across the workflow

Example request:

```text
Write a blog about Generative AI.
```

The Supervisor identifies the request as a blog-generation task and routes it to the Blog Agent.

---

# 📧 4. Email Automation Agent

The Email Agent converts natural-language requests into structured email information.

Example:

```text
Send an email to rahul@example.com about tomorrow's meeting.
```

The agent extracts structured information:

```json
{
  "to": "rahul@example.com",
  "subject": "Tomorrow's Meeting",
  "body": "..."
}
```

The structured email is then passed to the MCP Gmail tool.

---

# 🔌 5. MCP-Based Gmail Tool Integration

AgentFlow uses the **Model Context Protocol (MCP)** to separate email functionality from the core agent workflow.

```text
Email Agent
     │
     ▼
Email Tool
     │
     ▼
MCP Client
     │
     ▼
stdio transport
     │
     ▼
gmail_mcp_server.py
     │
     ▼
Gmail API
     │
     ▼
Email Sent
```

The MCP server exposes an email-sending capability:

```text
send_email
```

with:

```text
to
subject
body
```

This keeps external tool execution isolated from the main LangGraph workflow.

---

# 🛡️ 6. AI Content Safety Guardrails

AgentFlow includes a content-safety layer using an NVIDIA safety model through the NVIDIA API.

The system performs two safety checks.

### Input Safety

```text
User Input
    │
    ▼
NVIDIA Content Safety
    │
 ┌──┴────┐
 ▼       ▼
Safe   Unsafe
 │       │
 ▼       ▼
Graph   Block
```

Unsafe requests are rejected before reaching the agent workflow.

### Output Safety

```text
Generated Response
       │
       ▼
NVIDIA Content Safety
       │
    ┌──┴────┐
    ▼       ▼
   Safe   Unsafe
    │       │
    ▼       ▼
 Return    Block
```

This provides a basic defense-in-depth safety architecture.

---

# 🏗️ Application Architecture

AgentFlow separates the frontend, backend, agent orchestration, and external tools.

```text
┌──────────────────────────────────────────────────────┐
│                   Streamlit UI                       │
│                                                      │
│  Chat Interface │ User Input │ Response Rendering    │
└─────────────────────────┬────────────────────────────┘
                          │
                          │ HTTP
                          ▼
┌──────────────────────────────────────────────────────┐
│                    FastAPI                           │
│                                                      │
│                 /chat API Endpoint                   │
└─────────────────────────┬────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────┐
│                 Safety Layer                         │
│                                                      │
│              NVIDIA Content Safety                   │
└─────────────────────────┬────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────┐
│                  LangGraph                           │
│                                                      │
│                  Supervisor                          │
└─────────────────────────┬────────────────────────────┘
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
      ┌──────────────┐          ┌──────────────┐
      │  Blog Agent  │          │  Email Agent │
      └──────┬───────┘          └──────┬───────┘
             │                         │
             ▼                         ▼
      Blog Generation             MCP Email Tool
                                       │
                                       ▼
                                Gmail MCP Server
                                       │
                                       ▼
                                   Gmail API
             │                         │
             └────────────┬────────────┘
                          ▼
                  Output Safety
                          │
                          ▼
                  FastAPI Response
                          │
                          ▼
                  Streamlit Frontend
```

---

# 🛠️ Tech Stack

| Technology     | Purpose                                      |
| -------------- | -------------------------------------------- |
| **Python**     | Core application development                 |
| **Streamlit**  | Interactive frontend and chat UI             |
| **FastAPI**    | Backend REST API                             |
| **LangGraph**  | Multi-agent orchestration                    |
| **LangChain**  | LLM integration                              |
| **Groq**       | Fast LLM inference                           |
| **Pydantic**   | Structured data validation                   |
| **MCP**        | External tool integration                    |
| **Gmail API**  | Email authentication and delivery            |
| **NVIDIA API** | Content-safety checking                      |
| **Uvicorn**    | ASGI server                                  |
| **uv**         | Python environment and dependency management |

---

# 📁 Project Structure

```text
RAGFury-Agentic-Knowledge-Retrieval-Research-System/
│
├── app.py
├── gmail_auth.py
├── gmail_mcp_server.py
├── langgraph.json
├── pyproject.toml
├── requirements.txt
├── uv.lock
├── request.json
├── test_nemo.py
├── streamlit_app.py
├── README.md
│
└── src/
    │
    ├── graphs/
    │   ├── __init__.py
    │   └── graph_builder.py
    │
    ├── llms/
    │   ├── __init__.py
    │   └── groqllm.py
    │
    ├── nodes/
    │   ├── __init__.py
    │   ├── supervisor_node.py
    │   ├── blog_node.py
    │   └── mail_node.py
    │
    ├── states/
    │   ├── __init__.py
    │   └── blogstate.py
    │
    └── tools/
        └── email_tool.py
```

> If your Streamlit file has a different name, such as `frontend.py` or `ui.py`, replace `streamlit_app.py` above with the actual filename.

---

# 🔄 Request Lifecycle

Every user request follows this pipeline:

```text
1. User
      ↓
2. Streamlit Frontend
      ↓
3. HTTP Request
      ↓
4. FastAPI Backend
      ↓
5. Input Validation
      ↓
6. NVIDIA Input Safety
      ↓
7. LangGraph Supervisor
      ↓
8. Specialized Agent
      ↓
9. Tool Execution
      ↓
10. Generated Response
      ↓
11. NVIDIA Output Safety
      ↓
12. FastAPI Response
      ↓
13. Streamlit UI
      ↓
14. User
```

---

# 🖥️ Running the Application

AgentFlow uses two processes:

```text
Streamlit Frontend
       │
       │ HTTP
       ▼
FastAPI Backend
       │
       ▼
LangGraph Agents
```

## 1. Start the FastAPI Backend

Activate your virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

Then run:

```bash
python app.py
```

Or:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

---

## 2. Start Streamlit

Open a **second terminal** in the same project directory.

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

Run:

```bash
streamlit run streamlit_app.py
```

Streamlit will provide a local URL similar to:

```text
http://localhost:8501
```

Open that URL in your browser.

---

# 🔐 Environment Variables

Create a local `.env` file:

```env
GROQ_API_KEY=your_groq_api_key

NVIDIA_API_KEY=your_nvidia_api_key

LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=AgentFlow
```

If your Streamlit frontend communicates with FastAPI through an environment variable, you can also configure:

```env
BACKEND_URL=http://localhost:8000
```

### ⚠️ Security

Never commit:

```text
.env
credentials.json
token.json
.venv/
```

to GitHub.

API keys and OAuth tokens should always remain outside version control.

---

# 📧 Gmail Configuration

To enable Gmail automation:

### 1. Configure Gmail OAuth

Create Google OAuth credentials and save them locally as:

```text
credentials.json
```

### 2. Authenticate

```bash
python gmail_auth.py
```

This generates:

```text
token.json
```

Keep both files private.

---

# 🧪 API

The Streamlit frontend communicates with the FastAPI backend.

## Health Check

```http
GET /
```

Example response:

```json
{
  "message": "Multi-Agent AI System is running"
}
```

---

## Chat Endpoint

```http
POST /chat
```

Example request:

```json
{
  "query": "Write a blog about Generative AI"
}
```

The Streamlit frontend sends this request to the backend.

---

# ✍️ Blog Workflow

```text
Streamlit
    │
    ▼
FastAPI /chat
    │
    ▼
Input Safety
    │
    ▼
Supervisor
    │
    ▼
Blog Agent
    │
    ├──► Title Generation
    │
    └──► Content Generation
             │
             ▼
       Output Safety
             │
             ▼
        Streamlit UI
```

---

# 📧 Email Workflow

Example user request:

```text
Send an email to rahul@example.com about tomorrow's meeting.
```

Flow:

```text
Streamlit
    │
    ▼
FastAPI /chat
    │
    ▼
Input Safety
    │
    ▼
Supervisor
    │
    ▼
Email Agent
    │
    ▼
Structured Email
    │
    ▼
MCP Email Tool
    │
    ▼
Gmail MCP Server
    │
    ▼
Gmail API
    │
    ▼
Output Safety
    │
    ▼
Streamlit UI
```

---

# 🧠 Why Streamlit + FastAPI?

The frontend and backend are intentionally separated.

### Streamlit

Responsible for:

* User interface
* Chat interaction
* Input collection
* Response rendering
* Frontend state

### FastAPI

Responsible for:

* API endpoints
* Request validation
* Agent execution
* Safety checks
* Backend orchestration

This separation makes the application easier to:

* Develop
* Debug
* Test
* Deploy
* Extend
* Replace the frontend later

For example, the Streamlit frontend can eventually be replaced by React without rewriting the agent architecture.

---

# 📈 Current Implementation

### Frontend

* [x] Streamlit interface
* [x] Chat-based interaction
* [x] Backend API integration
* [x] Response rendering

### Backend

* [x] FastAPI backend
* [x] `/chat` endpoint
* [x] Request validation
* [x] LangGraph workflow

### Agent System

* [x] Supervisor routing
* [x] Blog Agent
* [x] Email Agent
* [x] Structured LLM outputs
* [x] Groq LLM integration

### Tools

* [x] MCP integration
* [x] Gmail MCP server
* [x] Gmail API integration

### AI Safety

* [x] NVIDIA content-safety integration
* [x] Input safety validation
* [x] Output safety validation

---

# 🗺️ Roadmap

## Phase 1 — Agent Engineering

* [x] Supervisor routing
* [x] Specialized Blog Agent
* [x] Specialized Email Agent
* [x] LangGraph orchestration
* [x] Structured outputs
* [x] MCP tool integration

## Phase 2 — Frontend

* [x] Streamlit interface
* [x] Conversational UI
* [x] Backend API integration
* [x] Response rendering
* [ ] Streaming agent responses
* [ ] Agent execution status
* [ ] Conversation history
* [ ] Better error handling

## Phase 3 — AI Safety & Evaluation

* [x] NVIDIA content safety
* [x] Input safety validation
* [x] Output safety validation
* [ ] Prompt-injection evaluation
* [ ] DeepEval evaluation suite
* [ ] Automated quality evaluation
* [ ] Granular tool authorization

## Phase 4 — Observability & Reliability

* [ ] LangSmith observability
* [ ] Distributed/request tracing
* [ ] LLM latency monitoring
* [ ] Error tracking
* [ ] Retry mechanisms
* [ ] Rate limiting
* [ ] Response caching

## Phase 5 — Advanced Agentic Capabilities

* [ ] Additional specialized agents
* [ ] Long-term memory
* [ ] Context engineering
* [ ] Tool selection
* [ ] Human-in-the-loop workflows
* [ ] Adaptive model selection

---

# 🎯 Engineering Goals

AgentFlow is designed as a practical exploration of modern **AI/LLM application engineering**, focusing on:

* Multi-agent system design
* Supervisor-based orchestration
* Graph-based workflows
* Structured LLM outputs
* Tool calling
* Model Context Protocol
* API-based AI systems
* Streamlit application development
* AI safety
* Content moderation
* Authentication
* External tool integration
* Production-oriented architecture

---

# 🚀 Future Architecture

The long-term goal is to evolve AgentFlow into a complete agentic workflow platform.

```text
                         ┌───────────────┐
                         │     User      │
                         └───────┬───────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │ Streamlit / Web │
                        │      UI         │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   API Gateway   │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  Safety Layer   │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │    Supervisor   │
                        └────────┬────────┘
                                 │
             ┌───────────────────┼───────────────────┐
             │                   │                   │
             ▼                   ▼                   ▼
         Blog Agent         Email Agent        Search Agent
             │                   │                   │
             ▼                   ▼                   ▼
         Content              MCP Tools           RAG/Web
             │                   │                   │
             └───────────────────┼───────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │ Output Safety   │
                        └────────┬────────┘
                                 │
                                 ▼
                              User
```

---

# 🤝 Contributing

Contributions and suggestions are welcome.

```bash
git checkout -b feature/new-agent
```

Make your changes, commit them, and open a Pull Request.

---

# 📄 License

This project is currently intended for learning, experimentation, and development purposes.

---

# 👨‍💻 Author

**Aviral**

GitHub: [@aviral-dot](https://github.com/aviral-dot)

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐.

**AgentFlow — From LLM calls to controlled agentic workflows.**


