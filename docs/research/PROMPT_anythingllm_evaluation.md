# Research Task: Evaluate AnythingLLM for Legislation Analysis

## Context

You are the Affordabot agent. Your primary use case is **legislation/bill analysis** - helping users understand, search, and analyze government bills, meeting transcripts, and regulatory documents.

A Railway template for **AnythingLLM** has been identified as a potential accelerant for your RAG capabilities. Your task is to investigate whether AnythingLLM is a good fit.

## Background on AnythingLLM

From the Railway deploy page (https://railway.com/deploy/HNSCS1):

> AnythingLLM is an all-in-one application for RAG, AI Agents, multi-user management & more.
>
> **Key Features:**
> - **Private RAG**: Chat with your documents with complete privacy
> - **AI Agents**: Build or use agents with no-code, supports MCP for tools
> - **Multi-User**: Workspace management and permissions
> - **Whitelabel**: Custom branding
>
> **Supported backends**: Multiple LLMs, embedding models, and vector databases

**Official docs**: https://docs.anythingllm.com/
**GitHub**: https://github.com/Mintplex-Labs/anything-llm

---

## Research Questions

### 1. Document Ingestion Fit

- [ ] **What document types can AnythingLLM ingest?** (PDF, DOCX, HTML, plain text?)
- [ ] **Can it handle large documents?** (Bill PDFs can be 100+ pages)
- [ ] **How does chunking work?** (configurable chunk size/overlap?)
- [ ] **Can you add metadata during ingestion?** (e.g., bill ID, session year, sponsor?)

### 2. Search & Retrieval Quality

- [ ] **What vector databases does it support?** (Check if pgvector is supported for consistency with Prime Radiant)
- [ ] **What embedding models are available?** (OpenAI, local models?)
- [ ] **Can you filter searches by metadata?** (e.g., "bills from 2024 session only")
- [ ] **How does hybrid search work?** (keyword + semantic?)

### 3. Agent Capabilities

- [ ] **Can agents call external APIs?** (e.g., your existing bill lookup endpoints)
- [ ] **MCP support**: What tools can be integrated via Model Context Protocol?
- [ ] **Can you build custom workflows?** (e.g., "summarize bill → extract sponsors → compare to similar bills")

### 4. Multi-User & Auth

- [ ] **How does authentication work?** (SSO, email/password, API keys?)
- [ ] **Can you create per-user or per-organization workspaces?**
- [ ] **Permission levels?** (admin, viewer, contributor?)

### 5. Deployment & Integration

- [ ] **Railway deployment**: Does the one-click template work? What services does it create?
- [ ] **API access**: Can you call AnythingLLM programmatically from your FastAPI backend?
- [ ] **Can you export/sync with your existing Railway Postgres?** (or does it use its own DB?)

### 6. Cost & Scaling

- [ ] **Resource requirements**: How much RAM/CPU does it need?
- [ ] **Embedding costs**: If using OpenAI embeddings, what's the per-document cost estimate for ~10K bills?
- [ ] **Storage**: Where does it store vectors? Can you use external pgvector?

---

## Evaluation Criteria

After researching, score each dimension (1-5):

| Dimension | Score | Notes |
|-----------|-------|-------|
| Document ingestion fit | /5 | |
| Search quality | /5 | |
| Agent capabilities | /5 | |
| Multi-user/auth | /5 | |
| Integration with existing infra | /5 | |
| Deployment simplicity | /5 | |
| **Total** | /30 | |

**Threshold**: If total ≥ 22, recommend proceeding with a pilot deployment.

---

## Recommended Actions

1. **Deploy the Railway template** in a dev environment
2. **Ingest 10-20 sample bills** (PDFs from your existing fixtures)
3. **Test retrieval** with queries like:
   - "Bills related to housing affordability in 2024"
   - "Who sponsored environmental legislation this session?"
   - "Compare AB-123 to previous versions"
4. **Report findings** with screenshots and API examples
5. **Recommend**: Proceed, explore further, or reject

---

## Resources

- AnythingLLM docs: https://docs.anythingllm.com/
- MCP tool integration: https://docs.anythingllm.com/mcp-compatibility/docker
- Agent flows: https://docs.anythingllm.com/agent-flows/overview
- Railway template: https://railway.com/deploy/HNSCS1

---

## Output Format

Create a document at `docs/research/anythingllm-evaluation.md` with:
1. Summary table (scores)
2. Detailed findings per section
3. Screenshots of UI/ingestion/search
4. Recommendation (proceed/explore/reject) with rationale
