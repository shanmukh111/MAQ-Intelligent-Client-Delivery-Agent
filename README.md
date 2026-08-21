# MAQ Intelligent Client Delivery Agent

An enterprise-style, multi-agent delivery intelligence solution built for MAQ Software using Microsoft Agent Framework (MAF), FastAPI, Azure DevOps MCP, Dataverse, SharePoint, Hybrid RAG, and Microsoft Copilot Studio.

The solution helps delivery managers ask natural-language questions about project health, sprint delivery, utilization, risks, and recommended actions. It routes each request to specialized agents, gathers grounded evidence from enterprise sources, validates the evidence, and produces a concise management response.

---

## Solution Overview

The system uses a three-agent architecture:

```text
User / Copilot Studio
        |
        v
FastAPI Orchestrator
        |
        +--> PII Masking
        +--> Prompt Injection Guard
        +--> Authorization
        +--> Deterministic Routing
        |
        +-------------------------------+
        |                               |
        v                               v
MAQPortfolioEvidenceAgent      MAQEngineeringEvidenceAgent
SharePoint + Dataverse         Azure DevOps MCP + Hybrid RAG
        |                               |
        +---------------+---------------+
                        |
                        v
                 Evidence Validation
                  Retry / Fallback
                        |
                        v
              MAQDeliveryAnalystAgent
                        |
                        v
               Grounded Final Answer
                        |
                        v
              Output Secret Redaction
```

### Agent Responsibilities

**MAQPortfolioEvidenceAgent**
- Retrieves business and project delivery evidence.
- Uses SharePoint project-register data.
- Uses Dataverse time-entry and utilization evidence.
- Returns structured portfolio evidence.
- Does not create the final management recommendation.

**MAQEngineeringEvidenceAgent**
- Retrieves engineering delivery evidence.
- Uses Azure DevOps through MCP.
- Uses Hybrid RAG when guidance or recommendations are requested.
- Preserves deterministic sprint-health calculations.
- Returns structured engineering evidence.

**MAQDeliveryAnalystAgent**
- Receives validated evidence from the Portfolio and Engineering agents.
- Does not directly call enterprise data sources.
- Synthesizes the final management-facing answer.
- Avoids unsupported causal claims across domains.

---

## Key Capabilities

- Multi-agent orchestration with Microsoft Agent Framework
- Conditional routing between portfolio and engineering domains
- Parallel execution for cross-domain queries
- Structured evidence with Pydantic models
- Azure DevOps integration through FastMCP
- SharePoint project-register ingestion
- Dataverse time-entry analysis
- Hybrid RAG using semantic search + BM25 + reciprocal-rank fusion
- Role-based authorization
- PII detection and masking with Microsoft Presidio
- Prompt-injection protection
- Output secret redaction
- Evidence validation with retry and graceful fallback
- Source tracking for grounded responses
- Copilot Studio integration for Microsoft Teams-facing interaction

---

## Technology Stack

| Area | Technology |
|---|---|
| Agent orchestration | Microsoft Agent Framework |
| API layer | FastAPI |
| Agent model client | OpenAI client through Agent Framework |
| MCP | FastMCP |
| Engineering data | Azure DevOps |
| Portfolio data | SharePoint + Dataverse |
| Retrieval | LlamaIndex + ChromaDB + BM25 |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| PII protection | Microsoft Presidio |
| Validation | Pydantic |
| Front-end / user interaction | Microsoft Copilot Studio |
| Source control | GitHub |
| ALM / CI-CD | Azure DevOps Pipelines |

---

## Repository Structure

```text
maq-client-delivery-agent/
├── agents/
│   ├── analyst_agent.py
│   ├── analyst_instructions.py
│   ├── engineering_agent.py
│   ├── engineering_instructions.py
│   ├── engineering_tools.py
│   ├── portfolio_agent.py
│   ├── portfolio_instructions.py
│   ├── portfolio_tools.py
│   ├── project_tools.py
│   └── retrieval_agent.py
│
├── apps/
│   └── api/
│       └── main.py
│
├── connectors/
│   ├── d365_timesheet.py
│   ├── dataverse_timeentry.py
│   └── sharepoint_export.py
│
├── data/
│   ├── d365/
│   ├── knowledge/
│   └── sharepoint/
│
├── mcp_server/
│   └── devops_server.py
│
├── orchestration/
│   ├── delivery_workflow.py
│   ├── evidence_models.py
│   ├── evidence_validation.py
│   ├── prompts.py
│   └── routing.py
│
├── retrieval/
│   ├── hybrid_rag.py
│   └── project_evidence.py
│
├── security/
│   ├── authorization.py
│   ├── output_filter.py
│   ├── pii_filter.py
│   └── prompt_guard.py
│
├── tests/
├── pipelines/
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Prerequisites

- Python
- Git
- Azure DevOps access
- Azure DevOps Personal Access Token for local development
- Dataverse access
- Microsoft Copilot Studio access
- PowerShell
- Microsoft Dev Tunnel for local Copilot Studio integration

> Secrets must never be committed to Git. Store local credentials only in `.env`.

---

## Installation

### 1. Clone the repository

```powershell
git clone <YOUR-REPOSITORY-URL>
cd maq-client-delivery-agent
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file in the project root.

