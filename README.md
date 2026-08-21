# 🚀 AgentFlow — Multi-Agent Content & Communication Automation

> **AgentFlow** is a production-oriented multi-agent AI automation system that combines **LangGraph orchestration, an LLM Gateway, NVIDIA AI safety guardrails, MCP-based Gmail integration, Human-in-the-Loop approval, FastAPI, and Streamlit** into a single workflow-driven application.

AgentFlow intelligently routes user requests to specialized AI agents for **blog generation** and **email automation**, while applying security checks and requiring explicit human approval before an email is sent.

---

## 🎯 What is AgentFlow?

Traditional LLM applications often send every user request directly to a single model.

AgentFlow instead uses a **supervisor-based multi-agent architecture**:

```text
                         ┌─────────────────────┐
                         │        User         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Streamlit UI      │
                         └──────────┬──────────┘
                                    │ HTTP
                                    ▼
                         ┌─────────────────────┐
                         │   FastAPI Backend   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Input Guardrails   │
                         │ NVIDIA / NeMo       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  LangGraph          │
                         │  Supervisor         │
                         └──────────┬──────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                     ▼                             ▼
             ┌───────────────┐             ┌───────────────┐
             │   Blog Agent  │             │  Email Agent  │
             └───────┬───────┘             └───────┬───────┘
                     │                             │
                     ▼                             ▼
              Blog Generation                Email Draft
                                                   │
                                                   ▼
                                           Human Approval
                                             │       │
                                      Reject │       │ Approve
                                             │       ▼
                                             │   MCP Email Tool
                                             │       │
                                             │       ▼
                                             │  Gmail MCP Server
                                             │       │
                                             │       ▼
                                             │    Gmail API
                                             │
                                             ▼
                                           END

                     ┌──────────────────────────────┐
                     │     Output Safety Layer      │
                     │       NVIDIA Safety          │
                     └──────────────────────────────┘
```

The architecture separates:

* User interface
* API layer
* LLM infrastructure
* Agent orchestration
* AI safety
* External tool execution
* Human approval

This makes the system easier to extend and replace individual components without redesigning the complete application.

---

# ✨ Key Features

## 🤖 1. Supervisor-Based Multi-Agent Routing

AgentFlow uses **LangGraph** to orchestrate specialized agents.

The Supervisor receives the user's request and produces a structured routing decision:

```text
User Request
     │
     ▼
 Supervisor
     │
 ┌───┴────┐
 │        │
 ▼        ▼
BLOG    EMAIL
```

The routing decision is constrained using Pydantic structured output:

```python
Literal["blog", "email"]
```

This prevents the supervisor from returning arbitrary routing values.

The current Supervisor supports:

* Blog generation requests
* Email composition/sending requests

The supervisor itself uses an asynchronous LLM invocation.

---

# 🧠 2. Centralized LLM Gateway

AgentFlow now includes a dedicated **LLM Gateway** instead of allowing individual agents to directly depend on a specific model provider.

```text
                    ┌──────────────────┐
                    │   Agent / Node    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    LLM Gateway   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   LiteLLM Router │
                    └────────┬─────────┘
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
          Primary Model           Fallback Model
             Groq                    Gemini
```

The gateway currently provides:

* Centralized model configuration
* LiteLLM routing
* Primary model selection
* Optional fallback model
* Retry configuration
* Request timeout configuration
* Routing strategy configuration
* Cached LangChain LLM instances

The primary model and fallback model are configurable through environment variables.

### Example configuration

```env
PRIMARY_LLM_MODEL=groq/openai/gpt-oss-20b
FALLBACK_LLM_MODEL=gemini/gemini-3.7-flash

LLM_ROUTING_STRATEGY=simple-shuffle
LLM_NUM_RETRIES=2
LLM_TIMEOUT=60
```

This abstraction allows the underlying LLM provider to be changed without rewriting every agent.

---

# ✍️ 3. Blog Generation Agent

The Blog Agent follows a two-stage workflow:

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

### Title Generation

The first node generates a creative and SEO-friendly title.

### Content Generation

The second node generates detailed Markdown-formatted blog content.

