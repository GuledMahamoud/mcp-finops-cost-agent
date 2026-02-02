# MCP FinOps Cost Tools (CSV-Based)

A minimal **Model Context Protocol (MCP)** server that exposes **deterministic FinOps cost analysis tools** over a standardized interface.

This project demonstrates how FinOps analysis can be safely exposed to AI systems using **auditable, reproducible tools** rather than ad-hoc prompts or dashboards.

---

## Why this project exists

Traditional FinOps workflows rely on:
- dashboards (Cost Explorer, Power BI, Looker),
- static reports,
- manual variance analysis.

This project shows a different approach:

> **FinOps as callable, governed tools that an AI assistant can use to explain cloud spend.**

The AI does not “guess” costs — it calls deterministic tools via MCP and explains the results.

---

## What this demonstrates (FinOps mapping)

| FinOps capability | Demonstrated by |
|------------------|----------------|
| Cost reporting | `cost_summary` |
| Cost allocation | account + tag breakdowns |
| Allocation maturity | tag coverage metrics |
| Variance analysis | `cost_diff` |
| Cost monitoring | `anomaly_check` |
| Accountability | explicit filters + attribution |

This aligns with core FinOps domains defined by the FinOps Foundation:
**Inform → Optimize → Operate**.

---

## Architecture overview
Cloud Billing Export (CSV) ---> Billing Loader & Normalizer ---> Deterministic FinOps Tool Layer ---> MCP Server (FastMCP) ---> AI Assistant (explains results, does not compute)


Key principle: **tools compute, the model narrates**.

---

## Tools exposed via MCP

### 1. `cost_summary`
Summarizes cloud spend for a period.

**Returns:**
- total cost
- top services
- top accounts
- top environment/team tags
- tag coverage (% of spend allocated)

**FinOps relevance:** cost visibility + allocation maturity.

---

### 2. `cost_diff`
Explains *what changed* between two time periods.

**Compare by:**
- service
- account
- environment tag
- team tag

**FinOps relevance:** variance analysis and driver identification.

---

### 3. `anomaly_check`
Detects daily spend anomalies using a rolling z-score.

**Returns:**
- flagged dates
- spend on anomaly day
- top contributing services and accounts

**FinOps relevance:** operational monitoring and early detection.

---

## Example demo questions (interview-ready)

- “What were our top cost drivers last week?”
- “Why did cloud spend increase compared to the previous period?”
- “Were there any abnormal spend spikes, and what caused them?”
- “How good is our tag coverage for team-level accountability?”

Each question results in **explicit MCP tool calls**, not free-form reasoning.

---

## Data source

The project uses a **CSV-based cloud billing export** for simplicity and portability.

Expected normalized columns:
- `date`
- `provider`
- `account`
- `service`
- `cost`
- `currency`
- `tag_env`
- `tag_team`

A small sample dataset is included so the project runs immediately.

The loader can be extended to map:
- AWS Cost & Usage Report (CUR)
- Azure Cost Management exports
- GCP Billing exports

---

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python server.py