Example:

```text
AZDO_ORG=<azure-devops-organization>
AZDO_PROJECT=<azure-devops-project>
AZDO_PAT=<azure-devops-pat>

APP_ENV=dev

OPENAI_API_KEY=<openai-api-key>
OPENAI_CHAT_MODEL=<model-name>

DATAVERSE_URL=<dataverse-environment-url>
DATAVERSE_API_VERSION=v9.2
DATAVERSE_ENTITY_SET=<dataverse-entity-set>
```

Do not commit `.env`.

---

## Run the API

From the repository root:

```powershell
uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

Health endpoint:

```text
GET /health
```

Primary delivery endpoint:

```text
POST /delivery/query
```

---

## Example Questions

### Engineering-only

```text
What is the health of the current sprint?
```

Expected routing:

```python
{
    "portfolio": False,
    "engineering": True,
    "guidance": False
}
```

### Portfolio-only

```text
What is the health of our active Power BI projects?
```

Expected routing:

```python
{
    "portfolio": True,
    "engineering": False,
    "guidance": False
}
```

### Cross-domain

```text
Are our risky Power BI projects also showing sprint pressure, and what actions should we prioritize?
```

Expected routing:

```python
{
    "portfolio": True,
    "engineering": True,
    "guidance": True
}
```

---

## Deterministic Sprint Health

Sprint health is calculated deterministically from Azure DevOps evidence.

The LLM is not allowed to override the calculated classification.

Example categories:

- On Track
- At Risk
- Behind

This protects delivery-status decisions from model hallucination.

---

## Hybrid RAG

The knowledge layer combines:

- Semantic vector retrieval with ChromaDB
- BM25 keyword retrieval
- Reciprocal-rank fusion
- LlamaIndex orchestration
- Hugging Face sentence-transformer embeddings

Knowledge documents are stored under:

```text
data/knowledge/
```

Hybrid RAG is used only when guidance or recommendations are required.

---

## Security Controls

### Authorization

A deterministic authorization layer validates whether a user is allowed to access:

- Portfolio evidence
- Engineering evidence
- Timesheet / utilization evidence

### PII Protection

Microsoft Presidio detects and masks PII before user content is sent into the agent workflow.

### Prompt Injection Guard

High-confidence prompt-injection and policy-bypass patterns are blocked before agent execution.

### Output Secret Redaction

Final model output is scanned before being returned by FastAPI. Secret-like values such as API keys, bearer tokens, JWTs, passwords, and PAT-style assignments are redacted.

### Source Isolation

The Analyst Agent is instructed not to infer causal relationships between portfolio and engineering evidence unless an explicit mapping exists.

---

## Azure DevOps MCP

The MCP server is implemented in:

```text
mcp_server/devops_server.py
```

Available engineering functions include:

```text
get_project_info
get_active_work_items
get_iterations
get_current_sprint_summary
```

The Engineering Agent uses these tools to obtain grounded Azure DevOps delivery evidence.

The current implementation also prevents repeated use of the same Azure DevOps function during a single Engineering Agent run.

> The current Agent Framework API used for progressive tool removal is marked experimental. This should be reviewed when upgrading Agent Framework versions.

---

## Dataverse Integration

Dataverse provides delivery evidence such as:

- Planned hours
- Actual hours
- Billable hours
- Variance
- Utilization
- Approval status
- High-risk time entries

Local development authentication is handled outside source control. Tokens and credentials are never stored in the repository.

---

## SharePoint Integration

The project register is supplied through SharePoint and Copilot Studio.

The Copilot Studio flow retrieves the workbook, converts the file content to Base64, and sends it to the FastAPI `/delivery/query` endpoint.

The backend parses the workbook and converts it into project evidence for the Portfolio Agent.

---

## Copilot Studio Integration

Copilot Studio acts as the conversational entry point.

Typical flow:

```text
User
  |
  v
Copilot Studio Agent
  |
  v
Power Automate / Agent Flow
  |
  +--> Get SharePoint file content
  |
  +--> POST /delivery/query
  |
  v
FastAPI Multi-Agent Backend
  |
  v
Answer returned to Copilot Studio
```

For the user question input, the flow should pass the original activity text rather than an AI-generated expansion so deterministic routing receives the actual user request.

---

## Testing

Install pytest if required:

```powershell
pip install pytest
```

Run:

```powershell
pytest -v
```

Planned automated coverage includes:

- routing
- authorization
- prompt-injection detection
- output secret redaction
- deterministic delivery-health logic
- evidence validation

---

## ALM / CI-CD

The target ALM process uses GitHub as source control and Azure DevOps Pipelines for promotion.

```text
Local Development
        |
        v