Both operations use asynchronous LLM calls:

```python
await self.llm.ainvoke(...)
```

The generated title is passed into the next graph state before content generation.

### Example

```text
User:
Write a blog about Generative AI

        ↓

Supervisor
        ↓
Blog Agent
        ↓
Title Creation
        ↓
Content Generation
        ↓
Final Blog
```

---

# 📧 4. Email Automation Agent

The Email Agent converts a natural-language request into a structured email.

For example:

```text
Send an email to rahul@example.com
about tomorrow's meeting.
```

The LLM produces:

```json
{
  "to": "rahul@example.com",
  "subject": "Tomorrow's Meeting",
  "body": "..."
}
```

The email schema is validated using Pydantic:

```python
class EmailDraft(BaseModel):
    to: str
    subject: str
    body: str
```

The Email Agent uses structured JSON output from the LLM before passing the email to the next stage.

---

# 👤 5. Human-in-the-Loop Email Approval

One of the major features of AgentFlow is **Human-in-the-Loop approval before external side effects**.

The system never directly sends an LLM-generated email.

Instead:

```text
Natural Language Request
          │
          ▼
      Email Agent
          │
          ▼
    Structured Draft
          │
          ▼
   Human Approval
      │       │
      │       │
   Reject   Approve
      │       │
      ▼       ▼
     END   Send Email
```

The approval node uses LangGraph's `interrupt()` mechanism.

The user receives a preview containing:

* Recipient
* Subject
* Email body

and must explicitly choose:

```text
✅ Approve
```

or

```text
❌ Reject
```

The approval decision is then passed back to the FastAPI backend through:

```text
POST /email/approval
```

The backend resumes the graph using:

```python
Command(resume=decision)
```

This creates a clear human authorization boundary before an external action is executed.

---

# 🔌 6. MCP-Based Gmail Integration

AgentFlow uses the **Model Context Protocol (MCP)** to isolate Gmail operations from the main agent workflow.

```text
Email Agent
    │
    ▼
EmailTool
    │
    ▼
MCP Client
    │
    │ stdio
    ▼
gmail_mcp_server.py
    │
    ▼
Gmail API
    │
    ▼
Email Sent
```

The application exposes a Gmail MCP tool:

```text
send_email
```

with:

```text
to
subject
body
```

The MCP server creates a MIME email, encodes it using URL-safe Base64, and sends it through the Gmail API.

### Why MCP?

MCP provides a clean separation between:

```text
Agent Reasoning
       │
       ▼
Tool Interface
       │
       ▼
External System
```

This makes the Gmail integration replaceable without tightly coupling Gmail API code to the agent nodes.

---

# 🛡️ 7. AI Safety & Guardrails

AgentFlow implements security at multiple stages.

```text
User Input
    │
    ▼
Input Guardrails
    │
    ▼
Agent Workflow
    │
    ▼
Generated Output
    │
    ▼
Output Safety
    │
    ▼
User
```

## Input Safety

The input pipeline uses NVIDIA/NeMo Guardrails for:

* Content safety
* Jailbreak detection
* Topic control

The current guardrail configuration uses separate models for these checks.

### Input safety categories include

* Violence
* Sexual content
* Criminal planning
* Weapons-related harmful instructions
* Controlled substances
* Self-harm
* Hate/identity-based violence
* Privacy abuse
* Harassment
* Threats
* Other clearly harmful content

The prompts also explicitly allow normal information such as:

* Names
* Email addresses
* URLs
* Company names
* Blog topics
* Public figures
* General knowledge requests

This helps avoid treating ordinary user information as unsafe.

---

# 🔐 8. Jailbreak & Topic Protection

The input guardrail layer also checks whether a request attempts to:

* Extract system prompts
* Obtain hidden instructions
* Obtain API keys or credentials
* Bypass security controls
* Disable guardrails
* Manipulate internal agents
* Abuse internal tools
* Override security policies

The topic-control layer also ensures that requests remain relevant to the capabilities supported by the application.

---

# 🛡️ 9. Output Safety

Generated responses are also passed through an NVIDIA safety model before being returned to the user.

