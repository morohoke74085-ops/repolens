from __future__ import annotations

from pydantic import BaseModel, Field


class RepoRef(BaseModel):
    owner: str
    name: str
    url: str

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"


class RepoMetadata(BaseModel):
    full_name: str
    description: str | None = None
    default_branch: str
    stars: int = 0
    open_issues: int = 0
    primary_language: str | None = None
    license_name: str | None = None
    topics: list[str] = Field(default_factory=list)
    homepage: str | None = None


class RepoFile(BaseModel):
    path: str
    type: str
    size: int | None = None


class ProjectAnalysis(BaseModel):
    repo_ref: RepoRef
    metadata: RepoMetadata
    summary: str
    readme_excerpt: str | None = None
    root_files: list[str] = Field(default_factory=list)
    manifest_files: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    package_managers: list[str] = Field(default_factory=list)
    test_frameworks: list[str] = Field(default_factory=list)
    ci_providers: list[str] = Field(default_factory=list)
    key_directories: list[str] = Field(default_factory=list)
    entry_points: list[str] = Field(default_factory=list)
    install_steps: list[str] = Field(default_factory=list)
    run_steps: list[str] = Field(default_factory=list)
    test_steps: list[str] = Field(default_factory=list)
    contribution_entry_points: list[str] = Field(default_factory=list)
    docs_gaps: list[str] = Field(default_factory=list)
    tooling_gaps: list[str] = Field(default_factory=list)

