"""
Comprehensive tests for Milestone 4 production tools.

Tests FilesystemTool, PythonTool, and BrowserTool implementations.
"""

import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any

from aura_backend.ai.tools import (
    FilesystemTool,
    PythonTool,
    BrowserTool,
    ToolRegistry,
    ToolResult,
)
from aura_backend.ai.tools.security import ToolSandbox, PathValidator


# ============================================================================
# FILESYSTEM TOOL TESTS
# ============================================================================

class TestFilesystemTool:
    """Test FilesystemTool production implementation"""

    @pytest.fixture
    def sandbox_dir(self):
        """Create temporary sandbox for tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def filesystem_tool(self, sandbox_dir):
        """Create FilesystemTool with sandbox"""
        sandbox = ToolSandbox(base_path=sandbox_dir)
        return FilesystemTool(sandbox=sandbox)

    @pytest.mark.asyncio
    async def test_read_file(self, filesystem_tool, sandbox_dir):
        """Read file operation"""
        # Create test file
        test_file = sandbox_dir / "test.txt"
        test_file.write_text("Hello, World!")

        result = await filesystem_tool.execute(
            operation="read-file",
            path=str(test_file)
        )

        assert result.success
        assert result.data == "Hello, World!"
        assert len(result.logs) > 0

    @pytest.mark.asyncio
    async def test_write_file(self, filesystem_tool, sandbox_dir):
        """Write file operation"""
        test_file = sandbox_dir / "output.txt"

        result = await filesystem_tool.execute(
            operation="write-file",
            path=str(test_file),
            content="Test content"
        )

        assert result.success
        assert test_file.read_text() == "Test content"

    @pytest.mark.asyncio
    async def test_append_file(self, filesystem_tool, sandbox_dir):
        """Append to file operation"""
        test_file = sandbox_dir / "append.txt"
        test_file.write_text("Line 1\n")

        result = await filesystem_tool.execute(
            operation="append-file",
            path=str(test_file),
            content="Line 2\n"
        )

        assert result.success
        assert test_file.read_text() == "Line 1\nLine 2\n"

    @pytest.mark.asyncio
    async def test_create_directory(self, filesystem_tool, sandbox_dir):
        """Create directory operation"""
        new_dir = sandbox_dir / "new_dir" / "nested"

        result = await filesystem_tool.execute(
            operation="create-directory",
            path=str(new_dir)
        )

        assert result.success
        assert new_dir.exists()

    @pytest.mark.asyncio
    async def test_list_directory(self, filesystem_tool, sandbox_dir):
        """List directory operation"""
        (sandbox_dir / "file1.txt").write_text("content1")
        (sandbox_dir / "file2.txt").write_text("content2")
        (sandbox_dir / "subdir").mkdir()

        result = await filesystem_tool.execute(
            operation="list-directory",
            path=str(sandbox_dir)
        )

        assert result.success
        assert result.data["count"] == 3

    @pytest.mark.asyncio
    async def test_copy_file(self, filesystem_tool, sandbox_dir):
        """Copy file operation"""
        source = sandbox_dir / "source.txt"
        source.write_text("Source content")
        dest = sandbox_dir / "dest.txt"

        result = await filesystem_tool.execute(
            operation="copy-file",
            path=str(source),
            destination=str(dest)
        )

        assert result.success
        assert dest.read_text() == "Source content"

    @pytest.mark.asyncio
    async def test_move_file(self, filesystem_tool, sandbox_dir):
        """Move file operation"""
        source = sandbox_dir / "source.txt"
        source.write_text("Source content")
        dest = sandbox_dir / "dest.txt"

        result = await filesystem_tool.execute(
            operation="move-file",
            path=str(source),
            destination=str(dest)
        )

        assert result.success
        assert not source.exists()
        assert dest.read_text() == "Source content"

    @pytest.mark.asyncio
    async def test_delete_file(self, filesystem_tool, sandbox_dir):
        """Delete file operation"""
        test_file = sandbox_dir / "delete_me.txt"
        test_file.write_text("temporary")

        result = await filesystem_tool.execute(
            operation="delete-file",
            path=str(test_file)
        )

        assert result.success
        assert not test_file.exists()

    @pytest.mark.asyncio
    async def test_exists(self, filesystem_tool, sandbox_dir):
        """Exists operation"""
        test_file = sandbox_dir / "test.txt"
        test_file.write_text("exists")

        result = await filesystem_tool.execute(
            operation="exists",
            path=str(test_file)
        )

        assert result.success
        assert result.data["exists"] is True

    @pytest.mark.asyncio
    async def test_stat(self, filesystem_tool, sandbox_dir):
        """Stat operation"""
        test_file = sandbox_dir / "test.txt"
        test_file.write_text("content here")

        result = await filesystem_tool.execute(
            operation="stat",
            path=str(test_file)
        )

        assert result.success
        assert result.data["is_file"] is True
        assert result.data["size"] == 12

    @pytest.mark.asyncio
    async def test_read_json(self, filesystem_tool, sandbox_dir):
        """Read JSON operation"""
        import json
        test_file = sandbox_dir / "data.json"
        data = {"key": "value", "number": 42}
        test_file.write_text(json.dumps(data))

        result = await filesystem_tool.execute(
            operation="read-json",
            path=str(test_file)
        )

        assert result.success
        assert result.data["key"] == "value"
        assert result.data["number"] == 42

    @pytest.mark.asyncio
    async def test_write_json(self, filesystem_tool, sandbox_dir):
        """Write JSON operation"""
        test_file = sandbox_dir / "output.json"
        data = {"test": "data", "list": [1, 2, 3]}

        result = await filesystem_tool.execute(
            operation="write-json",
            path=str(test_file),
            content=data
        )

        assert result.success
        import json
        written = json.loads(test_file.read_text())
        assert written["test"] == "data"

    @pytest.mark.asyncio
    async def test_hash_file(self, filesystem_tool, sandbox_dir):
        """Hash file operation"""
        test_file = sandbox_dir / "hash_test.txt"
        test_file.write_text("test content")

        result = await filesystem_tool.execute(
            operation="hash-file",
            path=str(test_file)
        )

        assert result.success
        assert "sha256" in result.data
        assert len(result.data["sha256"]) == 64  # SHA256 hex length

    @pytest.mark.asyncio
    async def test_search_files(self, filesystem_tool, sandbox_dir):
        """Search files operation"""
        (sandbox_dir / "test1.txt").write_text("content")
        (sandbox_dir / "test2.txt").write_text("content")
        (sandbox_dir / "other.py").write_text("code")

        result = await filesystem_tool.execute(
            operation="search-files",
            path=str(sandbox_dir),
            pattern="*.txt"
        )

        assert result.success
        assert result.data["count"] == 2

    @pytest.mark.asyncio
    async def test_path_sandbox_enforcement(self, filesystem_tool):
        """Path sandbox prevents escape"""
        result = await filesystem_tool.execute(
            operation="read-file",
            path="/etc/passwd"
        )

        assert not result.success
        assert "outside sandbox" in result.errors[0]

    @pytest.mark.asyncio
    async def test_tool_health(self, filesystem_tool):
        """Tool reports healthy status"""
        health = await filesystem_tool.health()
        assert health["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_tool_info(self, filesystem_tool):
        """Tool provides complete information"""
        info = await filesystem_tool.get_info()
        assert info["name"] == "Filesystem"
        assert len(info["capabilities"]) > 0


# ============================================================================
# PYTHON TOOL TESTS
# ============================================================================

class TestPythonTool:
    """Test PythonTool execution"""

    @pytest.fixture
    def python_tool(self):
        """Create PythonTool instance"""
        return PythonTool(timeout_seconds=5)

    @pytest.mark.asyncio
    async def test_execute_python(self, python_tool):
        """Execute Python code"""
        result = await python_tool.execute(
            operation="execute-python",
            code="print('Hello from Python')"
        )

        assert result.success
        assert "Hello from Python" in result.data["output"]

    @pytest.mark.asyncio
    async def test_evaluate_expression(self, python_tool):
        """Evaluate Python expression"""
        result = await python_tool.execute(
            operation="evaluate-expression",
            code="2 + 2"
        )

        assert result.success
        assert result.data["value"] == "4"

    @pytest.mark.asyncio
    async def test_python_timeout(self, python_tool):
        """Python execution timeout"""
        result = await python_tool.execute(
            operation="execute-python",
            code="import time; time.sleep(10)"
        )

        assert not result.success
        assert "timeout" in result.errors[0].lower()

    @pytest.mark.asyncio
    async def test_python_error_handling(self, python_tool):
        """Python error handling"""
        result = await python_tool.execute(
            operation="execute-python",
            code="raise ValueError('test error')"
        )

        assert not result.success

    @pytest.mark.asyncio
    async def test_list_packages(self, python_tool):
        """List installed packages"""
        result = await python_tool.execute(
            operation="list-packages"
        )

        assert result.success
        assert "count" in result.data
        assert result.data["count"] > 0

    @pytest.mark.asyncio
    async def test_create_venv(self, python_tool):
        """Create virtual environment"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = await python_tool.execute(
                operation="create-venv",
                venv_path=tmpdir
            )

            assert result.success

    @pytest.mark.asyncio
    async def test_tool_health(self, python_tool):
        """Tool reports healthy status"""
        health = await python_tool.health()
        assert health["status"] == "healthy"
        assert "python_version" in health


