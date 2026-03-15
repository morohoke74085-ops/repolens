from __future__ import annotations

from pathlib import Path

import httpx
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from repolens.analyzer import RepoAnalyzer
from repolens.generators.contribute import build_contributor_report
from repolens.generators.guide import build_onboarding_guide
from repolens.generators.markdown_export import build_markdown_report
from repolens.models import ProjectAnalysis

app = typer.Typer(help="Understand public GitHub repositories faster.")
console = Console()


@app.command()
def scan(repo_url: str = typer.Argument(..., help="Public GitHub repository URL.")) -> None:
    """Analyze a repository and print a structured summary."""
    analysis = _analyze(repo_url)
    _print_scan_report(analysis)


@app.command()
def guide(repo_url: str = typer.Argument(..., help="Public GitHub repository URL.")) -> None:
    """Generate a short onboarding guide."""
    analysis = _analyze(repo_url)
    console.print(Markdown(build_onboarding_guide(analysis)))


@app.command()
def contribute(repo_url: str = typer.Argument(..., help="Public GitHub repository URL.")) -> None:
    """Generate contribution entry points and gaps."""
    analysis = _analyze(repo_url)
    console.print(Markdown(build_contributor_report(analysis)))


@app.command()
def export(
    repo_url: str = typer.Argument(..., help="Public GitHub repository URL."),
    format: str = typer.Option("markdown", "--format", help="Output format."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write to a file instead of stdout."),
) -> None:
    """Export a repository report."""
    analysis = _analyze(repo_url)
    if format.lower() != "markdown":
        raise typer.BadParameter("Only markdown export is supported in v0.1.")

    report = build_markdown_report(analysis)
    if output:
        output.write_text(report + "\n", encoding="utf-8")
        console.print(f"[green]Wrote report to {output}[/green]")
        return
    console.print(Markdown(report))


def main() -> None:
    app()


def _analyze(repo_url: str) -> ProjectAnalysis:
    analyzer = RepoAnalyzer()
    try:
        return analyzer.analyze(repo_url)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc
    except httpx.HTTPError as exc:
        console.print(f"[red]GitHub request failed: {exc}[/red]")
        raise typer.Exit(code=1) from exc


def _print_scan_report(analysis: ProjectAnalysis) -> None:
    console.print(Panel(analysis.summary, title=analysis.metadata.full_name))

    metadata_table = Table(show_header=False, box=None)
    metadata_table.add_row("Stars", str(analysis.metadata.stars))
    metadata_table.add_row("Open issues", str(analysis.metadata.open_issues))
    metadata_table.add_row("Default branch", analysis.metadata.default_branch)
    metadata_table.add_row("License", analysis.metadata.license_name or "Unknown")
    metadata_table.add_row("Languages", ", ".join(analysis.languages) or "Not detected")
    metadata_table.add_row("Package managers", ", ".join(analysis.package_managers) or "Not detected")
    metadata_table.add_row("Test frameworks", ", ".join(analysis.test_frameworks) or "Not detected")
    metadata_table.add_row("CI", ", ".join(analysis.ci_providers) or "Not detected")
    console.print(metadata_table)

    _print_list("Root files", [f"`{item}`" for item in analysis.root_files[:12]])
    _print_list("Key directories", [f"`{item}/`" for item in analysis.key_directories])
    _print_list("Run steps", analysis.run_steps)
    _print_list("Test steps", analysis.test_steps)
    _print_list("Contribution entry points", analysis.contribution_entry_points)


def _print_list(title: str, items: list[str]) -> None:
    console.print(f"\n[bold]{title}[/bold]")
    if not items:
        console.print("- Not detected")
        return
    for item in items:
        console.print(f"- {item}")

