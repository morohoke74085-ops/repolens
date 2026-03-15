from repolens.analyzer import RepoAnalyzer
from tests.fixtures import FakeGitHubClient


def test_analyzer_detects_python_repo_signals() -> None:
    analyzer = RepoAnalyzer(client=FakeGitHubClient())

    analysis = analyzer.analyze("https://github.com/acme/sample")

    assert analysis.metadata.full_name == "acme/sample"
    assert analysis.languages == ["Python"]
    assert analysis.package_managers == ["pip"]
    assert analysis.test_frameworks == ["pytest"]
    assert analysis.ci_providers == ["GitHub Actions"]
    assert "Run `pytest` for the primary test suite." in analysis.test_steps
    assert "Read `README.md` first for setup context and repository intent." in analysis.entry_points

