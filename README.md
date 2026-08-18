# FactoryPilot

> AI copilot for manufacturing operations that combines manufacturing knowledge with real-time inventory intelligence to help factories make faster, smarter operational decisions.

[Live Demo](https://factorypilot.dev) · [Demo Video](#) · [Repository](#)

---

## Overview

Manufacturing teams make operational decisions using information scattered across inventory records, material availability, supplier data, product requirements, and manufacturing knowledge.

FactoryPilot brings this information together through an AI-powered copilot that can reason over operational data, retrieve manufacturing knowledge, and use specialized tools to perform real work.

Instead of simply answering questions, FactoryPilot can investigate operational situations, identify relevant information, and provide actionable insights through an agentic workflow.

---

## The Problem

Manufacturing operations often require answering questions such as:

- Which materials are currently running low?
- Which suppliers can provide the materials we need?
- Are we ready to manufacture a specific product?
- Which production risks should we be concerned about?
- What materials are impacting production?
- What should we purchase to maintain production readiness?

Answering these questions manually can require switching between multiple systems, checking inventory records, reviewing product-material relationships, and consulting manufacturing documentation.

This creates unnecessary operational overhead and slows down decision-making.

---

## The Solution

**FactoryPilot acts as an AI operational copilot for manufacturing teams.**

It combines:

- Real-time operational data
- Manufacturing knowledge
- Retrieval-Augmented Generation (RAG)
- Specialized AI tools
- Agentic reasoning
- Streaming responses and structured UI events

The user can ask a natural-language question and FactoryPilot determines what information or tools are required to answer it.

For example:

> "Which materials are currently at risk of affecting production, and what should we purchase?"

The agent can:

1. Analyze the request.
2. Select the relevant tools.
3. Retrieve inventory information.
4. Retrieve manufacturing knowledge when necessary.
5. Combine the results.
6. Generate an operational recommendation.
7. Stream the result back to the user through structured events.

---

## Key Features

### 🤖 Agentic AI Copilot

FactoryPilot uses an agentic workflow where the LLM can determine when it needs additional information or tools before producing an answer.

The agent can interact with specialized tools such as:

- Knowledge search
- Low-stock material analysis
- Supplier lookup
- Purchase plan generation
- Inventory trend analysis
- Production risk analysis

The goal is to move beyond static question answering and allow the AI to perform operational investigation.

---

### 📚 Manufacturing Knowledge with RAG

FactoryPilot can retrieve relevant manufacturing knowledge from an internal knowledge base.

The RAG pipeline transforms manufacturing documents into searchable vector representations and retrieves relevant context when the agent needs domain-specific knowledge.

This allows the AI to reason using both:

- Structured operational data
- Unstructured manufacturing knowledge

---

### 📦 Inventory Intelligence

FactoryPilot provides visibility into inventory conditions and material availability.

The system can identify:

- Low-stock materials
- Material availability risks
- Inventory trends
- Materials affecting production
- Supplier relationships

---

### 🏭 Production Risk Analysis

FactoryPilot can analyze whether material availability and inventory conditions could affect production readiness.

Instead of forcing users to manually correlate products, bills of materials, materials, and inventory, the system exposes these relationships through operational analysis.

---

### 🛒 Purchase Planning

FactoryPilot can generate purchase plans based on material requirements and inventory conditions.

The agent can use supplier and material information to help determine what should be replenished.

---

### ⚡ Streaming AI Experience

AI responses are streamed to the frontend using Server-Sent Events (SSE).

Instead of waiting for the entire response, the interface receives events as the agent progresses through its workflow.

This enables the UI to represent different stages of the AI interaction, including tool execution and structured operational results.

---

## Architecture

The following diagram shows the high-level architecture of FactoryPilot and how the frontend, backend, agent orchestration layer, tools, data stores, and external AI services interact.

<img width="7767" height="10946" alt="factorypilot-architecture" src="https://github.com/user-attachments/assets/446d49d7-f79a-4984-a133-ed7dc2e9d604" />

# Agent Workflow

The core of FactoryPilot is an agentic loop that allows the LLM to dynamically decide when it needs additional information before completing a request.

<img width="4848" height="11682" alt="fp-agent-workflow" src="https://github.com/user-attachments/assets/1082d18b-555c-4b58-bfef-83125c251e1a" />

# How It Works

For example, consider the request:

> "Which materials are at risk of affecting production?"

FactoryPilot can autonomously investigate the request by combining multiple sources of operational information.

The agent may:

1. **Identify low-stock materials** based on current inventory levels.
2. **Retrieve supplier information** for the affected materials.
3. **Analyze product-material dependencies** to determine which products rely on those materials.
4. **Assess production impact** based on material availability and product requirements.
5. **Combine the results** into a single operational analysis.
6. **Present the most relevant findings and recommendations** to the user.

The agent determines which tools are required during the interaction rather than following a fixed sequence for every request.

## Tech Stack

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- Zustand
- TanStack Query

### Backend

- Python
- FastAPI
- SQLModel
- SQLAlchemy
- PostgreSQL
- pgvector

### AI

- OpenAI
- Tool Calling
- Retrieval-Augmented Generation (RAG)
- Streaming Responses
- Structured AI Events

### Infrastructure

- Docker
- Docker Compose
- Supabase PostgreSQL
- Vercel
- Render

---

## Running Locally

### Prerequisites

Make sure you have the following installed:

- Docker
- Node.js
- pnpm

The backend is containerized and includes its own `Dockerfile` and `docker-compose.yml`.

Docker Compose automatically builds the backend and starts the local PostgreSQL database.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd factorypilot
```

### 2. Configure Environment Variables

Before starting the application, configure the required environment variables.

#### Backend

Create:

```text
backend/.env
```

Example:

```env
DATABASE_URL=postgresql+asyncpg://factorypilot:factorypilot@localhost:5432/factorypilot_db

ENV=development

ALLOW_ORIGINS=["http://localhost:3000"]

# Not in use
GEMINI_API_KEY=anything
GEMINI_EMBEDDING_MODEL=anything
GEMINI_EMBEDDING_DIMENSION=anything
GEMINI_MODEL=anything

OPENAI_MODEL=
OPENAI_API_KEY=
OPENAI_EMBEDDING_MODEL=
```

The OpenAI variables should be configured with the credentials and model used by your deployment.

#### Frontend

Create:

```text
frontend/.env.local
```

Example:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

> Never commit API keys, passwords, database credentials, or other secrets to the repository.

### 3. Start the Backend

The backend uses Docker Compose to start the FastAPI application and its local PostgreSQL database.

From the backend directory:

```bash
cd backend
docker compose up --build
```

The backend will be available at:

```text
http://localhost:8000
```

When running in development mode, the FastAPI documentation is available at:

```text
http://localhost:8000/docs
```

### 4. Start the Frontend

Open a second terminal:

```bash
cd frontend
pnpm install
pnpm dev
```

The frontend will be available at:

```text
http://localhost:3000
```

### Local Development Architecture

```text
┌──────────────────────┐
│   Next.js Frontend   │
│   localhost:3000     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   FastAPI Backend    │
│   localhost:8000     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ PostgreSQL Database   │
│    Docker Compose     │
└──────────────────────┘
```

---

## Environment Variables

FactoryPilot requires environment variables for the backend, AI services, database connection, and frontend-backend communication.

### Backend

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL database connection string |
| `ENV` | Application environment |
| `ALLOW_ORIGINS` | Allowed frontend origins |
| `OPENAI_API_KEY` | API key used to access the OpenAI API |
| `OPENAI_MODEL` | OpenAI model used by the application |
| `OPENAI_EMBEDDING_MODEL` | OpenAI embedding model used by the application |
| `GEMINI_API_KEY` | Gemini API key (currently not in use) |
| `GEMINI_EMBEDDING_MODEL` | Gemini embedding model (currently not in use) |
| `GEMINI_EMBEDDING_DIMENSION` | Gemini embedding dimension (currently not in use) |
| `GEMINI_MODEL` | Gemini model (currently not in use) |

Example:

```env
DATABASE_URL=postgresql+asyncpg://factorypilot:factorypilot@localhost:5432/factorypilot_db

ENV=development

ALLOW_ORIGINS=["http://localhost:3000"]

# Not in use
GEMINI_API_KEY=anything
GEMINI_EMBEDDING_MODEL=anything
GEMINI_EMBEDDING_DIMENSION=anything
GEMINI_MODEL=anything

OPENAI_MODEL=
OPENAI_API_KEY=
OPENAI_EMBEDDING_MODEL=
```

### Frontend

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | URL of the FastAPI backend |

For local development:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, this should point to the deployed FastAPI backend.

> Never commit `.env`, `.env.local`, API keys, database credentials, or other secrets to source control.

---

## Deployment

FactoryPilot is deployed as a production web application.

```text
                         ┌─────────────────┐
                         │     Vercel      │
                         │  Next.js App    │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │     Render      │
                         │ FastAPI Backend │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    Supabase     │
                         │   PostgreSQL    │
                         │    + pgvector   │
                         └─────────────────┘
```

### Live Demo

[factorypilot.dev](https://factorypilot.dev)

---

## Why FactoryPilot?

Manufacturing teams often need to make operational decisions using information distributed across inventory, materials, suppliers, products, and manufacturing knowledge.

The challenge is not simply having access to this information. The real challenge is connecting it quickly and turning it into actionable insight.

FactoryPilot is built around a simple idea:

> **Manufacturing teams should spend less time searching for operational information and more time making decisions.**

Instead of manually navigating multiple systems and correlating information themselves, users can ask FactoryPilot an operational question and let the agent investigate it using real operational data, specialized tools, and manufacturing knowledge.

The goal is not to replace the people making operational decisions.

**The goal is to give them an intelligent operational partner that handles the investigation and information gathering around those decisions.**

---

## Future Improvements

FactoryPilot provides a foundation for expanding AI-assisted manufacturing operations.

Potential future improvements include:

- **Advanced inventory forecasting** using historical demand and consumption patterns.
- **Automated replenishment workflows** with human approval before purchase execution.
- **Production scheduling intelligence** based on material availability and production constraints.
- **Deeper supplier intelligence** including lead times, reliability, and purchasing history.
- **Expanded production risk analysis** across multiple products and manufacturing stages.
- **Advanced inventory trend analysis** for identifying emerging shortages.
- **Additional agent tools** for purchasing, production planning, and supplier management.
- **Human-in-the-loop workflows** for approving high-impact operational actions.
- **Expanded manufacturing knowledge bases** covering additional manufacturing processes and operational scenarios.
- **Continuous operational monitoring** that proactively alerts teams when an issue requires attention.
