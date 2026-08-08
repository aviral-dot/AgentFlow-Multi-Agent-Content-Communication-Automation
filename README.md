# AgentFlow — Multi-Agent Content & Communication Automation

> **An AI-powered multi-agent automation system for intelligent blog generation and Gmail-based email communication, built with LangGraph, Groq, FastAPI, and structured agent workflows.**

AgentFlow is a **multi-agent AI system** designed to automate two common productivity workflows:

* ✍️ **Blog Generation** — creates SEO-friendly blog titles and detailed blog content.
* 📧 **Email Automation** — understands email requests, extracts recipient/subject/body, and sends emails through Gmail.

Instead of using a single LLM chain for every request, AgentFlow uses a **Supervisor-based LangGraph workflow** to intelligently route each user request to the appropriate specialized agent.

---

## 🚀 Key Features

### 🧠 Intelligent Request Routing

A Supervisor node analyzes the user's request and determines which specialized workflow should handle it.

```text
                         User Request
                              │
                              ▼
                       ┌─────────────┐
                       │  Supervisor │
                       └──────┬──────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                 BLOG                 EMAIL
                    │                   │
                    ▼                   ▼
             Title Creation       Draft Email
                    │                   │
                    ▼                   ▼
             Content Generation    Send via Gmail
                    │                   │
                    ▼                   ▼
                   END                 END
```

The Supervisor uses structured LLM output to select exactly one route: `blog` or `email`.

---

## ✍️ Blog Agent

The Blog Agent handles content-generation requests through a two-step workflow:

```text
User Request
     │
     ▼
Title Creation
     │
     ▼
Content Generation
     │
     ▼
Final Blog
```

### Capabilities

* Generates creative blog titles
* Produces SEO-friendly titles
* Generates detailed blog content
* Uses Markdown formatting
* Maintains the generated title while producing the final content

---

## 📧 Email Agent

The Email Agent converts natural-language email requests into structured email data.

```text
User Request
     │
     ▼
Email Draft
     │
     ├── Recipient
     ├── Subject
     └── Body
     │
     ▼
Gmail Email Tool
     │
     ▼
Email Sent
```

For example:

```text
Send an email to rahul@example.com regarding tomorrow's meeting.
```

The Email Agent extracts:

```json
{
  "to": "rahul@example.com",
  "subject": "Tomorrow's Meeting",
  "body": "..."
}
```

The structured email is then passed to the Gmail tool for delivery.

---

## 🏗️ Architecture

AgentFlow follows a **Supervisor + Specialized Agents** architecture implemented using LangGraph.

```text
                         ┌─────────────────────┐
                         │     FastAPI API     │
                         │      /chat          │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   LangGraph Graph   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     Supervisor      │
                         │   Route Decision    │
                         └──────────┬──────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                     ▼                             ▼
              ┌──────────────┐              ┌──────────────┐
              │  Blog Agent  │              │ Email Agent  │
              └──────┬───────┘              └──────┬───────┘
                     │                             │
              ┌──────┴───────┐              ┌──────┴───────┐
              ▼              ▼              ▼              ▼
            Title         Content         Draft          Gmail
            Creation      Generation      Email          Sending
```

The main LangGraph workflow defines the Supervisor, Blog, and Email nodes and connects them using conditional routing.

---

## 🛠️ Tech Stack

| Technology    | Purpose                                      |
| ------------- | -------------------------------------------- |
| **Python**    | Core application development                 |
| **LangGraph** | Agent orchestration and workflow management  |
| **LangChain** | LLM integration                              |
| **Groq**      | LLM inference                                |
| **FastAPI**   | Backend REST API                             |
| **Pydantic**  | Structured LLM outputs and validation        |
| **Gmail API** | Email authentication and delivery            |
| **Uvicorn**   | ASGI application server                      |
| **uv**        | Python dependency and environment management |

---

## 📁 Project Structure

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

### Core Components

**`app.py`**

FastAPI entry point. Exposes the `/chat` endpoint and invokes the compiled LangGraph workflow.

**`src/graphs/graph_builder.py`**

Builds and compiles the main LangGraph workflow, including Supervisor routing, Blog nodes, and Email nodes.

**`src/nodes/supervisor_node.py`**

Uses structured LLM output to determine whether a request should be handled by the Blog or Email workflow.

**`src/nodes/blog_node.py`**

Handles blog title generation followed by detailed content generation.

**`src/nodes/mail_node.py`**

Extracts structured email information and invokes the email tool to send the message.

**`src/tools/email_tool.py`**

Provides the Gmail-based email delivery functionality.

---

# 🔄 Request Flow

A request enters the system through the FastAPI `/chat` endpoint.

### Example 1 — Blog

```text
POST /chat

{
  "query": "Write a blog about Generative AI"
}
```

Flow:

