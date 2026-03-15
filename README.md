# RepoLens

RepoLens is an open-source CLI that helps developers understand public GitHub repositories and generate contributor onboarding guides.

## Why

Open-source repositories are often hard to approach for first-time contributors. RepoLens scans a public GitHub repository, detects its likely stack, and turns that into a quick-start guide plus contribution suggestions.

## Features

- Scan a public repository and summarize its structure
- Detect likely languages, package managers, and test frameworks
- Generate a 5-minute onboarding guide for contributors
- Highlight contribution entry points and maintenance gaps
- Export a Markdown report for docs, issues, or internal notes

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
```

If you hit GitHub API rate limits, set `GITHUB_TOKEN` before running RepoLens.

## Usage

```bash
repolens scan https://github.com/tiangolo/typer
repolens guide https://github.com/tiangolo/typer
repolens contribute https://github.com/tiangolo/typer
repolens export https://github.com/tiangolo/typer --format markdown --output typer-report.md
```

## Commands

### `repolens scan <repo-url>`

Print a structured summary including:

- Repository metadata
- Root files and key directories
- Likely languages and package managers
- Test and CI signals

### `repolens guide <repo-url>`

Generate a concise onboarding guide that answers:

- How to install dependencies
- How to run the project
- How to execute tests
- Which folders to inspect first

### `repolens contribute <repo-url>`

Generate contributor-oriented suggestions such as:

- Documentation gaps
- Missing tooling or CI
- Good first areas to explore

### `repolens export <repo-url> --format markdown`

Generate a Markdown report that can be pasted into a wiki, issue, or onboarding note.

## How It Works

RepoLens uses the public GitHub API to:

1. Read repository metadata and README content
2. Inspect the repository tree
3. Fetch a small set of common manifest files such as `package.json` and `pyproject.toml`
4. Derive a practical onboarding summary from those signals

## Roadmap

- Support more ecosystems beyond Python and Node
- Add local repository scanning
- Export JSON reports
- Draft `CONTRIBUTING.md` suggestions
- Inspect CI and docs quality more deeply

## Development

```bash
pytest
```

## Initial Codex Task Queue

1. Improve package-manager detection for Poetry, uv, and monorepos
2. Support local directory scanning in addition to GitHub URLs
3. Add JSON export alongside Markdown export
4. Detect CI details and surface failing workflow clues
5. Draft `CONTRIBUTING.md` suggestions for repositories missing maintainer docs
6. Expand heuristics for Go and Rust entry points
7. Add snapshot-style CLI output tests
8. Cache GitHub API responses to reduce repeated requests
9. Surface "good first issue" candidates from labels and issue metadata
10. Add release automation and publish the package to PyPI

## Project Status

`v0.1.0` is an MVP focused on public GitHub repositories and a polished terminal experience.

## License

MIT
