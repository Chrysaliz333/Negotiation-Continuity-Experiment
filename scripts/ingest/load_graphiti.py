from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from models import (
    AgentRecommendation,
    Clause,
    DocVersion,
    Document,
    UserDecision,
)

console = Console()
app = typer.Typer(help="Load negotiation continuity artifacts into Graphiti")


@dataclass
class GraphitiConfig:
    host: str
    port: int
    api_key: Optional[str]

    @classmethod
    def from_env(cls) -> "GraphitiConfig":
        host = os.getenv("FALKORDB_HOST", "localhost")
        port = int(os.getenv("FALKORDB_PORT", "6379"))
        api_key = os.getenv("GRAPHITI_API_KEY")
        return cls(host=host, port=port, api_key=api_key)


def iter_matter_dirs(root: Path, matter: Optional[str]) -> Iterator[Path]:
    if matter:
        candidate = root / matter
        if not candidate.exists():
            raise typer.BadParameter(f"Matter '{matter}' not found under {root}")
        yield candidate
        return

    for path in sorted(p for p in root.iterdir() if p.is_dir()):
        yield path


def load_json_payloads(matter_dir: Path) -> list[dict]:
    payloads: list[dict] = []
    for path in sorted(matter_dir.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            payloads.append(json.load(handle))
    return payloads


def summarize_payloads(payloads: Iterable[dict]) -> dict[str, int]:
    summary: dict[str, int] = {
        "documents": 0,
        "versions": 0,
        "clauses": 0,
        "recommendations": 0,
        "decisions": 0,
    }
    for blob in payloads:
        if "documents" in blob:
            summary["documents"] += len(blob["documents"])
        if "versions" in blob:
            summary["versions"] += len(blob["versions"])
        if "clauses" in blob:
            summary["clauses"] += len(blob["clauses"])
        if "recommendations" in blob:
            summary["recommendations"] += len(blob["recommendations"])
        if "decisions" in blob:
            summary["decisions"] += len(blob["decisions"])
    return summary


def validate_payloads(payloads: Iterable[dict]) -> None:
    for blob in payloads:
        for raw in blob.get("documents", []):
            Document.model_validate(raw)
        for raw in blob.get("versions", []):
            DocVersion.model_validate(raw)
        for raw in blob.get("clauses", []):
            Clause.model_validate(raw)
        for raw in blob.get("recommendations", []):
            AgentRecommendation.model_validate(raw)
        for raw in blob.get("decisions", []):
            UserDecision.model_validate(raw)


def render_summary_table(matter_id: str, summary: dict[str, int]) -> None:
    table = Table(title=f"Matter {matter_id}")
    table.add_column("Entity")
    table.add_column("Count", justify="right")
    for key, value in summary.items():
        table.add_row(key, str(value))
    console.print(table)


def ingest_payloads(payloads: Iterable[dict], config: GraphitiConfig, dry_run: bool) -> None:
    if dry_run:
        return
    raise NotImplementedError(
        "Graphiti ingestion wiring is pending dataset availability."
    )


@app.command()
def main(
    input_dir: Path = typer.Argument(
        Path("data/ground_truth"),
        exists=True,
        file_okay=False,
        resolve_path=True,
        help="Root directory containing matter JSON bundles.",
    ),
    matter: Optional[str] = typer.Option(
        None,
        help="Only ingest a specific matter directory (folder name).",
    ),
    dry_run: bool = typer.Option(
        True,
        help="Validate and summarize without writing to Graphiti.",
    ),
) -> None:
    """Validate and ingest matter payloads into Graphiti."""
    load_dotenv()
    config = GraphitiConfig.from_env()
    console.log(
        f"Starting ingestion (dry_run={dry_run}) against {config.host}:{config.port}"
    )

    for matter_dir in iter_matter_dirs(input_dir, matter):
        payloads = load_json_payloads(matter_dir)
        validate_payloads(payloads)
        summary = summarize_payloads(payloads)
        render_summary_table(matter_dir.name, summary)
        ingest_payloads(payloads, config, dry_run=dry_run)

    console.log("Ingestion run complete")


if __name__ == "__main__":
    app()
