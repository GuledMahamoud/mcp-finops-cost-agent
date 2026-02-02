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