```text
Generated Response
        │
        ▼
NVIDIA Safety Model
        │
   ┌────┴────┐
   ▼         ▼
 Safe      Unsafe
   │         │
   ▼         ▼
Return     Block
```

The application uses:

```text
nvidia/llama-3.1-nemotron-safety-guard-8b-v3
```

for output classification.

The implementation follows a **fail-closed** approach for output safety: if the safety check fails, the output is not returned.

---

# ⚡ 10. Asynchronous Agent Execution

Agent nodes use asynchronous LLM calls:

```python
await llm.ainvoke(...)
```

This is important because LLM requests are I/O-bound operations.

Using async execution allows the FastAPI/LangGraph application to avoid unnecessarily blocking the event loop while waiting for external model APIs.

Async execution is used across:

* Supervisor
* Blog Agent
* Email Agent
* Guardrail calls
* MCP email tool
* FastAPI graph execution

---

# 🌐 11. FastAPI Backend

FastAPI acts as the backend API layer.

Current endpoints include:

### Health Check

```http
GET /
```

Example response:

```json
{
  "message": "Multi-Agent AI System is running"
}
```

### Chat

```http
POST /chat
```

Request:

```json
{
  "query": "Write a blog about Generative AI"
}
```

### Email Approval

```http
POST /email/approval
```

Request:

```json
{
  "thread_id": "your-thread-id",
  "decision": "approve"
}
```

or:

```json
{
  "thread_id": "your-thread-id",
  "decision": "reject"
}
```

The `/chat` endpoint performs input validation, input safety checks, LangGraph execution, output safety validation, and response formatting.

---

# 🎨 12. Streamlit Frontend

The frontend is implemented using Streamlit.

It provides:

* Chat interface
* Backend connectivity status
* Agent response rendering
* Response timing
* Security-block notifications
* Email preview
* Human approval buttons
* Email rejection flow
* Conversation display
* Clear-chat functionality

The frontend communicates with FastAPI through HTTP.

### Email approval UI

```text
┌────────────────────────────────────┐
│ ⚠️ Human approval required         │
│                                    │
│ To: user@example.com               │
│ Subject: Meeting Tomorrow          │
│                                    │
│ Body:                              │
│ ┌────────────────────────────────┐ │
│ │ Email content...               │ │
│ └────────────────────────────────┘ │
│                                    │
│   [ ✅ Approve ] [ ❌ Reject ]     │
└────────────────────────────────────┘
```

---

# 🔄 Complete Request Lifecycle

Every request follows the following high-level pipeline:

```text
1. User
   ↓
2. Streamlit
   ↓
3. FastAPI /chat
   ↓
4. Input Validation
   ↓
5. Input Guardrails
   ├── Content Safety
   ├── Jailbreak Detection
   └── Topic Control
   ↓
6. LangGraph Supervisor
   ↓
7. Specialized Agent
   ├── Blog Agent
   └── Email Agent
   ↓
8. Tool Execution
   │
   └── Gmail MCP
   ↓
9. Output Safety
   ↓
10. FastAPI Response
   ↓
11. Streamlit
   ↓
12. User
```

For email requests, the workflow additionally introduces a human authorization checkpoint before Gmail execution.

---

# 🧩 LangGraph Workflow

The current graph is structured as:

```text
                         START
                           │
                           ▼
                     ┌───────────┐
                     │ Supervisor│
                     └─────┬─────┘
                           │
                ┌──────────┴──────────┐
                │                     │
              BLOG                  EMAIL
                │                     │
                ▼                     ▼
        ┌──────────────┐       ┌─────────────┐
        │Title Creation│       │ Draft Email │
        └──────┬───────┘       └──────┬──────┘
               │                      │
               ▼                      ▼
        ┌──────────────┐       ┌─────────────┐
        │Content       │       │Human        │
        │Generation    │       │Approval     │
        └──────┬───────┘       └──────┬──────┘
               │                  ┌────┴────┐
               │               Reject      Approve
               │                  │           │
               │                  ▼           ▼
               │                 END      Send Email
               │                              │
               ▼                              ▼
              END                            END
```

The graph currently contains:

