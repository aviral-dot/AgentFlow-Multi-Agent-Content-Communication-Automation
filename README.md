# 🚀 AgentFlow — Multi-Agent Content & Communication Automation

> An agentic AI automation system that intelligently routes user requests to specialized workflows for **blog generation** and **Gmail communication**, with **LangGraph orchestration, MCP-based tool integration, FastAPI, Groq LLM inference, and NVIDIA content-safety guardrails**.

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Orchestration-orange)](https://langchain-ai.github.io/langgraph/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Groq](https://img.shields.io/badge/Groq-LLM%20Inference-orange)](https://groq.com/)
[![MCP](https://img.shields.io/badge/MCP-Tool%20Integration-purple)](https://modelcontextprotocol.io/)
[![Gmail API](https://img.shields.io/badge/Gmail-API-red?logo=gmail)](https://developers.google.com/gmail/api)
[![NVIDIA](https://img.shields.io/badge/NVIDIA-Content%20Safety-76B900?logo=nvidia)](https://developer.nvidia.com/)

---

## 📌 Overview

**AgentFlow** is a multi-agent AI automation system designed to handle different productivity tasks through specialized agent workflows.

Instead of sending every request directly to a single LLM chain, AgentFlow uses a **Supervisor-based LangGraph architecture** to understand the user's request and route it to the appropriate specialized agent.

Currently, the system supports:

* ✍️ **Blog Generation**
* 📧 **Gmail Email Automation**
* 🛡️ **Input Content Safety**
* 🛡️ **Output Content Safety**
* 🔌 **MCP-based Gmail Tool Integration**
* 🧠 **Structured LLM Outputs**
* ⚡ **FastAPI-based API**

### High-Level Flow

```text
                         User Request
                              │
                              ▼
                     ┌─────────────────┐
                     │  FastAPI /chat  │
                     └────────┬────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  Input Safety Check │
                   │      NVIDIA         │
                   └─────────┬───────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Supervisor   │
                    │    LangGraph    │
                    └────────┬────────┘
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
        ┌────────────────┐      ┌────────────────┐
        │   Blog Agent   │      │   Email Agent  │
        └───────┬────────┘      └───────┬────────┘
                │                       │
                ▼                       ▼
        Title Generation         Structured Email
                │                       │
                ▼                       ▼
        Content Generation       MCP Gmail Tool
                │                       │
                └───────────┬───────────┘
                            ▼
                   ┌──────────────────┐
                   │ Output Safety    │
                   │     NVIDIA       │
                   └────────┬─────────┘
                            │
                            ▼
                         Response
```

---

# ✨ Key Features

## 🧠 1. Supervisor-Based Multi-Agent Architecture

AgentFlow uses **LangGraph** to orchestrate specialized workflows.

A Supervisor analyzes the user's request and selects the appropriate route:

```text
User Request
     │
     ▼
 Supervisor
     │
 ┌───┴────┐
 ▼        ▼
Blog    Email
Agent    Agent
```

This makes the system modular and easier to extend with additional agents.

---

## ✍️ 2. Blog Generation Agent

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

Example:

```json
{
  "query": "Write a blog about AI agents"
}
```

The Supervisor identifies this as a blog request and routes it to the Blog Agent.

---

# 📧 3. Email Automation Agent

The Email Agent converts natural-language requests into structured email information.

Example:

```text
"Send an email to rahul@example.com about tomorrow's meeting"
```

The agent extracts:

```json
{
  "to": "rahul@example.com",
  "subject": "Tomorrow's Meeting",
  "body": "..."
}
```

The structured email is then passed to the Gmail tool for delivery.

---

# 🔌 4. MCP-Based Gmail Tool Integration

AgentFlow uses the **Model Context Protocol (MCP)** to separate the email capability from the main agent workflow.

The architecture is:

```text
Email Agent
     │
     ▼
EmailTool
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

The MCP server exposes an email-sending tool:

```text
send_email
```

with:

```text
to
subject
body
```

This approach keeps external tool execution isolated from the core LangGraph workflow.

---

# 🛡️ 5. AI Content Safety Guardrails

AgentFlow includes a content-safety layer using an NVIDIA safety model through the NVIDIA API.

The system performs **two safety checks**:

### Input Safety

Before the request reaches the agent workflow:

```text
User Query
    │
    ▼
NVIDIA Content Safety
    │
 ┌──┴────┐
Safe   Unsafe
 │        │
 ▼        ▼
Graph   Block
```

Unsafe input is rejected before reaching the LangGraph workflow.

### Output Safety

The generated response is also checked:

```text
LangGraph Response
       │
       ▼
NVIDIA Content Safety
       │
    ┌──┴────┐
   Safe   Unsafe
    │        │
    ▼        ▼
 Return    Block
```

This provides a basic **defense-in-depth approach** for AI-generated content.

---

# 🏗️ Architecture

AgentFlow follows a **Supervisor + Specialized Agents + Tools** architecture.

```text
                         ┌─────────────────────┐
                         │       Client        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI       │
                         │       /chat         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Input Safety Layer │
                         │       NVIDIA        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      LangGraph      │
                         │     Supervisor      │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
             ┌──────────────┐               ┌──────────────┐
             │  Blog Agent  │               │  Email Agent │
             └───────┬──────┘               └───────┬──────┘
                     │                              │
                     ▼                              ▼
              Title Generation               Email Extraction
                     │                              │
                     ▼                              ▼
              Content Generation              MCP Email Tool
                                                    │
                                                    ▼
                                             Gmail MCP Server
                                                    │
                                                    ▼
                                                Gmail API
                    │                              │
                    └──────────────┬───────────────┘
                                   ▼
                         ┌─────────────────────┐
                         │ Output Safety Layer │
                         │       NVIDIA        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                               API Response
```

---

# 🛠️ Tech Stack

| Technology     | Purpose                                        |
| -------------- | ---------------------------------------------- |
| **Python**     | Core application development                   |
| **LangGraph**  | Multi-agent orchestration and workflow control |
| **LangChain**  | LLM integration                                |
| **Groq**       | Fast LLM inference                             |
| **FastAPI**    | Backend REST API                               |
| **Pydantic**   | Structured data validation                     |
| **MCP**        | External tool integration                      |
| **Gmail API**  | Email authentication and delivery              |
| **NVIDIA API** | Content-safety checking                        |
| **Uvicorn**    | ASGI server                                    |
| **uv**         | Python environment and dependency management   |

---

# 📁 Project Structure

```text
AgentFlow-Multi-Agent-Content-Communication-Automation/
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

---

# 🔄 Request Lifecycle

Every request follows a controlled pipeline.

```text
1. User Request
       ↓
2. FastAPI
       ↓
3. Input Validation
       ↓
4. NVIDIA Content Safety
       ↓
5. LangGraph Supervisor
       ↓
6. Specialized Agent
       ↓
7. Tool Execution (if required)
       ↓
8. Generated Response
       ↓
9. NVIDIA Output Safety
       ↓
10. API Response
```

---

# 🧪 API

## Health Check

```http
GET /
```

Response:

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

### Request

```json
{
  "query": "Write a blog about Generative AI"
}
```

### Blog Flow

```text
POST /chat
     ↓
Input Safety
     ↓
Supervisor
     ↓
Blog Agent
     ↓
Title Generation
     ↓
Content Generation
     ↓
Output Safety
     ↓
Response
```

---

### Email Flow

```json
{
  "query": "Send an email to rahul@example.com about tomorrow's meeting"
}
```

Flow:

```text
POST /chat
     ↓
Input Safety
     ↓
Supervisor
     ↓
Email Agent
     ↓
Structured Email
     ↓
MCP Email Tool
     ↓
Gmail MCP Server
     ↓
Gmail API
     ↓
Output Safety
     ↓
Response
```

---

# ⚙️ Installation

## 1. Clone Repository

```bash
git clone https://github.com/aviral-dot/AgentFlow-Multi-Agent-Content-Communication-Automation.git

cd AgentFlow-Multi-Agent-Content-Communication-Automation
```

## 2. Create Virtual Environment

Using `uv`:

```bash
uv venv
```

### Windows

```powershell
.venv\Scripts\Activate.ps1
```

## 3. Install Dependencies

```bash
uv sync
```

Or:

```bash
pip install -r requirements.txt
```

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

### ⚠️ Security

Never commit:

```text
.env
credentials.json
token.json
```

to GitHub.

API keys and OAuth tokens should always remain outside version control.

---

# 📧 Gmail Configuration

To enable Gmail sending:

### 1. Create Google OAuth credentials

Create a Gmail API OAuth client configuration and save it locally as:

```text
credentials.json
```

### 2. Run authentication

```bash
python gmail_auth.py
```

This generates the local OAuth token.

```text
token.json
```

Keep this file private.

---

# ▶️ Running the Application

Start the FastAPI application:

```bash
python app.py
```

Or:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

The API will be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

---

# 🧠 Why Multi-Agent Architecture?

A single LLM could technically perform both tasks.

However, specialized agents provide:

* Clear separation of responsibilities
* Explicit workflow control
* Easier debugging
* Better modularity
* Independent agent development
* Easier tool integration
* Easier future expansion

For example, the architecture can later evolve into:

```text
                    Supervisor
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
      Blog            Email            Search
      Agent           Agent             Agent
                                        │
                                  ┌─────┴─────┐
                                  ▼           ▼
                               Web Tool    RAG Tool
```

---

# 🛡️ Security Architecture

Current security controls include:

```text
                  User Input
                      │
                      ▼
              Content Safety
                  NVIDIA
                      │
                      ▼
               Agent Workflow
                      │
                      ▼
               Tool Execution
                      │
                      ▼
              Generated Output
                      │
                      ▼
              Content Safety
                  NVIDIA
                      │
                      ▼
                  Response
```

Additionally:

* API keys are loaded through environment variables.
* OAuth credentials are kept outside Git.
* Gmail authentication uses OAuth.
* External email functionality is isolated through MCP.
* Structured outputs are used for agent routing and email extraction.

---

# 📈 Current Implementation

### ✅ Implemented

* [x] FastAPI backend
* [x] LangGraph workflow
* [x] Supervisor routing
* [x] Blog Agent
* [x] Email Agent
* [x] Structured LLM outputs
* [x] Groq LLM integration
* [x] Gmail API integration
* [x] MCP-based email tool
* [x] Gmail MCP server
* [x] Input content-safety checking
* [x] Output content-safety checking
* [x] Environment-based secret management

---

# 🗺️ Roadmap

## Phase 1 — Agent Engineering

* [x] Supervisor routing
* [x] Specialized Blog Agent
* [x] Specialized Email Agent
* [x] LangGraph orchestration
* [x] Structured outputs
* [x] MCP tool integration

## Phase 2 — AI Safety & Evaluation

* [x] NVIDIA content-safety integration
* [x] Input safety validation
* [x] Output safety validation
* [ ] Prompt-injection evaluation
* [ ] DeepEval evaluation suite
* [ ] Automated quality evaluation
* [ ] More granular tool authorization

## Phase 3 — Observability & Reliability

* [ ] Distributed/request tracing
* [ ] LangSmith observability
* [ ] LLM latency monitoring
* [ ] Error tracking
* [ ] Retry mechanisms
* [ ] Rate limiting
* [ ] Response caching

## Phase 4 — Advanced Agentic Capabilities

* [ ] Additional specialized agents
* [ ] Long-term memory
* [ ] Context engineering
* [ ] Tool selection
* [ ] Human-in-the-loop workflows
* [ ] Adaptive model selection

---

# 🎯 Engineering Goals

AgentFlow is built as a practical exploration of modern **AI/LLM application engineering**, focusing on:

* Multi-agent system design
* Agent orchestration
* Graph-based workflows
* Structured LLM outputs
* Tool calling
* MCP integration
* API-based AI systems
* AI safety
* Content moderation
* Authentication and authorization
* Production-oriented architecture

---

# 🚀 Future Architecture

The long-term goal is to evolve AgentFlow from a simple two-agent automation system into a more complete **agentic workflow platform**:

```text
                         ┌───────────────┐
                         │     User      │
                         └───────┬───────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   API Gateway   │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │ Safety Layer    │
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

