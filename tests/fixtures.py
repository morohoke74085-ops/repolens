from __future__ import annotations

from repolens.models import ProjectAnalysis, RepoFile, RepoMetadata, RepoRef


def sample_analysis() -> ProjectAnalysis:
    return ProjectAnalysis(
        repo_ref=RepoRef(owner="acme", name="sample", url="https://github.com/acme/sample"),
        metadata=RepoMetadata(
            full_name="acme/sample",
            description="Sample repository",
            default_branch="main",
            stars=42,
            open_issues=3,
            primary_language="Python",
            license_name="MIT",
            topics=["cli", "developer-tools"],
        ),
        summary="acme/sample looks like a Python repository managed with pip, with pytest detected.",
        readme_excerpt="Sample README excerpt",
        root_files=["README.md", "pyproject.toml", "LICENSE"],
        manifest_files=["pyproject.toml"],
        languages=["Python"],
        package_managers=["pip"],
        test_frameworks=["pytest"],
        ci_providers=["GitHub Actions"],
        key_directories=["repolens", "tests", "docs"],
        entry_points=[
            "Read `README.md` first for setup context and repository intent.",
            "Inspect `repolens/` to understand the main project layout.",
        ],
        install_steps=[
            "Run `python -m pip install -e .` for an editable local install.",
        ],
        run_steps=[
            "Run `python -m <package>` after replacing `<package>` with the main Python package name.",
        ],
        test_steps=["Run `pytest` for the primary test suite."],
        contribution_entry_points=["Improve onboarding docs, examples, and setup clarity."],
        docs_gaps=["No dedicated `docs/` directory detected."],
        tooling_gaps=[],
    )


class FakeGitHubClient:
    def __init__(self) -> None:
        self.repo_ref = RepoRef(owner="acme", name="sample", url="https://github.com/acme/sample")
        self.metadata = RepoMetadata(
            full_name="acme/sample",
            description="Sample repository",
            default_branch="main",
            stars=42,
            open_issues=3,
            primary_language="Python",
            license_name="MIT",
            topics=["cli"],
        )
        self.tree = [
            RepoFile(path="README.md", type="blob"),
            RepoFile(path="pyproject.toml", type="blob"),
            RepoFile(path=".github/workflows/ci.yml", type="blob"),
            RepoFile(path="repolens/__init__.py", type="blob"),
            RepoFile(path="repolens/cli.py", type="blob"),
            RepoFile(path="tests/test_cli.py", type="blob"),
            RepoFile(path="docs/index.md", type="blob"),
            RepoFile(path="repolens", type="tree"),
            RepoFile(path="tests", type="tree"),
            RepoFile(path="docs", type="tree"),
        ]
        self.manifests = {
            "pyproject.toml": """
[project]
name = "sample"

[project.optional-dependencies]
test = ["pytest>=8.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
""".strip()
        }
        self.readme = "# Sample\n\nUse pytest to run tests."

    def get_repo_ref(self, repo_url: str) -> RepoRef:
        return self.repo_ref

    def get_repo_metadata(self, repo: RepoRef) -> RepoMetadata:
        return self.metadata

    def get_tree(self, repo: RepoRef, branch: str) -> list[RepoFile]:
        return self.tree

    def get_readme(self, repo: RepoRef) -> str:
        return self.readme

    def get_file_content(self, repo: RepoRef, path: str, branch: str | None = None) -> str | None:
        return self.manifests.get(path)