* Supervisor node
* Title creation node
* Content generation node
* Email drafting node
* Email approval node
* Email sending node

Conditional routing determines both the initial agent and the post-approval email path.

---

# 🧪 Evaluation

AgentFlow includes a dedicated blog evaluation suite using **DeepEval**.

```text
evals/
└── blog/
    ├── dataset.py
    ├── metrics.py
    └── test_blog_eval.py
```

The current dataset contains test topics covering:

* Artificial intelligence in healthcare
* Cloud computing
* Large language models
* Renewable energy
* Cybersecurity

## Evaluation Metrics

The evaluation suite currently includes:

### Answer Relevancy

Measures whether the generated title/output is relevant to the requested topic.

Threshold:

```text
0.80
```

### Blog Quality

A GEval-based metric evaluates:

* Topic relevance
* Directness
* Coherence
* Organization
* Information quality
* Clarity
* Markdown formatting

Threshold:

```text
0.80
```

The evaluation model currently uses a Groq-hosted Llama model.

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
├── request.json
├── streamlit_app.py
├── uv.lock
│
├── evals/
│   └── blog/
│       ├── __init__.py
│       ├── dataset.py
│       ├── metrics.py
│       └── test_blog_eval.py
│
└── src/
    │
    ├── gateway/
    │   ├── config.py
    │   └── llm_gateway.py
    │
    ├── graphs/
    │   ├── __init__.py
    │   └── graph_builder.py
    │
    ├── guardrails/
    │   ├── config.yml
    │   ├── guardrail.py
    │   └── prompts.yml
    │
    ├── Human_in_the_loop_middleware/
    │   └── mail_approval_human_in_the _loop.py
    │
    ├── llms/
    │   └── ...
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

The repository currently separates orchestration, gateway infrastructure, guardrails, agents, state, tools, evaluations, and frontend/backend entry points.

---

# 🛠️ Technology Stack

| Technology          | Purpose                                              |
| ------------------- | ---------------------------------------------------- |
| **Python**          | Core application                                     |
| **LangGraph**       | Agent orchestration                                  |
| **LangChain**       | LLM abstraction                                      |
| **LiteLLM**         | LLM routing and fallback                             |
| **FastAPI**         | Backend API                                          |
| **Streamlit**       | Frontend UI                                          |
| **Groq**            | Primary LLM provider                                 |
| **Gemini**          | Optional fallback provider                           |
| **Pydantic**        | Structured output validation                         |
| **MCP**             | External tool integration                            |
| **Gmail API**       | Email delivery                                       |
| **NVIDIA API**      | Content safety                                       |
| **NeMo Guardrails** | Input safety, topic control and jailbreak protection |
| **DeepEval**        | LLM evaluation                                       |
| **Uvicorn**         | ASGI server                                          |
| **uv**              | Python environment/dependency management             |

The current dependency configuration includes FastAPI, LangChain, LangGraph, LiteLLM, MCP, NeMo Guardrails, Streamlit and the Google API packages.

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/aviral-dot/AgentFlow-Multi-Agent-Content-Communication-Automation.git

cd AgentFlow-Multi-Agent-Content-Communication-Automation
```

## 2. Create the environment

Using `uv`:

```bash
uv sync
```

Or create a traditional virtual environment:

```bash
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\Activate.ps1
```

---

# 🔑 Environment Configuration

Create a `.env` file in the project root.

```env
# Primary LLM
GROQ_API_KEY=your_groq_api_key

# Optional fallback
GEMINI_API_KEY=your_gemini_api_key

# LLM Gateway
PRIMARY_LLM_MODEL=groq/openai/gpt-oss-20b
FALLBACK_LLM_MODEL=gemini/gemini-3.7-flash
LLM_ROUTING_STRATEGY=simple-shuffle
LLM_NUM_RETRIES=2
LLM_TIMEOUT=60

# NVIDIA Safety
NVIDIA_API_KEY=your_nvidia_api_key

# LangSmith - optional
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=AgentFlow