GitHub
        |
        v
Azure DevOps Pipeline
        |
        v
Build / Validate
        |
        v
Automated Tests
        |
        v
DEV
        |
        v
TEST
        |
        v
Manual Approval
        |
        v
PROD
```

Planned Azure DevOps environments:

```text
MAQ-Delivery-Dev
MAQ-Delivery-Test
MAQ-Delivery-Prod
```

Production promotion should require an Azure DevOps approval check.

---

## Responsible AI Principles

The solution is designed around:

- grounded enterprise evidence
- deterministic calculations for critical delivery classifications
- least-privilege access
- PII protection
- output secret filtering
- source attribution
- explicit domain separation
- human review for production decisions
- no unsupported cross-domain causal claims

---

## Current Status

Implemented:

- Three-agent MAF architecture
- Conditional and parallel routing
- Azure DevOps MCP
- SharePoint evidence
- Dataverse evidence
- Hybrid RAG
- Evidence validation
- Role-based authorization
- PII masking
- Prompt-injection protection
- Output secret redaction
- Copilot Studio integration

Next ALM activities:

- automated pytest suite
- Azure DevOps YAML pipeline
- Dev / Test / Prod environments
- Production approval gate
- observability and monitoring
- STRIDE threat model
- final architecture and demo documentation

---

## Dependency Baseline

The working local environment currently uses major dependencies including:

```text
agent-framework==1.14.0
fastapi==0.138.0
uvicorn==0.52.3
httpx==0.28.1
pydantic==2.13.4
fastmcp==3.4.7
openpyxl==3.1.5
msal==1.37.0
presidio-analyzer==2.2.364
presidio-anonymizer==2.2.364
chromadb==1.5.9
sentence-transformers==5.7.0
llama-index==0.14.23
llama-index-retrievers-bm25==0.7.1
llama-index-vector-stores-chroma==0.5.5
llama-index-embeddings-huggingface==0.7.0
```

Pin the complete dependency set in `requirements.txt` before running the Azure DevOps CI/CD pipeline.

---

## Disclaimer

This repository is an implementation and capstone reference for an intelligent client-delivery workflow. Production deployment should use organization-approved identity, secret-management, monitoring, network, and governance controls.

## Security and STRIDE Threat Model

| STRIDE | Threat | Example | Mitigation |
|---|---|---|---|
| Spoofing | User impersonation | Sending another user's ID | Role-based authorization; Entra ID recommended for production |
| Tampering | Prompt or payload manipulation | "Ignore previous instructions" | Prompt-injection guard and deterministic routing |
| Repudiation | Lack of request traceability | User denies making a request | Correlation IDs, user logging, timestamps |
| Information Disclosure | PII or secret leakage | Email, phone, API key in response | Presidio masking and output secret redaction |
| Denial of Service | Excessive agent/tool calls | Repeated MCP invocation | Single-use MCP tool controls and bounded retries |
| Elevation of Privilege | Access beyond user role | Engineering user requests portfolio data | Authorization before agent/tool execution |

## Responsible AI

The solution follows the following Responsible AI principles:

- **Fairness:** access decisions are deterministic and role-based rather than model-driven.
- **Reliability and Safety:** sprint health is calculated deterministically from Azure DevOps evidence and cannot be overridden by the LLM.
- **Privacy and Security:** PII is masked before agent execution and secret-like output is redacted before returning a response.
- **Transparency:** responses track the enterprise sources used.
- **Accountability:** Azure DevOps ALM stages and production approval checks provide governance and traceability.
- **Human Oversight:** agent recommendations support delivery decisions but do not replace management review.

## Observability

The solution includes lightweight observability to support troubleshooting, performance analysis, and auditability.

Current logging captures:

- request start and completion
- routing decisions
- authorization results
- prompt-security decisions
- agent execution status
- source usage
- MCP tool usage
- evidence validation status
- final workflow success/failure

Recommended production enhancements:

- correlation ID for every request
- request duration measurement
- structured JSON logging
- centralized telemetry with Azure Application Insights
- distributed tracing across FastAPI, agents, MCP, and external data sources
- alerts for failures, high latency, repeated tool calls, and authorization denials

### Suggested Request Trace

```text
Correlation ID
     ↓
FastAPI request
     ↓
Security checks
     ↓
Routing decision
     ↓
Portfolio / Engineering agent
     ↓
Enterprise data sources
     ↓
Analyst agent
     ↓
Final response


For the presentation, you can summarize it as:

> “The solution logs routing, authorization, tool usage, evidence status, and workflow completion. In production, these logs would be centralized in Azure Application Insights with correlation IDs and latency/error monitoring.”

For speed, I would **not add more observability code now** unless your capstone specifically requires a working correlation ID implementation.

Next we should do the **final architecture diagram**, because that will be used both in the README and the PPT.