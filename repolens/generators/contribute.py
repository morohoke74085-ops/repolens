from __future__ import annotations

from repolens.models import ProjectAnalysis


def build_contributor_report(analysis: ProjectAnalysis) -> str:
    lines = [
        f"# Contribution entry points for {analysis.metadata.full_name}",
        "",
        "## Good first areas",
        *(f"- {item}" for item in _or_placeholder(analysis.contribution_entry_points, "Start with small documentation or test improvements.")),
        "",
        "## Documentation gaps",
        *(f"- {item}" for item in _or_placeholder(analysis.docs_gaps, "No major documentation gaps were detected from the repository tree alone.")),
        "",
        "## Tooling gaps",
        *(f"- {item}" for item in _or_placeholder(analysis.tooling_gaps, "No major tooling gaps were detected from the repository tree alone.")),
    ]
    return "\n".join(lines).strip()


def _or_placeholder(items: list[str], placeholder: str) -> list[str]:
    return items if items else [placeholder]