# Frontend
BACKEND_URL=http://localhost:8000
```

The LLM Gateway validates that the primary Groq credential exists before initialization.

---

# 📧 Gmail OAuth Setup

To enable real Gmail sending, configure Google OAuth credentials.

## 1. Create OAuth credentials

Create Gmail OAuth credentials through Google Cloud.

Place the downloaded credentials file in the project root:

```text
credentials.json
```

## 2. Authenticate

Run:

```bash
python gmail_auth.py
```

This generates:

```text
token.json
```

The Gmail MCP server loads this token and requests the Gmail `send` scope.

### Never commit

```text
.env
credentials.json
token.json
```

to GitHub.

---

# ▶️ Running AgentFlow

AgentFlow runs as two processes.

```text
Streamlit
    │
    │ HTTP
    ▼
FastAPI
    │
    ▼
LangGraph
```

## Terminal 1 — FastAPI

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

Swagger documentation:

```text
http://localhost:8000/docs
```

## Terminal 2 — Streamlit

```bash
streamlit run streamlit_app.py
```

Frontend:

```text
http://localhost:8501
```

---

# 🧪 Running Evaluations

The blog evaluation suite is located at:

```text
evals/blog/
```

Run DeepEval tests using the project's configured environment and test runner.

The evaluation suite uses predefined blog prompts and evaluates generated results for relevance and overall blog quality.

---

# 🔐 Security Architecture

AgentFlow follows a defense-in-depth approach.

```text
                 USER
                   │
                   ▼
          ┌─────────────────┐
          │ Input Validation │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ Input Guardrail │
          │                 │
          │ Content Safety  │
          │ Jailbreak       │
          │ Topic Control   │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ LangGraph Agent │
          └────────┬────────┘
                   │
             ┌─────┴─────┐
             │           │
             ▼           ▼
          Content      Email
                       │
                       ▼
                 Human Approval
                       │
                       ▼
                   Gmail MCP
                       │
                       ▼
                  Gmail API
                   │
                   ▼
          ┌─────────────────┐
          │ Output Safety   │
          └────────┬────────┘
                   │
                   ▼
                  USER
