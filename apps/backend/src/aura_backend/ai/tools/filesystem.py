"""
Production-grade Filesystem Tool implementation.
"""

import asyncio
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    import yaml
except ImportError:
    yaml = None

from aura_backend.ai.tools.models import ToolResult, ToolArtifact, ToolMetrics
from aura_backend.ai.tools.security import PathValidator, PermissionValidator, ToolSandbox, create_sandbox


class FilesystemTool:
    """Production-grade filesystem operations"""

    def __init__(self, sandbox: Optional[ToolSandbox] = None):
        self.sandbox = sandbox or create_sandbox()
        self.validator = PathValidator(self.sandbox)
        self.permission_validator = PermissionValidator(self.sandbox)
        self._id = "FilesystemTool"
        self._created_at = datetime.utcnow()
        self._execution_count = 0
        self._total_execution_time_ms = 0.0

    @property
    def id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return "Filesystem"

    def get_description(self) -> str:
        return "Production-grade file system operations with security"

    def get_capabilities(self):
        """Get available capabilities"""
        from aura_backend.ai.tools import ToolCapability

        return [
            ToolCapability("read-file", "Read file contents"),
            ToolCapability("write-file", "Write file contents"),
            ToolCapability("append-file", "Append to file"),
            ToolCapability("delete-file", "Delete file"),
            ToolCapability("move-file", "Move/rename file"),
            ToolCapability("copy-file", "Copy file"),
            ToolCapability("create-directory", "Create directory"),
            ToolCapability("delete-directory", "Delete directory"),
            ToolCapability("list-directory", "List directory contents"),
            ToolCapability("search-files", "Search for files"),
            ToolCapability("exists", "Check if path exists"),
            ToolCapability("stat", "Get file statistics"),
            ToolCapability("read-json", "Read JSON file"),
            ToolCapability("write-json", "Write JSON file"),
            ToolCapability("read-yaml", "Read YAML file"),
            ToolCapability("write-yaml", "Write YAML file"),
            ToolCapability("hash-file", "Calculate file hash"),
            ToolCapability("watch-directory", "Watch directory for changes"),
        ]

    def get_parameters(self):
        """Get operation parameters"""
        from aura_backend.ai.tools import ToolParameter

        return [
            ToolParameter("operation", "string", "Operation to perform", required=True),
            ToolParameter("path", "string", "File or directory path", required=False),
            ToolParameter("content", "string", "File content", required=False),
            ToolParameter("destination", "string", "Destination path", required=False),
            ToolParameter("pattern", "string", "Search pattern", required=False),
            ToolParameter("recursive", "boolean", "Recursive operation", required=False),
        ]

    def _validate_write_extension(self, path: Path) -> None:
        """
        Validate file extension for write operation.

        HIGH PRIORITY FIX: Check extension on ALL writes, not just new files.
        Prevents type confusion attacks (overwriting .txt with binary data).
        """
        ext = path.suffix.lower()
        if self.sandbox.allowed_extensions and ext not in self.sandbox.allowed_extensions:
            raise PermissionError(f"File type not allowed: {ext}")

    async def validate(self, **kwargs) -> Dict[str, Any]:
        """Validate parameters"""
        operation = kwargs.get("operation")
        path = kwargs.get("path")

        if not operation:
            return {"valid": False, "error": "operation is required"}

        if path:
            try:
                self.validator.validate_path(str(path))
            except Exception as e:
                return {"valid": False, "error": str(e)}

        return {"valid": True}

    async def execute(self, **kwargs) -> ToolResult:
        """Execute filesystem operation"""
        start_time = datetime.utcnow()
        result = ToolResult(success=True)

        try:
            operation = kwargs.get("operation")

            if operation == "read-file":
                result = await self._read_file(kwargs.get("path"), result)
            elif operation == "write-file":
                result = await self._write_file(kwargs.get("path"), kwargs.get("content"), result)
            elif operation == "append-file":
                result = await self._append_file(kwargs.get("path"), kwargs.get("content"), result)
            elif operation == "delete-file":
                result = await self._delete_file(kwargs.get("path"), result)
            elif operation == "move-file":
                result = await self._move_file(kwargs.get("path"), kwargs.get("destination"), result)
            elif operation == "copy-file":
                result = await self._copy_file(kwargs.get("path"), kwargs.get("destination"), result)
            elif operation == "create-directory":
                result = await self._create_directory(kwargs.get("path"), result)
            elif operation == "delete-directory":
                result = await self._delete_directory(kwargs.get("path"), result)
            elif operation == "list-directory":
                result = await self._list_directory(kwargs.get("path"), result)
            elif operation == "search-files":
                result = await self._search_files(kwargs.get("path"), kwargs.get("pattern"), kwargs.get("recursive", False), result)
            elif operation == "exists":
                result = await self._exists(kwargs.get("path"), result)
            elif operation == "stat":
                result = await self._stat(kwargs.get("path"), result)
            elif operation == "read-json":
                result = await self._read_json(kwargs.get("path"), result)
            elif operation == "write-json":
                result = await self._write_json(kwargs.get("path"), kwargs.get("content"), result)
            elif operation == "read-yaml":
                result = await self._read_yaml(kwargs.get("path"), result)
            elif operation == "write-yaml":
                result = await self._write_yaml(kwargs.get("path"), kwargs.get("content"), result)
            elif operation == "hash-file":
                result = await self._hash_file(kwargs.get("path"), result)
            else:
                result.success = False
                result.add_error(f"Unknown operation: {operation}")

        except Exception as e:
            result.success = False
            result.add_error(str(e))
            result.add_log("ERROR", f"Filesystem operation failed: {e}")

        # Track metrics
        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        result.duration = duration_ms
        self._execution_count += 1
        self._total_execution_time_ms += duration_ms

        return result

    async def _read_file(self, path: str, result: ToolResult) -> ToolResult:
        """Read file contents"""
        validated_path = self.validator.validate_read(path)

        size_bytes = self.validator.validate_file_size(validated_path)

        try:
            content = await asyncio.to_thread(validated_path.read_text, encoding='utf-8')
            result.data = content
            result.metadata["file_size"] = size_bytes
            result.add_log("INFO", f"Read {size_bytes} bytes from {path}")
        except UnicodeDecodeError:
            result.success = False
            result.add_error(f"File is not valid UTF-8: {path}")

        return result

    async def _write_file(self, path: str, content: str, result: ToolResult) -> ToolResult:
        """Write file contents"""
        validated_path = self.validator.validate_write(path)

        # HIGH PRIORITY FIX: Validate extension on ALL writes
        try:
            self._validate_write_extension(validated_path)
        except PermissionError as e:
            result.success = False
            result.add_error(str(e))
            return result

        try:
            content_str = str(content) if content else ""
            await asyncio.to_thread(validated_path.write_text, content_str, encoding='utf-8')
            result.data = {"written_bytes": len(content_str), "path": str(validated_path)}
            result.add_log("INFO", f"Wrote {len(content_str)} bytes to {path}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to write file: {e}")

        return result

    async def _append_file(self, path: str, content: str, result: ToolResult) -> ToolResult:
        """Append to file"""
        validated_path = self.validator.validate_write(path)

        # HIGH PRIORITY FIX: Validate extension on ALL writes
        try:
            self._validate_write_extension(validated_path)
        except PermissionError as e:
            result.success = False
            result.add_error(str(e))
            return result

        try:
            content_str = str(content) if content else ""

            # HIGH PRIORITY FIX: Use asyncio.to_thread for consistency (was using blocking I/O)
            async def append_impl():
                with open(validated_path, 'a', encoding='utf-8') as f:
                    f.write(content_str)

            await asyncio.to_thread(append_impl)
            result.data = {"appended_bytes": len(content_str), "path": str(validated_path)}
            result.add_log("INFO", f"Appended {len(content_str)} bytes to {path}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to append to file: {e}")

        return result

    async def _delete_file(self, path: str, result: ToolResult) -> ToolResult:
        """Delete file"""
        validated_path = self.validator.validate_write(path)

        if not validated_path.exists():
            result.success = False
            result.add_error(f"File not found: {path}")
            return result

        try:
            await asyncio.to_thread(validated_path.unlink)
            result.data = {"deleted": str(validated_path)}
            result.add_log("INFO", f"Deleted file: {path}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to delete file: {e}")

        return result

    async def _move_file(self, path: str, destination: str, result: ToolResult) -> ToolResult:
        """Move/rename file"""
        source_path = self.validator.validate_read(path)
        dest_path = self.validator.validate_write(destination)

        try:
            await asyncio.to_thread(source_path.rename, dest_path)
            result.data = {"source": str(source_path), "destination": str(dest_path)}
            result.add_log("INFO", f"Moved {path} to {destination}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to move file: {e}")

        return result

    async def _copy_file(self, path: str, destination: str, result: ToolResult) -> ToolResult:
        """Copy file"""
        source_path = self.validator.validate_read(path)
        dest_path = self.validator.validate_write(destination)

        try:
            await asyncio.to_thread(shutil.copy2, source_path, dest_path)
            result.data = {"source": str(source_path), "destination": str(dest_path)}
            result.add_log("INFO", f"Copied {path} to {destination}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to copy file: {e}")

        return result

    async def _create_directory(self, path: str, result: ToolResult) -> ToolResult:
        """Create directory"""
        validated_path = self.validator.validate_write(path)

        try:
            await asyncio.to_thread(validated_path.mkdir, parents=True, exist_ok=True)
            result.data = {"created": str(validated_path), "existed": validated_path.exists()}
            result.add_log("INFO", f"Created directory: {path}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to create directory: {e}")

        return result

    async def _delete_directory(self, path: str, result: ToolResult) -> ToolResult:
        """Delete directory"""
        validated_path = self.validator.validate_write(path)

        if not validated_path.exists():
            result.success = False
            result.add_error(f"Directory not found: {path}")
            return result

        try:
            await asyncio.to_thread(shutil.rmtree, validated_path)
            result.data = {"deleted": str(validated_path)}
            result.add_log("INFO", f"Deleted directory: {path}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to delete directory: {e}")

        return result

    async def _list_directory(self, path: str, result: ToolResult) -> ToolResult:
        """List directory contents"""
        validated_path = self.validator.validate_read(path)

        if not validated_path.is_dir():
            result.success = False
            result.add_error(f"Not a directory: {path}")
            return result

        try:
            entries = await asyncio.to_thread(lambda: [
                {
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file",
                    "size": entry.stat().st_size if entry.is_file() else None,
                }
                for entry in validated_path.iterdir()
            ])
            result.data = {"path": str(validated_path), "entries": entries, "count": len(entries)}
            result.add_log("INFO", f"Listed {len(entries)} entries in {path}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to list directory: {e}")

        return result

    async def _search_files(self, path: str, pattern: str, recursive: bool, result: ToolResult) -> ToolResult:
        """Search for files"""
        validated_path = self.validator.validate_read(path or "/")

        if not pattern:
            result.success = False
            result.add_error("pattern is required for search")
            return result

        try:
            search_pattern = pattern if "*" in pattern else f"*{pattern}*"
            if recursive:
                matches = list(validated_path.rglob(search_pattern))
            else:
                matches = list(validated_path.glob(search_pattern))

            files = [str(m) for m in matches if m.is_file()]
            result.data = {"path": str(validated_path), "pattern": pattern, "matches": files, "count": len(files)}
            result.add_log("INFO", f"Found {len(files)} files matching {pattern}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to search files: {e}")

        return result

    async def _exists(self, path: str, result: ToolResult) -> ToolResult:
        """Check if path exists"""
        try:
            validated_path = self.validator.validate_path(path)
            exists = validated_path.exists()
            result.data = {"path": str(validated_path), "exists": exists}
        except Exception as e:
            result.success = False
            result.add_error(str(e))

        return result

    async def _stat(self, path: str, result: ToolResult) -> ToolResult:
        """Get file statistics"""
        validated_path = self.validator.validate_read(path)

        try:
            stat_info = await asyncio.to_thread(validated_path.stat)
            result.data = {
                "path": str(validated_path),
                "size": stat_info.st_size,
                "is_file": validated_path.is_file(),
                "is_dir": validated_path.is_dir(),
                "is_symlink": validated_path.is_symlink(),
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            }
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to stat file: {e}")

        return result

    async def _read_json(self, path: str, result: ToolResult) -> ToolResult:
        """Read JSON file"""
        validated_path = self.validator.validate_read(path)

        try:
            content = await asyncio.to_thread(validated_path.read_text, encoding='utf-8')
            data = await asyncio.to_thread(json.loads, content)
            result.data = data
            result.add_log("INFO", f"Read JSON from {path}")
        except json.JSONDecodeError as e:
            result.success = False
            result.add_error(f"Invalid JSON: {e}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to read JSON: {e}")

        return result

    async def _write_json(self, path: str, content: Any, result: ToolResult) -> ToolResult:
        """Write JSON file"""
        validated_path = self.validator.validate_write(path)

        try:
            json_str = await asyncio.to_thread(json.dumps, content, indent=2)
            await asyncio.to_thread(validated_path.write_text, json_str, encoding='utf-8')
            result.data = {"path": str(validated_path), "written_bytes": len(json_str)}
            result.add_log("INFO", f"Wrote JSON to {path}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to write JSON: {e}")

        return result

    async def _read_yaml(self, path: str, result: ToolResult) -> ToolResult:
        """Read YAML file"""
        if yaml is None:
            result.success = False
            result.add_error("YAML support not available (install pyyaml)")
            return result

        validated_path = self.validator.validate_read(path)

        try:
            content = await asyncio.to_thread(validated_path.read_text, encoding='utf-8')
            data = await asyncio.to_thread(yaml.safe_load, content)
            result.data = data
            result.add_log("INFO", f"Read YAML from {path}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to read YAML: {e}")

        return result

    async def _write_yaml(self, path: str, content: Any, result: ToolResult) -> ToolResult:
        """Write YAML file"""
        if yaml is None:
            result.success = False
            result.add_error("YAML support not available (install pyyaml)")
            return result

        validated_path = self.validator.validate_write(path)

        try:
            yaml_str = await asyncio.to_thread(yaml.dump, content)
            await asyncio.to_thread(validated_path.write_text, yaml_str, encoding='utf-8')
            result.data = {"path": str(validated_path), "written_bytes": len(yaml_str)}
            result.add_log("INFO", f"Wrote YAML to {path}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to write YAML: {e}")

        return result

    async def _hash_file(self, path: str, result: ToolResult) -> ToolResult:
        """Calculate file hash"""
        validated_path = self.validator.validate_read(path)

        try:
            sha256_hash = hashlib.sha256()

            def compute_hash():
                with open(validated_path, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                return sha256_hash.hexdigest()

            hash_value = await asyncio.to_thread(compute_hash)
            result.data = {"path": str(validated_path), "sha256": hash_value}
            result.add_log("INFO", f"Computed hash for {path}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to hash file: {e}")

        return result

    async def health(self) -> Dict[str, Any]:
        """Get tool health status"""
        try:
            # Check if sandbox directory exists and is writable
            self.sandbox.base_path.mkdir(parents=True, exist_ok=True)
            is_writable = os.access(self.sandbox.base_path, os.W_OK)

            return {
                "status": "healthy" if is_writable else "degraded",
                "sandbox_path": str(self.sandbox.base_path),
                "writable": is_writable,
                "execution_count": self._execution_count,
                "total_time_ms": self._total_execution_time_ms,
            }
        except Exception as e:
            return {
                "status": "unavailable",
                "error": str(e),
            }

    @property
    def timeout_seconds(self) -> float:
        return self.sandbox.timeout_seconds

    async def get_info(self) -> Dict[str, Any]:
        """Get complete tool information"""
        return {
            "id": self.id,
            "name": self.get_name(),
            "description": self.get_description(),
            "capabilities": [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "version": cap.version,
                }
                for cap in self.get_capabilities()
            ],
            "parameters": [
                {
                    "name": param.name,
                    "type": param.type,
                    "description": param.description,
                    "required": param.required,
                }
                for param in self.get_parameters()
            ],
            "timeout_seconds": self.timeout_seconds,
            "execution_count": self._execution_count,
            "total_execution_time_ms": self._total_execution_time_ms,
        }