# ============================================================================
# BROWSER TOOL TESTS (Basic - Playwright required)
# ============================================================================

class TestBrowserToolBasic:
    """Test BrowserTool basic functionality"""

    @pytest.fixture
    def browser_tool(self):
        """Create BrowserTool instance"""
        try:
            return BrowserTool(headless=True, timeout_seconds=10)
        except ImportError:
            pytest.skip("Playwright not installed")

    @pytest.mark.asyncio
    async def test_tool_health(self, browser_tool):
        """Tool reports health status"""
        health = await browser_tool.health()
        assert "status" in health
        assert health["browser_launched"] is False

    @pytest.mark.asyncio
    async def test_tool_info(self, browser_tool):
        """Tool provides information"""
        info = await browser_tool.get_info()
        assert info["name"] == "Browser"
        assert len(info["capabilities"]) > 0


# ============================================================================
# TOOL REGISTRY TESTS
# ============================================================================

class TestToolRegistry:
    """Test ToolRegistry capability discovery"""

    @pytest.fixture
    def registry_with_tools(self):
        """Create registry with test tools"""
        try:
            registry = ToolRegistry()
            registry.register(FilesystemTool())
            registry.register(PythonTool())
            registry.register(BrowserTool())
            return registry
        except ImportError:
            pytest.skip("Playwright not installed")

    def test_register_tool(self):
        """Register a tool"""
        registry = ToolRegistry()
        tool = FilesystemTool()
        registry.register(tool)

        assert registry.count() == 1
        assert registry.get("FilesystemTool") is tool

    def test_find_by_capability(self, registry_with_tools):
        """Find tools by capability"""
        tools = registry_with_tools.find_by_capability("read-file")
        assert len(tools) > 0
        assert any(t.id == "FilesystemTool" for t in tools)

    def test_list_capabilities(self, registry_with_tools):
        """List all capabilities"""
        caps = registry_with_tools.list_capabilities()
        assert len(caps) > 0
        assert "read-file" in caps

    @pytest.mark.asyncio
    async def test_registry_health(self, registry_with_tools):
        """Get health of all tools"""
        health = await registry_with_tools.health()
        assert len(health) > 0
        assert "FilesystemTool" in health

    @pytest.mark.asyncio
    async def test_registry_health_all(self, registry_with_tools):
        """Get detailed health with metrics"""
        health = await registry_with_tools.health_all()
        assert len(health) > 0

        fs_health = health.get("FilesystemTool")
        assert "execution_count" in fs_health

    def test_update_metrics(self):
        """Update tool metrics"""
        registry = ToolRegistry()
        tool = FilesystemTool()
        registry.register(tool)

        registry.update_metrics("FilesystemTool", 100.0)
        registry.update_metrics("FilesystemTool", 200.0)

        metrics = registry.get_metrics("FilesystemTool")
        assert metrics["execution_count"] == 2
        assert metrics["total_time_ms"] == 300.0
        assert metrics["average_time_ms"] == 150.0

    def test_get_tool_info(self, registry_with_tools):
        """Get tool information with metrics"""
        info = registry_with_tools.get_tool_info("FilesystemTool")
        assert info is not None
        assert info["name"] == "Filesystem"
        assert "metrics" in info


