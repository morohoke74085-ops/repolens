from __future__ import annotations

from repolens.models import ProjectAnalysis


def build_onboarding_guide(analysis: ProjectAnalysis) -> str:
    lines = [
        f"# 5-minute guide for {analysis.metadata.full_name}",
        "",
        analysis.summary,
        "",
        "## Install",
        *(f"- {step}" for step in _or_placeholder(analysis.install_steps, "Install steps were not confidently detected.")),
        "",
        "## Run",
        *(f"- {step}" for step in _or_placeholder(analysis.run_steps, "Run steps were not confidently detected.")),
        "",
        "## Test",
        *(f"- {step}" for step in _or_placeholder(analysis.test_steps, "Test steps were not confidently detected.")),
        "",
        "## Where to look first",
        *(f"- {item}" for item in _or_placeholder(analysis.entry_points, "Start with the README and root manifest files.")),
        "",
        "## Key directories",
        *(f"- {directory}" for directory in _or_placeholder(analysis.key_directories, "No obvious key directories were detected.")),
    ]
    return "\n".join(lines).strip()


def _or_placeholder(items: list[str], placeholder: str) -> list[str]:
    return items if items else [placeholder]

