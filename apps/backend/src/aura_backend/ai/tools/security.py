"""
Security and sandboxing utilities for tool execution.
"""

import os
import stat
from pathlib import Path
from typing import Optional, Set
from dataclasses import dataclass


@dataclass
class ToolSandbox:
    """Sandbox configuration for tool execution"""

    base_path: Path
    allowed_extensions: Set[str] = None
    allowed_directories: Set[Path] = None
    max_file_size_mb: int = 100
    max_total_size_mb: int = 1000
    read_only_paths: Set[Path] = None
    timeout_seconds: int = 300

    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = {
                ".py", ".txt", ".json", ".yaml", ".yml",
                ".md", ".csv", ".xml", ".html", ".js",
                ".ts", ".tsx", ".jsx", ".css", ".scss"
            }
        if self.allowed_directories is None:
            self.allowed_directories = {self.base_path}
        if self.read_only_paths is None:
            self.read_only_paths = set()


class PathValidator:
    """Validates file paths for security"""

    def __init__(self, sandbox: ToolSandbox):
        self.sandbox = sandbox
        self.base_path = sandbox.base_path.resolve()

    def validate_path(self, path: str) -> Path:
        """
        Validate and resolve a path.

        Ensures the path is within sandbox.
        """
        try:
            requested_path = Path(path).resolve()
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid path: {path}") from e

        # Check if path is within allowed directories
        is_within = any(
            requested_path == allowed or requested_path.is_relative_to(allowed)
            for allowed in self.sandbox.allowed_directories
        )
        if not is_within:
            raise PermissionError(f"Path outside sandbox: {path}")

        return requested_path

    def validate_read(self, path: str) -> Path:
        """Validate path for read operation"""
        validated = self.validate_path(path)

        if not validated.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if validated.is_dir():
            if not os.access(validated, os.R_OK):
                raise PermissionError(f"No read permission: {path}")
        else:
            if not validated.is_file():
                raise ValueError(f"Not a file: {path}")

        return validated

    def validate_write(self, path: str) -> Path:
        """Validate path for write operation"""
        validated = self.validate_path(path)

        # Check if path is in read-only locations
        if any(validated.is_relative_to(ro) for ro in self.sandbox.read_only_paths):
            raise PermissionError(f"Path is read-only: {path}")

        # Check parent directory is writable
        parent = validated.parent
        if parent.exists() and not os.access(parent, os.W_OK):
            raise PermissionError(f"No write permission for parent: {path}")

        # Check file extension if it's a new file
        if not validated.exists():
            ext = validated.suffix.lower()
            if self.sandbox.allowed_extensions and ext not in self.sandbox.allowed_extensions:
                raise PermissionError(f"File type not allowed: {ext}")

        return validated

    def validate_file_size(self, path: Path) -> int:
        """Validate file size"""
        if not path.exists():
            return 0

        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > self.sandbox.max_file_size_mb:
            raise ValueError(
                f"File too large: {size_mb:.1f}MB "
                f"(max: {self.sandbox.max_file_size_mb}MB)"
            )

        return int(size_mb * 1024 * 1024)


class PermissionValidator:
    """Validates operation permissions"""

    def __init__(self, sandbox: ToolSandbox):
        self.sandbox = sandbox

    def can_read(self, path: Path) -> bool:
        """Check if file can be read"""
        try:
            return path.exists() and os.access(path, os.R_OK)
        except (OSError, ValueError):
            return False

    def can_write(self, path: Path) -> bool:
        """Check if file can be written"""
        if any(path.is_relative_to(ro) for ro in self.sandbox.read_only_paths):
            return False

        try:
            if path.exists():
                return os.access(path, os.W_OK)
            else:
                return os.access(path.parent, os.W_OK)
        except (OSError, ValueError):
            return False

    def can_delete(self, path: Path) -> bool:
        """Check if file can be deleted"""
        if any(path.is_relative_to(ro) for ro in self.sandbox.read_only_paths):
            return False

        try:
            return path.exists() and os.access(path.parent, os.W_OK)
        except (OSError, ValueError):
            return False


