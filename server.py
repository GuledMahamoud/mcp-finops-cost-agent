from __future__ import annotations

from fastmcp import FastMCP

from billing_loader import BillingLoader
from finops_tools import FinOpsTools

mcp = FastMCP(name="FinOps Cost Tools (CSV)")

TOOLS = FinOpsTools(loader=BillingLoader(csv_path="data/sample_billing.csv"))


@mcp.tool
def cost_summary(
    start_date: str,
    end_date: str,
    top_n: int = 5,
    provider: str | None = None,
    account: str | None = None,
    service: str | None = None,
    tag_env: str | None = None,
    tag_team: str | None = None,
):
    """Summarize cloud spend for a period (total + top drivers + tag coverage)."""
    return TOOLS.cost_summary(
        start_date=start_date,
        end_date=end_date,
        top_n=top_n,
        provider=provider,
        account=account,
        service=service,
        tag_env=tag_env,
        tag_team=tag_team,
    )


@mcp.tool
def cost_diff(
    period_a_start: str,
    period_a_end: str,
    period_b_start: str,
    period_b_end: str,
    dimension: str = "service",
    top_n: int = 7,
    provider: str | None = None,
    account: str | None = None,
    tag_env: str | None = None,
    tag_team: str | None = None,
):
    """Compare spend between two periods ("what changed?") by service/account/tag."""
    return TOOLS.cost_diff(
        period_a_start=period_a_start,
        period_a_end=period_a_end,
        period_b_start=period_b_start,
        period_b_end=period_b_end,
        dimension=dimension,
        top_n=top_n,
        provider=provider,
        account=account,
        tag_env=tag_env,
        tag_team=tag_team,
    )


@mcp.tool
def anomaly_check(
    start_date: str,
    end_date: str,
    window_days: int = 7,
    z_threshold: float = 2.5,
    top_n_drivers: int = 3,
    provider: str | None = None,
    account: str | None = None,
    tag_env: str | None = None,
    tag_team: str | None = None,
):
    """Detect daily spend anomalies and attribute likely service/account drivers."""
    return TOOLS.anomaly_check(
        start_date=start_date,
        end_date=end_date,
        window_days=window_days,
        z_threshold=z_threshold,
        top_n_drivers=top_n_drivers,
        provider=provider,
        account=account,
        tag_env=tag_env,
        tag_team=tag_team,
    )


if __name__ == "__main__":
    # FastMCP defaults to stdio transport for MCP hosts.
    mcp.run()