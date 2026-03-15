from __future__ import annotations

import base64
import os
from urllib.parse import quote, urlparse

import httpx

from repolens.models import RepoFile, RepoMetadata, RepoRef


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None, timeout: float = 15.0) -> None:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "RepoLens/0.1.0",
        }
        auth_token = token or os.getenv("GITHUB_TOKEN")
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        )

    def close(self) -> None:
        self._client.close()

    def get_repo_ref(self, repo_url: str) -> RepoRef:
        parsed = urlparse(repo_url)
        if parsed.netloc not in {"github.com", "www.github.com"}:
            raise ValueError("RepoLens currently supports GitHub repository URLs only.")

        parts = [part for part in parsed.path.strip("/").split("/") if part]
        if len(parts) < 2:
            raise ValueError("Expected a GitHub repository URL like https://github.com/owner/repo.")

        owner, name = parts[0], parts[1].removesuffix(".git")
        return RepoRef(owner=owner, name=name, url=f"https://github.com/{owner}/{name}")

    def get_repo_metadata(self, repo: RepoRef) -> RepoMetadata:
        payload = self._get_json(f"/repos/{repo.owner}/{repo.name}")
        return RepoMetadata(
            full_name=payload["full_name"],
            description=payload.get("description"),
            default_branch=payload["default_branch"],
            stars=payload.get("stargazers_count", 0),
            open_issues=payload.get("open_issues_count", 0),
            primary_language=payload.get("language"),
            license_name=(payload.get("license") or {}).get("spdx_id"),
            topics=payload.get("topics") or [],
            homepage=payload.get("homepage"),
        )

    def get_readme(self, repo: RepoRef) -> str | None:
        try:
            payload = self._get_json(f"/repos/{repo.owner}/{repo.name}/readme")
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            raise
        return self._decode_content(payload.get("content"), payload.get("encoding"))

    def get_tree(self, repo: RepoRef, branch: str) -> list[RepoFile]:
        branch_name = quote(branch, safe="")
        branch_data = self._get_json(f"/repos/{repo.owner}/{repo.name}/branches/{branch_name}")
        commit_sha = branch_data["commit"]["sha"]
        commit_data = self._get_json(f"/repos/{repo.owner}/{repo.name}/git/commits/{commit_sha}")
        tree_sha = commit_data["tree"]["sha"]
        tree_data = self._get_json(
            f"/repos/{repo.owner}/{repo.name}/git/trees/{tree_sha}",
            params={"recursive": "1"},
        )
        return [
            RepoFile(path=item["path"], type=item["type"], size=item.get("size"))
            for item in tree_data.get("tree", [])
        ]

    def get_file_content(self, repo: RepoRef, path: str, branch: str | None = None) -> str | None:
        encoded_path = quote(path, safe="/")
        params = {"ref": branch} if branch else None
        try:
            payload = self._get_json(f"/repos/{repo.owner}/{repo.name}/contents/{encoded_path}", params=params)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            raise
        if isinstance(payload, list):
            return None
        return self._decode_content(payload.get("content"), payload.get("encoding"))

    def _get_json(self, path: str, params: dict[str, str] | None = None) -> dict:
        response = self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _decode_content(content: str | None, encoding: str | None) -> str | None:
        if not content:
            return None
        if encoding == "base64":
            decoded = base64.b64decode(content.encode("utf-8"))
            return decoded.decode("utf-8", errors="replace")
        return content