class ResourceLimits:
    """Resource limit tracking"""

    def __init__(self, max_memory_mb: int = 256, max_cpu_percent: float = 80.0):
        self.max_memory_mb = max_memory_mb
        self.max_cpu_percent = max_cpu_percent

    def get_estimated_memory_mb(self, size_bytes: int) -> float:
        """Estimate memory usage for data of given size"""
        return size_bytes / (1024 * 1024) * 1.5  # 1.5x factor for overhead

    def check_memory_available(self, needed_mb: float) -> bool:
        """Check if enough memory available"""
        return needed_mb <= self.max_memory_mb

    def validate_memory(self, needed_mb: float) -> None:
        """Validate memory requirement"""
        if not self.check_memory_available(needed_mb):
            raise MemoryError(
                f"Insufficient memory: {needed_mb:.1f}MB needed "
                f"(max: {self.max_memory_mb}MB)"
            )


def create_sandbox(base_path: Optional[str] = None) -> ToolSandbox:
    """Create a tool sandbox"""
    if base_path is None:
        base_path = os.path.expanduser("~/.aura/tools_sandbox")

    base = Path(base_path)
    base.mkdir(parents=True, exist_ok=True)

    return ToolSandbox(
        base_path=base,
        allowed_directories={base},
        timeout_seconds=300
    )


@dataclass
class URLSecurityPolicy:
    """URL access control policy for browser tool"""

    allow_http: bool = True
    allow_https: bool = True
    allow_localhost: bool = False
    allow_private_ips: bool = False
    allow_cloud_metadata: bool = False
    blocked_protocols: Set[str] = None
    blocked_ip_ranges: List[str] = None

    def __post_init__(self):
        if self.blocked_protocols is None:
            self.blocked_protocols = {"file", "ftp", "javascript", "data", "blob"}
        if self.blocked_ip_ranges is None:
            self.blocked_ip_ranges = [
                "127.0.0.0/8",      # localhost
                "0.0.0.0/8",        # this network
                "10.0.0.0/8",       # private
                "172.16.0.0/12",    # private
                "192.168.0.0/16",   # private
                "169.254.0.0/16",   # link-local/metadata
            ]


def create_default_url_policy() -> URLSecurityPolicy:
    """Create default URL security policy (secure for untrusted LLMs)"""
    return URLSecurityPolicy(
        allow_http=True,
        allow_https=True,
        allow_localhost=False,
        allow_private_ips=False,
        allow_cloud_metadata=False,
    )


def create_permissive_url_policy() -> URLSecurityPolicy:
    """Create permissive policy (for testing only)"""
    return URLSecurityPolicy(
        allow_http=True,
        allow_https=True,
        allow_localhost=True,
        allow_private_ips=True,
        allow_cloud_metadata=False,  # Never allow metadata
    )


class URLValidator:
    """Validates URLs for security"""

    def __init__(self, policy: URLSecurityPolicy = None):
        self.policy = policy or create_default_url_policy()

    def validate_url(self, url: str) -> str:
        """
        Validate URL for security.

        Ensures URL is safe to navigate to.
        """
        try:
            from urllib.parse import urlparse
            import ipaddress
        except ImportError as e:
            raise ImportError("urllib required for URL validation") from e

        if not url:
            raise ValueError("URL is empty")

        if len(url) > 2048:
            raise ValueError("URL too long")

        parsed = urlparse(url)
        scheme = parsed.scheme.lower()

        # Check protocol
        if scheme in self.policy.blocked_protocols:
            raise PermissionError(f"Protocol not allowed: {scheme}")

        if scheme == "http" and not self.policy.allow_http:
            raise PermissionError("HTTP not allowed")

        if scheme == "https" and not self.policy.allow_https:
            raise PermissionError("HTTPS not allowed")

        if scheme not in ("http", "https"):
            raise PermissionError(f"Only http/https allowed, got: {scheme}")

        # Check hostname/IP
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("URL has no hostname")

        # Check for localhost
        if hostname.lower() in ("localhost", "127.0.0.1", "::1", "[::1]"):
            if not self.policy.allow_localhost:
                raise PermissionError("localhost not allowed")

        # Check for private IPs
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private and not self.policy.allow_private_ips:
                raise PermissionError(f"Private IP not allowed: {hostname}")
            if ip.is_loopback and not self.policy.allow_localhost:
                raise PermissionError(f"Loopback IP not allowed: {hostname}")
            if ip.is_link_local:
                if not self.policy.allow_cloud_metadata:
                    raise PermissionError(f"Link-local IP not allowed: {hostname}")
        except ValueError:
            # Not an IP address, it's a hostname - check if it resolves to private
            pass

        return url
