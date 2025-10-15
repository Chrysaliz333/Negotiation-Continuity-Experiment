from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from analytics.kpi_queries import build_queries, describe_queries

console = Console()
app = typer.Typer(help="Execute or preview KPI queries against Graphiti")


def default_since() -> str:
    return datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()


@app.command()
def main(
    output: Path = typer.Option(
        Path("data/metrics/graphiti_baseline.jsonl"),
        help="Metrics output file (JSONL).",
    ),
    canonical_clause_id: Optional[str] = typer.Option(
        None,
        help="Canonical clause to inspect for lineage queries.",
    ),
    session_id: Optional[str] = typer.Option(
        None,
        help="Review session identifier for handover snapshot.",
    ),
    since: str = typer.Option(
        default_since,
        help="ISO timestamp boundary for concession queries.",
    ),
    dry_run: bool = typer.Option(
        True,
        help="Preview queries instead of executing against Graphiti.",
    ),
) -> None:
    """Preview KPI queries and emit placeholder metrics."""
    load_dotenv()

    params: Dict[str, str] = {}
    if canonical_clause_id:
        params["canonical_clause_id"] = canonical_clause_id
    if session_id:
        params["session_id"] = session_id
    params["since"] = since

    queries = build_queries(params)
    metadata = describe_queries(queries)

    table = Table(title="KPI Queries")
    table.add_column("Name")
    table.add_column("Parameters")
    for item in metadata:
        param_display = ", ".join(
            f"{key}={value}" for key, value in item["parameters"].items()
        ) or "<none>"
        table.add_row(item["name"], param_display)
    console.print(table)

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for item in metadata:
            record = {
                "query": item["name"],
                "parameters": item["parameters"],
                "status": "pending" if not dry_run else "skipped",
                "description": item["description"],
            }
            handle.write(json.dumps(record) + "\n")

    if dry_run:
        console.log("Dry-run complete; metrics file contains placeholders.")
        return

    raise NotImplementedError("Graphiti execution wiring will be added once connectivity is ready.")


if __name__ == "__main__":
    app()
