from pathlib import Path

from typer.testing import CliRunner

from repolens import cli
from tests.fixtures import sample_analysis

runner = CliRunner()


def test_scan_command_renders_summary(monkeypatch) -> None:
    monkeypatch.setattr(cli, "_analyze", lambda repo_url: sample_analysis())

    result = runner.invoke(cli.app, ["scan", "https://github.com/acme/sample"])

    assert result.exit_code == 0
    assert "acme/sample" in result.stdout
    assert "Python" in result.stdout
    assert "pytest" in result.stdout


def test_export_command_writes_markdown(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cli, "_analyze", lambda repo_url: sample_analysis())
    output_path = tmp_path / "report.md"

    result = runner.invoke(
        cli.app,
        ["export", "https://github.com/acme/sample", "--output", str(output_path)],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert "RepoLens report for acme/sample" in output_path.read_text(encoding="utf-8")