# ============================================================================
# SECURITY TESTS
# ============================================================================

class TestPathValidator:
    """Test path validation and sandbox enforcement"""

    @pytest.fixture
    def validator(self):
        """Create path validator"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sandbox = ToolSandbox(base_path=Path(tmpdir))
            yield PathValidator(sandbox)

    def test_valid_path_within_sandbox(self, validator):
        """Valid path within sandbox"""
        path = validator.validate_path("test.txt")
        assert path.is_absolute()

    def test_path_outside_sandbox_rejected(self, validator):
        """Path outside sandbox is rejected"""
        with pytest.raises(PermissionError):
            validator.validate_path("../../../etc/passwd")

    def test_file_extension_validation(self, validator):
        """File extension validation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sandbox = ToolSandbox(
                base_path=Path(tmpdir),
                allowed_extensions={".txt", ".json"}
            )
            val = PathValidator(sandbox)

            # Allowed extension
            path = val.validate_write("test.txt")
            assert path is not None

            # Disallowed extension
            with pytest.raises(PermissionError):
                val.validate_write("test.exe")


# ============================================================================
# TOOL RESULT TESTS
# ============================================================================

class TestToolResult:
    """Test enhanced ToolResult model"""

    def test_tool_result_creation(self):
        """Create tool result"""
        result = ToolResult(success=True, data={"key": "value"})
        assert result.success
        assert result.data["key"] == "value"

    def test_tool_result_logs(self):
        """Tool result logging"""
        result = ToolResult(success=True)
        result.add_log("INFO", "Test message")
        assert len(result.logs) == 1
        assert result.logs[0].level == "INFO"

    def test_tool_result_warnings(self):
        """Tool result warnings"""
        result = ToolResult(success=True)
        result.add_warning("Test warning")
        assert "Test warning" in result.warnings

    def test_tool_result_errors(self):
        """Tool result errors"""
        result = ToolResult(success=False)
        result.add_error("Test error")
        assert "Test error" in result.errors

    def test_tool_result_serialization(self):
        """Serialize tool result"""
        result = ToolResult(success=True, data={"test": "data"})
        result.add_log("INFO", "Message")
        result.add_warning("Warning")

        serialized = result.to_dict()
        assert serialized["success"]
        assert len(serialized["logs"]) == 1
        assert len(serialized["warnings"]) == 1