```

This architecture provides multiple independent security boundaries rather than relying solely on the primary LLM.

---

# 🧠 Design Principles

AgentFlow is built around several important AI engineering principles:

### 1. Separation of concerns

Frontend, API, orchestration, LLM infrastructure, safety, and external tools are separated.

### 2. Structured outputs

Pydantic models constrain critical LLM outputs such as:

```text
SupervisorDecision
EmailDraft
```

### 3. Centralized LLM infrastructure

Agents obtain their models through the LLM Gateway rather than directly depending on individual providers.

### 4. Human authorization for side effects

External actions such as sending email require explicit user approval.

### 5. Defense-in-depth security

Input and output safety checks are performed independently.

### 6. Tool isolation

Gmail operations are isolated behind an MCP interface.

### 7. Async I/O

External LLM, guardrail, and MCP operations use asynchronous execution where appropriate.

### 8. Evaluation-driven development

The repository includes an evaluation suite rather than relying exclusively on manual testing.

---

# 📊 Current Implementation Status

| Component                           | Status                 |
| ----------------------------------- | ---------------------- |
| Streamlit frontend                  | ✅ Implemented          |
| FastAPI backend                     | ✅ Implemented          |
| LangGraph orchestration             | ✅ Implemented          |
| Supervisor routing                  | ✅ Implemented          |
| Blog Agent                          | ✅ Implemented          |
| Email Agent                         | ✅ Implemented          |
| Structured LLM output               | ✅ Implemented          |
| Async LLM execution                 | ✅ Implemented          |
| LLM Gateway                         | ✅ Implemented          |
| LiteLLM routing                     | ✅ Implemented          |
| Optional LLM fallback               | ✅ Implemented          |
| MCP integration                     | ✅ Implemented          |
| Gmail API integration               | ✅ Implemented          |
| Gmail OAuth                         | ✅ Implemented          |
| Human-in-the-Loop approval          | ✅ Implemented          |
| NVIDIA input safety                 | ✅ Implemented          |
| NVIDIA output safety                | ✅ Implemented          |
| Jailbreak detection                 | ✅ Configured           |
| Topic control                       | ✅ Configured           |
| DeepEval evaluation                 | ✅ Implemented          |
| LangSmith integration               | ⚙️ Configured/optional |
| Persistent production checkpointing | 🚧 Future improvement  |
| Distributed rate limiting           | 🚧 Future improvement  |
| Production cache backend            | 🚧 Future improvement  |
| Authentication/authorization        | 🚧 Future improvement  |
| Metrics dashboard                   | 🚧 Future improvement  |
| Production deployment configuration | 🚧 Future improvement  |

---

# 🚧 Production Roadmap

The current project has the core architecture of a production-oriented AI application, but several infrastructure capabilities should still be added before calling it fully production-ready.

## Phase 1 — Reliability

* [ ] Persistent LangGraph checkpointer
* [ ] Durable Human-in-the-Loop state
* [ ] Retry policies
* [ ] Timeout handling
* [ ] Better exception taxonomy
* [ ] Idempotency for email sending

## Phase 2 — Security

* [ ] API authentication
* [ ] User authorization
* [ ] Per-user Gmail credentials
* [ ] Tool-level authorization
* [ ] Secret management
* [ ] Audit logging

## Phase 3 — Performance

* [ ] Redis-based caching
* [ ] Request rate limiting
* [ ] Connection pooling
* [ ] Background execution for long-running workflows
* [ ] LLM cost tracking

## Phase 4 — Observability

* [ ] LangSmith tracing
* [ ] Structured application logs
* [ ] Prometheus metrics
* [ ] Grafana dashboards
* [ ] Latency monitoring
* [ ] Token/cost monitoring
* [ ] Error tracking

## Phase 5 — Evaluation

* [ ] Expanded evaluation datasets
* [ ] Email-agent evaluation
* [ ] Supervisor-routing evaluation
* [ ] Guardrail evaluation
* [ ] Prompt-injection tests
* [ ] Regression evaluation in CI/CD

## Phase 6 — Deployment

* [ ] Docker image
* [ ] Docker Compose environment
* [ ] Production environment configuration
* [ ] HTTPS
* [ ] Health/readiness probes
* [ ] CI/CD pipeline

---

# 📈 Why This Project Matters

AgentFlow demonstrates practical implementation of modern AI application engineering concepts:

* Multi-agent systems
* Supervisor-based routing
* LangGraph workflows
* Structured LLM outputs
* LLM Gateway architecture
* Multi-provider LLM routing
* LLM fallback strategies
* Async LLM execution
* MCP tool integration
* Gmail API integration
* Human-in-the-Loop workflows
* AI safety guardrails
* Jailbreak detection
* Topic control
* Output moderation
* FastAPI backend architecture
* Streamlit frontend architecture
* LLM evaluation with DeepEval
* Production-oriented AI system design

The project therefore goes beyond a simple "LLM chatbot" and demonstrates how an AI application can be structured as a **workflow-driven, tool-using, safety-aware multi-agent system**.

---

# 🔮 Future Architecture

The long-term goal is to evolve AgentFlow into a more complete enterprise AI automation platform:

```text
                         ┌──────────────┐
                         │     User     │
                         └──────┬───────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │ Web / Streamlit UI   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     API Gateway      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Security & Auth      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Agent Supervisor   │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        Blog Agent       Email Agent       Future Agents
              │                │
              │                ▼
              │        Human Approval
              │                │
              │                ▼
              │           MCP Tools
              │                │
              │                ▼
              │          External APIs
              │
              └────────────┬───────────────────┘
                           │
                           ▼
                    Output Guardrails
                           │
                           ▼
                    Observability
                           │
                           ▼
                       Response
```

---

# 👨‍💻 Author

**Aviral**

Built as a practical exploration of production-oriented **AI Engineering, LLMOps, agent orchestration, AI safety, tool integration, and evaluation**.

---

# ⭐ Project

If you find the project useful, consider giving the repository a star.

**Repository:**
[AgentFlow — Multi-Agent Content & Communication Automation](https://github.com/aviral-dot/AgentFlow-Multi-Agent-Content-Communication-Automation?utm_source=chatgpt.com)



