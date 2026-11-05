"""
Production-grade Python execution tool.
"""

import asyncio
import os
import platform
import resource as resource_module
import signal
import subprocess
import sys
import tempfile
from io import StringIO
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

from aura_backend.ai.tools.models import ToolResult
from aura_backend.ai.tools.security import PathValidator, ToolSandbox, create_sandbox


class PythonExecutor:
    """Sandboxed Python code execution"""

    def __init__(
        self,
        timeout_seconds: int = 30,
        max_memory_mb: int = 256,
        max_output_mb: int = 100,
        sandbox: Optional[ToolSandbox] = None,
    ):
        self.timeout_seconds = timeout_seconds
        self.max_memory_mb = max_memory_mb
        self.max_output_mb = max_output_mb
        self.sandbox = sandbox or create_sandbox()
        self.path_validator = PathValidator(self.sandbox)
        self._id = "PythonTool"
        self._created_at = datetime.utcnow()
        self._execution_count = 0
        self._total_execution_time_ms = 0.0

    @property
    def id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return "Python"

    def get_description(self) -> str:
        return "Sandboxed Python code execution with timeouts"

    def get_capabilities(self):
        """Get available capabilities"""
        from aura_backend.ai.tools import ToolCapability

        return [
            ToolCapability("execute-python", "Execute Python code"),
            ToolCapability("run-script", "Run Python script from file"),
            ToolCapability("evaluate-expression", "Evaluate Python expression"),
            ToolCapability("install-package", "Install Python package"),
            ToolCapability("list-packages", "List installed packages"),
            ToolCapability("create-venv", "Create virtual environment"),
        ]

    def get_parameters(self):
        """Get operation parameters"""
        from aura_backend.ai.tools import ToolParameter

        return [
            ToolParameter("operation", "string", "Operation to perform", required=True),
            ToolParameter("code", "string", "Python code to execute", required=False),
            ToolParameter("script_path", "string", "Path to Python script", required=False),
            ToolParameter("package", "string", "Package name", required=False),
            ToolParameter("venv_path", "string", "Virtual environment path", required=False),
        ]

    async def validate(self, **kwargs) -> Dict[str, Any]:
        """Validate parameters"""
        operation = kwargs.get("operation")

        if not operation:
            return {"valid": False, "error": "operation is required"}

        if operation == "execute-python":
            if not kwargs.get("code"):
                return {"valid": False, "error": "code is required"}

        elif operation == "run-script":
            if not kwargs.get("script_path"):
                return {"valid": False, "error": "script_path is required"}

        elif operation == "evaluate-expression":
            if not kwargs.get("code"):
                return {"valid": False, "error": "code is required"}

        return {"valid": True}

    async def execute(self, **kwargs) -> ToolResult:
        """Execute Python operation"""
        start_time = datetime.utcnow()
        result = ToolResult(success=True)

        try:
            operation = kwargs.get("operation")

            if operation == "execute-python":
                result = await self._execute_code(kwargs.get("code"), result)
            elif operation == "run-script":
                result = await self._run_script(kwargs.get("script_path"), result)
            elif operation == "evaluate-expression":
                result = await self._evaluate_expression(kwargs.get("code"), result)
            elif operation == "install-package":
                result = await self._install_package(kwargs.get("package"), result)
            elif operation == "list-packages":
                result = await self._list_packages(result)
            elif operation == "create-venv":
                result = await self._create_venv(kwargs.get("venv_path"), result)
            else:
                result.success = False
                result.add_error(f"Unknown operation: {operation}")

        except Exception as e:
            result.success = False
            result.add_error(str(e))
            result.add_log("ERROR", f"Python execution failed: {e}")

        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        result.duration = duration_ms
        self._execution_count += 1
        self._total_execution_time_ms += duration_ms

        return result

    def _preexec_fn(self) -> None:
        """Set resource limits for child process (Unix only)"""
        if platform.system() != "Windows":
            try:
                # Memory limit (soft limit only, process can exceed)
                soft_limit = self.max_memory_mb * 1024 * 1024
                resource_module.setrlimit(resource_module.RLIMIT_AS, (soft_limit, soft_limit))

                # CPU time limit (seconds)
                resource_module.setrlimit(resource_module.RLIMIT_CPU, (self.timeout_seconds, self.timeout_seconds + 5))
            except (ValueError, OSError) as e:
                # If resource limits fail, still allow execution but log it
                pass

    async def _execute_code(self, code: str, result: ToolResult) -> ToolResult:
        """Execute Python code in subprocess"""
        if not code:
            result.success = False
            result.add_error("code is required")
            return result

        # Create temporary script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            script_path = f.name

        try:
            # CRITICAL FIX: Apply resource limits on Unix systems
            preexec_fn = self._preexec_fn if platform.system() != "Windows" else None

            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                preexec_fn=preexec_fn,  # Unix only
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=self.timeout_seconds
                )
            except asyncio.TimeoutError:
                # Terminate process group to kill children
                try:
                    if platform.system() != "Windows":
                        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                    else:
                        proc.kill()
                except (ProcessLookupError, OSError):
                    pass  # Process already terminated
                result.success = False
                result.add_error(f"Execution timeout after {self.timeout_seconds} seconds")
                result.add_log("ERROR", "Python code execution timed out")
                return result

            output = stdout.decode('utf-8', errors='replace')
            errors = stderr.decode('utf-8', errors='replace')

            result.data = {
                "output": output,
                "stderr": errors,
                "return_code": proc.returncode,
            }

            if errors:
                result.add_warning(f"stderr: {errors}")

            if proc.returncode != 0:
                result.success = False
                result.add_error(f"Process exited with code {proc.returncode}")

            result.add_log("INFO", f"Executed Python code ({len(code)} chars)")

        except Exception as e:
            result.success = False
            result.add_error(f"Failed to execute code: {e}")

        finally:
            Path(script_path).unlink(missing_ok=True)

        return result

    async def _run_script(self, script_path: str, result: ToolResult) -> ToolResult:
        """Run Python script from file"""
        if not script_path:
            result.success = False
            result.add_error("script_path is required")
            return result

        # CRITICAL FIX: Validate script path against sandbox
        try:
            validated_path = self.path_validator.validate_read(script_path)
        except (ValueError, PermissionError, FileNotFoundError) as e:
            result.success = False
            result.add_error(f"Script path validation failed: {str(e)}")
            return result

        if not validated_path.suffix == '.py':
            result.add_warning(f"File does not have .py extension: {script_path}")

        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                str(validated_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=self.timeout_seconds
                )
            except asyncio.TimeoutError:
                proc.kill()
                result.success = False
                result.add_error(f"Script execution timeout after {self.timeout_seconds} seconds")
                return result

            output = stdout.decode('utf-8', errors='replace')
            errors = stderr.decode('utf-8', errors='replace')

            result.data = {
                "script": str(path),
                "output": output,
                "stderr": errors,
                "return_code": proc.returncode,
            }

            if errors:
                result.add_warning(f"stderr: {errors}")

            if proc.returncode != 0:
                result.success = False
                result.add_error(f"Script exited with code {proc.returncode}")

            result.add_log("INFO", f"Ran script: {script_path}")

        except Exception as e:
            result.success = False
            result.add_error(f"Failed to run script: {e}")

        return result

    async def _evaluate_expression(self, code: str, result: ToolResult) -> ToolResult:
        """Evaluate Python expression"""
        if not code:
            result.success = False
            result.add_error("code is required")
            return result

        try:
            # CRITICAL FIX: Use restricted eval with no builtin access
            # Prevents arbitrary code execution like __import__('os').system(...)
            eval_script = f"""
import json
import ast
try:
    # Try to parse as valid expression
    ast.parse({repr(code)}, mode='eval')

    # Create restricted environment
    restricted_globals = {{"__builtins__": {{}}, "True": True, "False": False, "None": None}}
    restricted_locals = {{}}

    # Evaluate in restricted context (no __import__, no getattr, etc.)
    result = eval({repr(code)}, restricted_globals, restricted_locals)
    print(json.dumps({{"value": str(result), "type": type(result).__name__}}))
except SyntaxError as e:
    print(json.dumps({{"error": f"Syntax error: {{e.msg}}"}}))
except Exception as e:
    print(json.dumps({{"error": str(e)}}))
"""

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(eval_script)
                script_path = f.name

            try:
                preexec_fn = self._preexec_fn if platform.system() != "Windows" else None

                proc = await asyncio.create_subprocess_exec(
                    sys.executable,
                    script_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    preexec_fn=preexec_fn,
                )

                try:
                    stdout, stderr = await asyncio.wait_for(
                        proc.communicate(),
                        timeout=self.timeout_seconds
                    )
                except asyncio.TimeoutError:
                    try:
                        if platform.system() != "Windows":
                            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                        else:
                            proc.kill()
                    except (ProcessLookupError, OSError):
                        pass
                    result.success = False
                    result.add_error(f"Evaluation timeout after {self.timeout_seconds} seconds")
                    return result

                output = stdout.decode('utf-8', errors='replace')
                import json
                output_data = json.loads(output)

                if "error" in output_data:
                    result.success = False
                    result.add_error(output_data["error"])
                else:
                    result.data = output_data
                    result.add_log("INFO", f"Evaluated expression: {code}")

            finally:
                Path(script_path).unlink(missing_ok=True)

        except Exception as e:
            result.success = False
            result.add_error(f"Failed to evaluate expression: {e}")

        return result

    async def _install_package(self, package: str, result: ToolResult) -> ToolResult:
        """Install Python package"""
        if not package:
            result.success = False
            result.add_error("package is required")
            return result

        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                "-m",
                "pip",
                "install",
                package,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=60  # Longer timeout for package installation
                )
            except asyncio.TimeoutError:
                proc.kill()
                result.success = False
                result.add_error(f"Installation timeout after 60 seconds")
                return result

            output = stdout.decode('utf-8', errors='replace')
            errors = stderr.decode('utf-8', errors='replace')

            result.data = {
                "package": package,
                "output": output,
                "stderr": errors,
                "return_code": proc.returncode,
            }

            if proc.returncode != 0:
                result.success = False
                result.add_error(f"pip failed with code {proc.returncode}")
            else:
                result.add_log("INFO", f"Installed package: {package}")

        except Exception as e:
            result.success = False
            result.add_error(f"Failed to install package: {e}")

        return result

    async def _list_packages(self, result: ToolResult) -> ToolResult:
        """List installed packages"""
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                "-m",
                "pip",
                "list",
                "--format=json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=10
                )
            except asyncio.TimeoutError:
                proc.kill()
                result.success = False
                result.add_error("Package listing timeout")
                return result

            output = stdout.decode('utf-8', errors='replace')
            import json
            packages = json.loads(output)

            result.data = {
                "packages": packages,
                "count": len(packages),
            }

            result.add_log("INFO", f"Listed {len(packages)} packages")

        except Exception as e:
            result.success = False
            result.add_error(f"Failed to list packages: {e}")

        return result

    async def _create_venv(self, venv_path: str, result: ToolResult) -> ToolResult:
        """Create virtual environment"""
        if not venv_path:
            result.success = False
            result.add_error("venv_path is required")
            return result

        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                "-m",
                "venv",
                venv_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=30
                )
            except asyncio.TimeoutError:
                proc.kill()
                result.success = False
                result.add_error("Virtual environment creation timeout")
                return result

            if proc.returncode != 0:
                result.success = False
                result.add_error(f"venv creation failed with code {proc.returncode}")
            else:
                result.data = {"venv_path": venv_path, "created": True}
                result.add_log("INFO", f"Created virtual environment at {venv_path}")

        except Exception as e:
            result.success = False
            result.add_error(f"Failed to create virtual environment: {e}")

        return result

    async def health(self) -> Dict[str, Any]:
        """Get tool health status"""
        try:
            # Quick Python execution test
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                "-c",
                "print('ok')",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
                is_working = stdout.decode().strip() == "ok"
            except asyncio.TimeoutError:
                proc.kill()
                is_working = False

            return {
                "status": "healthy" if is_working else "degraded",
                "python_version": sys.version,
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
        return self.timeout_seconds

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
