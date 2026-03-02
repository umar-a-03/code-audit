"""Version Control System (VCS) provider protocol.

Defines the contract for interacting with code repositories.
Supports GitHub, GitLab, Bitbucket, and local repositories.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class RepoMetadata:
    """Repository metadata."""

    name: str
    description: str | None
    url: str
    branch: str
    default_branch: str
    is_private: bool
    stars: int
    forks: int
    last_updated: datetime
    languages: dict[str, int]  # language -> bytes of code


@dataclass
class FileInfo:
    """File information."""

    path: str
    name: str
    extension: str
    size: int
    is_binary: bool


@dataclass
class FileContent:
    """File content with metadata."""

    path: str
    content: str
    encoding: str
    size: int
    language: str | None


class VCSProvider(ABC):
    """Version Control System provider protocol.

    All VCS providers (GitHub, GitLab, Bitbucket) must implement this interface.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get provider name.

        Returns:
            Provider name (e.g., 'github', 'gitlab').
        """
        pass

    @abstractmethod
    async def clone_repository(
        self,
        url: str,
        branch: str | None = None,
        destination: Path | None = None,
    ) -> Path:
        """Clone a repository to local filesystem.

        Args:
            url: Repository URL.
            branch: Branch to clone (default: default branch).
            destination: Local path to clone to (default: temp directory).

        Returns:
            Path to cloned repository.
        """
        pass

    @abstractmethod
    async def get_repository_metadata(self, url: str) -> RepoMetadata:
        """Get repository metadata without cloning.

        Args:
            url: Repository URL.

        Returns:
            Repository metadata.
        """
        pass

    @abstractmethod
    async def get_file_tree(
        self,
        url: str,
        branch: str | None = None,
    ) -> list[FileInfo]:
        """Get list of all files in repository.

        Args:
            url: Repository URL.
            branch: Branch to scan.

        Returns:
            List of file information.
        """
        pass

    @abstractmethod
    async def get_file_content(
        self,
        url: str,
        file_path: str,
        branch: str | None = None,
    ) -> FileContent:
        """Get content of a single file.

        Args:
            url: Repository URL.
            file_path: Path to file in repository.
            branch: Branch to fetch from.

        Returns:
            File content with metadata.
        """
        pass

    @abstractmethod
    async def get_multiple_files(
        self,
        url: str,
        file_paths: list[str],
        branch: str | None = None,
    ) -> list[FileContent]:
        """Get content of multiple files efficiently.

        Args:
            url: Repository URL.
            file_paths: List of file paths to fetch.
            branch: Branch to fetch from.

        Returns:
            List of file contents.
        """
        pass

    @abstractmethod
    def parse_repository_url(self, url: str) -> dict[str, str]:
        """Parse repository URL into components.

        Args:
            url: Repository URL.

        Returns:
            Dict with: owner, repo_name, branch, etc.
        """
        pass

    @abstractmethod
    async def validate_access(self, url: str, token: str | None = None) -> bool:
        """Validate that we can access the repository.

        Args:
            url: Repository URL.
            token: Optional access token.

        Returns:
            True if repository is accessible.
        """
        pass

    async def cleanup_clone(self, path: Path) -> None:
        """Clean up a cloned repository.

        Args:
            path: Path to cloned repository.
        """
        import shutil

        if path.exists():
            shutil.rmtree(path)