```text
Request
   ↓
FastAPI
   ↓
Supervisor
   ↓
Blog Agent
   ↓
Title Generation
   ↓
Content Generation
   ↓
Response
```

### Example 2 — Email

```text
POST /chat

{
  "query": "Send an email to rahul@example.com about tomorrow's meeting"
}
```

Flow:

```text
Request
   ↓
FastAPI
   ↓
Supervisor
   ↓
Email Agent
   ↓
Structured Email Draft
   ↓
Gmail Tool
   ↓
Email Sent
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/aviral-dot/AgentFlow-Multi-Agent-Content-Communication-Automation.git
cd AgentFlow-Multi-Agent-Content-Communication-Automation
```

## 2. Create a virtual environment

Using `uv`:

```bash
uv venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```bash
uv sync
```

Alternatively:

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a local `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=AgentFlow
```

**Never commit `.env`, OAuth credentials, or access/refresh tokens to GitHub.**

The repository intentionally excludes sensitive files such as:

```text
.env
credentials.json
token.json
```

---

# 📧 Gmail Setup

To enable email sending, configure Google OAuth credentials for the Gmail API.

Place your local OAuth client configuration in:

```text
credentials.json
```

Run the authentication flow using:

```bash
python gmail_auth.py
```

The generated OAuth token should remain local and should **never be committed to Git**.

---

# ▶️ Running the Application

Start the FastAPI server:

```bash
python app.py
```

The API will run on:

```text
http://localhost:8000
```

You can also run it using Uvicorn:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

# 🧪 API Usage

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

## Chat

```http
POST /chat
```

Request:

```json
{
  "query": "Write a blog about AI agents"
}
```

The system automatically determines the appropriate workflow.

---

# 🧩 Why Multi-Agent Architecture?

A single general-purpose LLM can perform both tasks, but separating responsibilities into specialized workflows provides several advantages:

* **Clear separation of responsibilities**
* **More predictable routing**
* **Easier testing and debugging**
* **Independent agent development**
* **Better workflow control**
* **Easy extension with additional agents**

The current architecture can be extended with additional specialized capabilities without redesigning the entire system.

For example:

```text
                    Supervisor
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
     Blog             Email           Future Agent
     Agent            Agent              │
                                     ┌────┴────┐
                                     ▼         ▼
                                   Search    Calendar
```

---

# 🔒 Current Security Considerations

AgentFlow keeps credentials outside the repository through environment variables and Git exclusions.

The project is also structured so that security and validation layers can be added around the existing LangGraph workflow.

### Planned enhancements

* 🛡️ NeMo Guardrails
* 🧪 DeepEval-based evaluation
* 🔍 Prompt injection protection
* 🧹 Input/output validation
* 📊 LLM observability
* ⚡ Caching and performance optimization
* 🧠 Memory support
* 🔐 More robust tool authorization

> These are planned/next-stage improvements and are **not represented as currently implemented features**.

---

# 🗺️ Roadmap

### Phase 1 — Core Multi-Agent System

* [x] Supervisor routing
* [x] Blog generation workflow
* [x] Email drafting workflow
* [x] Gmail email sending
* [x] FastAPI backend
* [x] LangGraph orchestration
* [x] Structured LLM outputs

### Phase 2 — AI Safety & Evaluation

* [ ] NeMo Guardrails
* [ ] Prompt injection protection
* [ ] DeepEval test suite
* [ ] Automated quality evaluation
* [ ] Input/output validation

### Phase 3 — Production Engineering

* [ ] LangSmith/LangFuse observability
* [ ] Request tracing
* [ ] Error handling improvements
* [ ] Rate limiting
* [ ] Response caching
* [ ] Retry mechanisms
* [ ] Tool authorization

### Phase 4 — Advanced Agentic Capabilities

* [ ] Additional specialized agents
* [ ] Long-term memory
* [ ] Context engineering
* [ ] Tool selection
* [ ] Human-in-the-loop workflows
* [ ] Adaptive model selection

---

# 🎯 Project Goals

AgentFlow is designed as a practical exploration of **agent engineering and LLM application development**, focusing on:

* Multi-agent orchestration
* Graph-based workflow design
* Structured LLM outputs
* Tool integration
* API-based AI applications
* AI safety
* Evaluation
* Production-oriented architecture

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/new-agent
```

3. Commit your changes

```bash
git commit -m "Add new agent"
```

4. Push the branch

```bash
git push origin feature/new-agent
```

5. Open a Pull Request

---

# 📄 License

This project is currently available for learning and development purposes.

---

## ⭐ Acknowledgements

Built using:

* LangGraph
* LangChain
* Groq
* FastAPI
* Gmail API
* Pydantic

---

## 👨‍💻 Author

**Aviral**

GitHub:
https://github.com/aviral-dot

---

⭐ If you find this project useful, consider giving the repository a star.
