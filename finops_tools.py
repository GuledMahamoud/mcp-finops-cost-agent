from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from dateutil.parser import isoparse

from billing_loader import BillingLoader


def _parse_date(d: str) -> date:
    # Accepts "YYYY-MM-DD" (and many ISO formats)
    return isoparse(d).date()


def _filter_df(
    df: pd.DataFrame,
    start_date: date,
    end_date: date,
    provider: Optional[str] = None,
    account: Optional[str] = None,
    service: Optional[str] = None,
    tag_env: Optional[str] = None,
    tag_team: Optional[str] = None,
) -> pd.DataFrame:
    mask = (df["date"] >= start_date) & (df["date"] <= end_date)

    if provider:
        mask &= df["provider"].astype(str) == provider
    if account:
        mask &= df["account"].astype(str) == account
    if service:
        mask &= df["service"].astype(str) == service
    if tag_env:
        mask &= df["tag_env"].astype(str) == tag_env
    if tag_team:
        mask &= df["tag_team"].astype(str) == tag_team

    return df.loc[mask].copy()


def _top_n(series: pd.Series, n: int) -> List[Dict[str, Any]]:
    s = series.sort_values(ascending=False).head(n)
    return [{"name": str(k), "cost": float(v)} for k, v in s.items()]


def _tag_coverage(df: pd.DataFrame) -> Dict[str, Any]:
    total = float(df["cost"].sum()) if len(df) else 0.0

    def coverage_for(col: str) -> Dict[str, Any]:
        if total == 0.0:
            return {"by_cost_pct": 0.0, "missing_cost": 0.0}

        missing_mask = df[col].isna()
        missing_cost = float(df.loc[missing_mask, "cost"].sum())
        covered_cost = total - missing_cost
        return {
            "by_cost_pct": round((covered_cost / total) * 100.0, 2),
            "missing_cost": round(missing_cost, 2),
        }

    return {
        "total_cost": round(total, 2),
        "tag_env": coverage_for("tag_env"),
        "tag_team": coverage_for("tag_team"),
    }


