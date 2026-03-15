from __future__ import annotations

from repolens.generators.contribute import build_contributor_report
from repolens.generators.guide import build_onboarding_guide
from repolens.models import ProjectAnalysis


def build_markdown_report(analysis: ProjectAnalysis) -> str:
    metadata_lines = [
        f"- Repository: `{analysis.metadata.full_name}`",
        f"- Stars: `{analysis.metadata.stars}`",
        f"- Open issues: `{analysis.metadata.open_issues}`",
        f"- Default branch: `{analysis.metadata.default_branch}`",
        f"- License: `{analysis.metadata.license_name or 'Unknown'}`",
    ]

    sections = [
        f"# RepoLens report for {analysis.metadata.full_name}",
        "",
        analysis.summary,
        "",
        "## Snapshot",
        *metadata_lines,
        "",
        "## Stack signals",
        f"- Languages: {', '.join(analysis.languages) or 'Not detected'}",
        f"- Package managers: {', '.join(analysis.package_managers) or 'Not detected'}",
        f"- Test frameworks: {', '.join(analysis.test_frameworks) or 'Not detected'}",
        f"- CI providers: {', '.join(analysis.ci_providers) or 'Not detected'}",
        "",
        "## Root files",
        *(f"- `{path}`" for path in analysis.root_files[:15]),
        "",
        build_onboarding_guide(analysis),
        "",
        build_contributor_report(analysis),
    ]
    return "\n".join(sections).strip()