@dataclass
class FinOpsTools:
    loader: BillingLoader

    def cost_summary(
        self,
        start_date: str,
        end_date: str,
        top_n: int = 5,
        provider: Optional[str] = None,
        account: Optional[str] = None,
        service: Optional[str] = None,
        tag_env: Optional[str] = None,
        tag_team: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        FinOps: Inform / Allocate.
        Returns total cost and top drivers by service, account, and tags (+ tag coverage).
        """
        data = self.loader.load().df
        s = _parse_date(start_date)
        e = _parse_date(end_date)

        f = _filter_df(
            data, s, e,
            provider=provider, account=account, service=service,
            tag_env=tag_env, tag_team=tag_team,
        )

        total = float(f["cost"].sum()) if len(f) else 0.0

        by_service = f.groupby("service")["cost"].sum() if len(f) else pd.Series(dtype=float)
        by_account = f.groupby("account")["cost"].sum() if len(f) else pd.Series(dtype=float)
        by_env = f.groupby("tag_env")["cost"].sum() if len(f) else pd.Series(dtype=float)
        by_team = f.groupby("tag_team")["cost"].sum() if len(f) else pd.Series(dtype=float)

        return {
            "period": {"start_date": str(s), "end_date": str(e)},
            "filters": {
                "provider": provider, "account": account, "service": service,
                "tag_env": tag_env, "tag_team": tag_team,
            },
            "total_cost": round(total, 2),
            "currency": (f["currency"].iloc[0] if len(f) else "UNKNOWN"),
            "top_services": _top_n(by_service, top_n),
            "top_accounts": _top_n(by_account, top_n),
            "top_tag_env": _top_n(by_env, top_n),
            "top_tag_team": _top_n(by_team, top_n),
            "tag_coverage": _tag_coverage(f),
            "rows": int(len(f)),
        }

    def cost_diff(
        self,
        period_a_start: str,
        period_a_end: str,
        period_b_start: str,
        period_b_end: str,
        dimension: str = "service",
        top_n: int = 7,
        provider: Optional[str] = None,
        account: Optional[str] = None,
        tag_env: Optional[str] = None,
        tag_team: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        FinOps: Variance analysis ("what changed?").
        Compares two periods across a single dimension: service | account | tag_env | tag_team.
        """
        valid_dims = {"service", "account", "tag_env", "tag_team"}
        if dimension not in valid_dims:
            raise ValueError(f"dimension must be one of {sorted(valid_dims)}")

        data = self.loader.load().df
        a_s, a_e = _parse_date(period_a_start), _parse_date(period_a_end)
        b_s, b_e = _parse_date(period_b_start), _parse_date(period_b_end)

        A = _filter_df(data, a_s, a_e, provider=provider, account=account, tag_env=tag_env, tag_team=tag_team)
        B = _filter_df(data, b_s, b_e, provider=provider, account=account, tag_env=tag_env, tag_team=tag_team)

        A_grp = A.groupby(dimension)["cost"].sum()
        B_grp = B.groupby(dimension)["cost"].sum()

        # Align indexes
        idx = A_grp.index.union(B_grp.index)
        A_al = A_grp.reindex(idx, fill_value=0.0)
        B_al = B_grp.reindex(idx, fill_value=0.0)

        delta = (A_al - B_al).sort_values(ascending=False)

        # Top movers by absolute delta
        top_increase = delta.head(top_n)
        top_decrease = delta.tail(top_n).sort_values()

        return {
            "dimension": dimension,
            "period_a": {"start_date": str(a_s), "end_date": str(a_e), "total_cost": round(float(A["cost"].sum()), 2)},
            "period_b": {"start_date": str(b_s), "end_date": str(b_e), "total_cost": round(float(B["cost"].sum()), 2)},
            "filters": {"provider": provider, "account": account, "tag_env": tag_env, "tag_team": tag_team},
            "top_increases": [{"name": str(k), "delta_cost": round(float(v), 2)} for k, v in top_increase.items()],
            "top_decreases": [{"name": str(k), "delta_cost": round(float(v), 2)} for k, v in top_decrease.items()],
        }

    def anomaly_check(
        self,
        start_date: str,
        end_date: str,
        window_days: int = 7,
        z_threshold: float = 2.5,
        top_n_drivers: int = 3,
        provider: Optional[str] = None,
        account: Optional[str] = None,
        tag_env: Optional[str] = None,
        tag_team: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        FinOps: Operate / Monitor.
        Very simple anomaly detector on daily total spend:
          z = (x - rolling_mean) / rolling_std
        Flags days where z >= threshold and attributes likely drivers (service/account).
        """
        data = self.loader.load().df
        s, e = _parse_date(start_date), _parse_date(end_date)

        f = _filter_df(data, s, e, provider=provider, account=account, tag_env=tag_env, tag_team=tag_team)

        if len(f) == 0:
            return {"period": {"start_date": str(s), "end_date": str(e)}, "anomalies": [], "note": "No data in range."}

        daily = f.groupby("date")["cost"].sum().sort_index()
        daily = daily.asfreq("D", fill_value=0.0)

        roll_mean = daily.rolling(window=window_days, min_periods=max(2, window_days // 2)).mean()
        roll_std = daily.rolling(window=window_days, min_periods=max(2, window_days // 2)).std(ddof=0)

        z = (daily - roll_mean) / roll_std.replace({0.0: pd.NA})
        z = z.fillna(0.0)

        flagged = z[z >= z_threshold]

        anomalies: List[Dict[str, Any]] = []
        for day, zscore in flagged.items():
            day_cost = float(daily.loc[day])

            # Attribute drivers: compare that day’s service/account against its own average
            day_rows = f[f["date"] == day.date()].copy()

            svc = day_rows.groupby("service")["cost"].sum().sort_values(ascending=False)
            acc = day_rows.groupby("account")["cost"].sum().sort_values(ascending=False)

            anomalies.append({
                "date": str(day.date()),
                "day_cost": round(day_cost, 2),
                "z_score": round(float(zscore), 2),
                "top_service_drivers": _top_n(svc, top_n_drivers),
                "top_account_drivers": _top_n(acc, top_n_drivers),
            })

        return {
            "period": {"start_date": str(s), "end_date": str(e)},
            "params": {"window_days": window_days, "z_threshold": z_threshold, "top_n_drivers": top_n_drivers},
            "filters": {"provider": provider, "account": account, "tag_env": tag_env, "tag_team": tag_team},
            "daily_total_cost": [{"date": str(d), "cost": round(float(c), 2)} for d, c in daily.items()],
            "anomalies": anomalies,
        }