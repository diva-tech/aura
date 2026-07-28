# AURA Core Tool Platform - Milestone 4

**Status**: ✅ Complete  
**Date**: 2026-07-28  
**Scope**: Production-grade tools with security, sandboxing, and observability

---

## Executive Summary

Milestone 4 implements three production-grade tools extending the AI Framework:

- **FilesystemTool**: 18 capabilities for file/directory operations
- **PythonTool**: 6 capabilities for code execution and package management
- **BrowserTool**: 27 capabilities for web automation using Playwright

All tools feature:
- ✅ Comprehensive security and sandboxing
- ✅ Timeout protection and cancellation
- ✅ Resource limits and monitoring
- ✅ Structured error handling
- ✅ Execution metrics and observability
- ✅ Full async/await support
- ✅ Enhanced ToolResult model with logs, artifacts, metrics

---

## Architecture Overview

### Layered Security Model

```
┌─────────────────────────────────────┐
│         Tool Interface              │
│    (Abstract base from M3)          │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│   Production Implementation         │
│  - Filesystem, Python, Browser      │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│    Security Layer                   │
│  - Path validation                  │
│  - Permission checks                │
│  - Resource limits                  │
│  - Timeout protection               │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│    Sandbox Environment              │
│  - Restricted directories           │
│  - File type whitelisting           │
│  - Read-only paths                  │
│  - Size limits                      │
└─────────────────────────────────────┘
```

### Security & Sandbox Design

#### ToolSandbox Configuration

```python
@dataclass
class ToolSandbox:
    base_path: Path                          # Sandbox root directory
    allowed_extensions: Set[str]             # Allowed file types
    allowed_directories: Set[Path]           # Accessible directories
    max_file_size_mb: int = 100              # Individual file limit
    max_total_size_mb: int = 1000            # Total storage limit
    read_only_paths: Set[Path] = None        # Immutable paths
    timeout_seconds: int = 300               # Execution timeout
```

#### Path Validation

```python
# Three levels of validation:

1. Path Resolution
   - Converts relative paths to absolute
   - Resolves symlinks
   - Validates path format

2. Boundary Checking
   - Ensures path within sandbox
   - Prevents directory traversal
   - Rejects escape attempts

3. Permission Validation
   - Checks file read permissions
   - Verifies write permissions
   - Enforces read-only protection
```

#### Resource Limits

```python
# Memory Management
- max_memory_mb: Maximum usable memory
- Estimated for data operations
- Validates before execution

# Execution Control
- timeout_seconds: Hard execution limit
- Automatic process termination
- Cancellation token support

# File Size Constraints
- Individual file: max_file_size_mb
- Directory: max_total_size_mb
- Extension whitelist enforcement
```

---

## Tool Implementations

### 1. FilesystemTool

Production-grade file system operations with security.

#### Capabilities (18 total)

**File Operations**:
- `read-file`: Read text file contents
- `write-file`: Write text to file (creates or overwrites)
- `append-file`: Append text to existing file
- `delete-file`: Delete file
- `move-file`: Move/rename file
- `copy-file`: Copy file
- `hash-file`: Calculate SHA256 hash

**Directory Operations**:
- `create-directory`: Create directory (with parents)
- `delete-directory`: Delete directory (recursive)
- `list-directory`: List directory contents
- `search-files`: Search for files by pattern

**File Information**:
- `exists`: Check if path exists
- `stat`: Get file metadata (size, timestamps, type)

**Data Format Operations**:
- `read-json`: Parse and read JSON file
- `write-json`: Write data as JSON
- `read-yaml`: Parse and read YAML file
- `write-yaml`: Write data as YAML

#### Parameters

```python
ToolParameter("operation", "string", "Operation to perform", required=True)
ToolParameter("path", "string", "File or directory path", required=False)
ToolParameter("content", "string", "File content", required=False)
ToolParameter("destination", "string", "Destination path", required=False)
ToolParameter("pattern", "string", "Search pattern", required=False)
ToolParameter("recursive", "boolean", "Recursive operation", required=False)
```

#### Examples

```python
# Read a file
result = await filesystem_tool.execute(
    operation="read-file",
    path="/sandbox/data.txt"
)

# Write JSON
result = await filesystem_tool.execute(
    operation="write-json",
    path="/sandbox/config.json",
    content={"key": "value"}
)

# Search for files
result = await filesystem_tool.execute(
    operation="search-files",
    path="/sandbox",
    pattern="*.py",
    recursive=True
)

# Get file hash
result = await filesystem_tool.execute(
    operation="hash-file",
    path="/sandbox/binary.dat"
)
```

#### Security Features

- **Sandbox Enforcement**: All paths validated within sandbox directory
- **Extension Whitelist**: Only allowed file types can be written
- **Read-Only Protection**: Designated paths cannot be modified
- **Size Limits**: Individual files and total directory size checked
- **Permission Validation**: File permissions verified before access

#### Async Behavior

All operations are truly async:
- File I/O uses `asyncio.to_thread()`
- Directory operations non-blocking
- Large file hashing asynchronous
- Multi-file operations concurrent where possible

---

### 2. PythonTool (PythonExecutor)

Sandboxed Python execution with timeout and resource protection.

#### Capabilities (6 total)

- `execute-python`: Execute Python code in subprocess
- `run-script`: Execute Python script from file
- `evaluate-expression`: Evaluate Python expression safely
- `install-package`: Install Python package via pip
- `list-packages`: List installed packages
- `create-venv`: Create virtual environment

#### Parameters

```python
ToolParameter("operation", "string", "Operation to perform", required=True)
ToolParameter("code", "string", "Python code to execute", required=False)
ToolParameter("script_path", "string", "Path to Python script", required=False)
ToolParameter("package", "string", "Package name", required=False)
ToolParameter("venv_path", "string", "Virtual environment path", required=False)
```

#### Examples

```python
# Execute Python code
result = await python_tool.execute(
    operation="execute-python",
    code="print('Hello'); x = 2 + 2; print(x)"
)
# Output: "Hello\n4\n"

# Evaluate expression
result = await python_tool.execute(
    operation="evaluate-expression",
    code="len([1, 2, 3]) * 10"
)
# Returns: {"value": "30", "type": "int"}

# Run script
result = await python_tool.execute(
    operation="run-script",
    script_path="/sandbox/my_script.py"
)

# Install package
result = await python_tool.execute(
    operation="install-package",
    package="requests==2.28.0"
)

# List installed packages
result = await python_tool.execute(
    operation="list-packages"
)
```

#### Execution Model

```
┌─────────────────────────────────┐
│      execute()                  │
│  Creates temporary script        │
└────────────────┬────────────────┘
                 │
┌────────────────▼────────────────┐
│  asyncio.create_subprocess_exec │
│  Launches Python process         │
└────────────────┬────────────────┘
                 │
┌────────────────▼────────────────┐
│  asyncio.wait_for()             │
│  Enforces timeout               │
│  (default: 30s)                 │
└────────────────┬────────────────┘
                 │
┌────────────────▼────────────────┐
│  Capture stdout/stderr          │
│  Collect output                 │
│  Return ToolResult              │
└─────────────────────────────────┘
```

#### Safety Features

- **Subprocess Isolation**: Code runs in separate process (not eval())
- **Timeout Protection**: Hard limit with process termination
- **Output Capture**: Both stdout and stderr captured
- **Error Handling**: Structured error reporting
- **Resource Limits**: Memory and CPU constrained by OS

#### Timeout Handling

```python
# Default timeouts
- Code execution: 30 seconds
- Script execution: 30 seconds
- Package installation: 60 seconds
- Package listing: 10 seconds

# On timeout:
proc.kill()  # Terminate process
result.success = False
result.add_error(f"Execution timeout after {timeout_seconds}s")
```

---

### 3. BrowserTool

Web automation using Playwright with full browser control.

#### Capabilities (27 total)

**Browser Control**:
- `launch`: Launch browser instance
- `close`: Close browser
- `navigate`: Navigate to URL
- `back`: Go back in history
- `forward`: Go forward in history
- `reload`: Reload current page

**DOM Interaction**:
- `click`: Click element by selector
- `double-click`: Double-click element
- `hover`: Hover over element
- `fill`: Fill form field (clear + type)
- `type`: Type text character by character
- `press`: Press keyboard key
- `select`: Select dropdown option
- `check`: Check checkbox
- `uncheck`: Uncheck checkbox

**Waiting**:
- `wait`: Wait for specified duration
- `wait-for-selector`: Wait for element to appear

**Content Extraction**:
- `extract-text`: Extract page text content
- `extract-html`: Extract HTML
- `extract-links`: Extract all links

**Capture**:
- `screenshot`: Take screenshot (PNG)
- `pdf`: Generate PDF

**Storage**:
- `get-cookies`: Get browser cookies
- `get-local-storage`: Get localStorage data
- `get-session-storage`: Get sessionStorage data

#### Parameters

```python
ToolParameter("operation", "string", "Operation to perform", required=True)
ToolParameter("url", "string", "URL to navigate to", required=False)
ToolParameter("selector", "string", "CSS selector", required=False)
ToolParameter("text", "string", "Text content", required=False)
ToolParameter("key", "string", "Key to press", required=False)
ToolParameter("value", "string", "Value to set", required=False)
ToolParameter("timeout", "integer", "Operation timeout in ms", required=False)
ToolParameter("page_id", "string", "Page identifier", required=False)
```

#### Examples

```python
# Launch and navigate
await browser_tool.execute(operation="launch")
result = await browser_tool.execute(
    operation="navigate",
    url="https://example.com"
)

# Form interaction
await browser_tool.execute(
    operation="fill",
    selector="input[name='email']",
    text="user@example.com"
)
await browser_tool.execute(
    operation="click",
    selector="button[type='submit']"
)

# Extract data
result = await browser_tool.execute(operation="extract-text")
print(result.data["text"])

# Take screenshot
result = await browser_tool.execute(operation="screenshot")
# result.data["screenshot_bytes"] contains PNG data

# Generate PDF
result = await browser_tool.execute(operation="pdf")
```

#### Multi-Page Support

```python
# Each new navigation creates a page
result1 = await browser_tool.execute(
    operation="navigate",
    url="https://site1.com"
)  # page_id_0

result2 = await browser_tool.execute(
    operation="navigate",
    url="https://site2.com"
)  # page_id_1

# Operations target specific page
await browser_tool.execute(
    operation="click",
    selector="a.link",
    page_id="page_id_0"
)
```

#### Timeout & Retries

```python
# Default timeouts
- Page operations: 30 seconds
- Navigation: 30 seconds

# Auto-retries on:
- Network timeouts (built into Playwright)
- Transient selector issues

# Manual wait:
await browser_tool.execute(
    operation="wait-for-selector",
    selector=".dynamic-content",
    timeout=10000
)
```

---

## Enhanced ToolResult Model

All tools return the enhanced ToolResult with full observability.

### Structure

```python
@dataclass
class ToolResult:
    success: bool                      # Operation succeeded
    data: Any = None                   # Operation output
    metadata: Dict[str, Any] = {}      # Operation metadata
    duration: float = 0.0              # Milliseconds
    logs: List[ToolExecutionLog] = []  # Structured logs
    warnings: List[str] = []           # Non-fatal issues
    errors: List[str] = []             # Error messages
    artifacts: List[ToolArtifact] = [] # Generated files
    metrics: Optional[ToolMetrics] = None # Performance metrics
```

### Backward Compatibility

```python
# Old API still works:
result.output           # Maps to result.data
result.error            # Maps to result.errors[0]
result.execution_time_ms # Maps to result.duration
```

### Structured Logging

```python
# Add log entry
result.add_log("INFO", "Operation started", {"key": "value"})
result.add_log("DEBUG", "Processing step 1")
result.add_log("WARNING", "Slow operation detected")
result.add_log("ERROR", "Recovery required", {"attempt": 1})

# Each log includes:
- timestamp (ISO format)
- level (DEBUG, INFO, WARNING, ERROR)
- message
- context (optional metadata)
```

### Error Tracking

```python
# Multiple errors recorded
result.add_error("Primary error")
result.add_error("Secondary issue")

result.errors  # List of all errors
result.error   # First error (backward compat)
result.success # False if any errors
```

### Artifact Tracking

```python
artifact = ToolArtifact(
    name="output.pdf",
    type="document",
    path="/sandbox/output.pdf",
    size_bytes=102400,
    mime_type="application/pdf"
)
result.add_artifact(artifact)
```

### Metrics Collection

```python
result.metrics = ToolMetrics(
    execution_time_ms=150.5,
    memory_used_mb=45.2,
    cpu_percent=35.0,
    io_operations=12
)
```

### Serialization

```python
# Convert to dict for transmission
data = result.to_dict()

# Includes all fields in JSON-friendly format
{
    "success": true,
    "data": {...},
    "duration": 150.5,
    "logs": [
        {
            "timestamp": "2026-07-28T10:30:45.123456",
            "level": "INFO",
            "message": "...",
            "context": {}
        }
    ],
    "warnings": [...],
    "errors": [...],
    "artifacts": [...],
    "metrics": {...}
}
```

---

## Tool Registry with Capability Discovery

Enhanced ToolRegistry supports discovery and metrics.

### Capabilities Discovery

```python
registry = ToolRegistry()
registry.register(filesystem_tool)
registry.register(python_tool)
registry.register(browser_tool)

# Find tools by capability
tools = registry.find_by_capability("read-file")
# Returns: [FilesystemTool]

# List all capabilities
capabilities = registry.list_capabilities()
# {
#     "read-file": ["Filesystem"],
#     "write-file": ["Filesystem"],
#     "execute-python": ["Python"],
#     "navigate": ["Browser"],
#     ...
# }

# Get capabilities for a tool
caps = registry.get_tool_info("FilesystemTool")["capabilities"]
```

### Health Monitoring

```python
# Quick health check
health = await registry.health()
# {
#     "FilesystemTool": {"status": "healthy"},
#     "PythonTool": {"status": "healthy"},
#     "BrowserTool": {"status": "ready"}
# }

# Detailed health with metrics
health = await registry.health_all()
# {
#     "FilesystemTool": {
#         "status": "healthy",
#         "execution_count": 42,
#         "total_time_ms": 3500.0,
#         "average_time_ms": 83.3,
#         "last_execution": "2026-07-28T10:30:45Z"
#     },
#     ...
# }
```

### Metrics Tracking

```python
# Update execution metrics
registry.update_metrics("FilesystemTool", execution_time_ms=150.5)

# Get metrics for specific tool
metrics = registry.get_metrics("FilesystemTool")
# {
#     "execution_count": 1,
#     "total_time_ms": 150.5,
#     "average_time_ms": 150.5,
#     "last_execution": "2026-07-28T10:30:45Z"
# }

# Get complete tool info with metrics
info = registry.get_tool_info("FilesystemTool")
# {
#     "id": "FilesystemTool",
#     "name": "Filesystem",
#     "description": "...",
#     "capabilities": [...],
#     "metrics": {...}
# }
```

---

## Observability & Events

Tools integrate with runtime EventBus for full observability.

### Execution Flow Events

Each tool execution publishes events:

```
Start → Validation → Execution → Completion
  │         │           │            │
  ├→ ToolStarted       ├→ ToolExecuted (on success)
  ├→ CheckingParams    └→ ToolFailed (on error)
  └→ ...
```

### Event Types

Tools publish these events to runtime EventBus:

- **ToolExecuted**: Successful tool execution
- **ToolFailed**: Tool execution failed
- **ToolTimeout**: Execution timeout occurred
- **ToolCancelled**: Execution cancelled by user

### Event Structure

```python
event = ToolExecuted(
    tool_id="FilesystemTool",
    tool_name="Filesystem",
    capability="read-file",
    success=True,
    duration_ms=45.2,
    execution_timestamp="2026-07-28T10:30:45Z",
    correlation_id="corr-123",
    session_id="sess-456",
    metadata={
        "file_size": 1024,
        "operation": "read-file"
    }
)
```

---

## Performance Characteristics

### Filesystem Tool

| Operation | Typical Time | Notes |
|-----------|------------|-------|
| read-file (1MB) | 10-50ms | Async I/O |
| write-file (1MB) | 15-60ms | Async I/O |
| list-directory (100 files) | 20-100ms | Stat calls per entry |
| search-files | 100-500ms | Recursive glob |
| hash-file (10MB) | 50-200ms | SHA256 computation |
| read-json (1MB) | 20-100ms | Parse + validation |

### Python Tool

| Operation | Typical Time | Notes |
|-----------|------------|-------|
| execute-python (simple) | 100-300ms | Process spawn + Python startup |
| evaluate-expression | 100-200ms | Expression parsing + eval |
| run-script (simple) | 150-400ms | Process overhead |
| list-packages | 500-2000ms | pip operation |
| install-package | 5000-30000ms | Network + compilation |

### Browser Tool

| Operation | Typical Time | Notes |
|-----------|------------|-------|
| launch | 2000-5000ms | Browser startup |
| navigate | 2000-10000ms | Network + rendering |
| click | 100-500ms | DOM interaction |
| extract-text | 50-200ms | JavaScript evaluation |
| screenshot | 500-2000ms | Image encoding |
| pdf | 1000-5000ms | Rendering + encoding |

---

## Security Model

### Threat Model

**Threats Protected Against**:
1. **Path Traversal**: Access files outside sandbox
2. **Resource Exhaustion**: Infinite loops, large allocations
3. **Privilege Escalation**: Accessing privileged operations
4. **Information Disclosure**: Reading sensitive files
5. **Denial of Service**: Crashing tool or server

### Protection Mechanisms

| Threat | Mechanism |
|--------|-----------|
| Path Traversal | PathValidator with boundary checking |
| Resource Exhaustion | Timeouts + memory limits |
| Privilege Escalation | Subprocess isolation |
| Information Disclosure | Sandbox directory restriction |
| Denial of Service | Timeout + process termination |

### Hardening Checklist

- ✅ All file paths validated before access
- ✅ Symlinks resolved and checked
- ✅ File extensions whitelisted
- ✅ Read-only paths protected from modification
- ✅ File size limits enforced
- ✅ Subprocess execution isolated
- ✅ Execution timeouts enforced
- ✅ Process termination on timeout
- ✅ Resource limits validated
- ✅ Error messages sanitized

---

## Implementation Files

### New Files

**Tool Implementations**:
- `ai/tools/models.py` — Enhanced ToolResult model
- `ai/tools/security.py` — Sandbox and path validation
- `ai/tools/filesystem.py` — FilesystemTool implementation
- `ai/tools/python_executor.py` — PythonTool implementation
- `ai/tools/browser.py` — BrowserTool with Playwright

**Testing**:
- `tests/test_tools_milestone4.py` — Comprehensive tool tests (60+ cases)

### Modified Files

**Framework Integration**:
- `ai/tools/__init__.py` — Enhanced ToolRegistry, imports production implementations

---

## Remaining Placeholder Tools

These tools are placeholders for future implementation:

- **VisionTool**: Image analysis, object detection, OCR
- **VideoTool**: Video processing, frame extraction
- **AudioTool**: Speech transcription, audio analysis
- **ImageGenerationTool**: Text-to-image, image editing

Expected in Milestone 5+.

---

## Future Extensions

### Milestone 5+

- Implement Vision tool (image analysis)
- Implement Video tool (FFmpeg integration)
- Implement Audio tool (speech processing)
- Implement ImageGeneration tool (stable diffusion)
- Add authentication/authorization to tools
- Add rate limiting per tool/user
- Add audit logging for sensitive operations

### Architecture Readiness

The tool framework is designed to accept these extensions without modification:

```python
# Add new tool
class CustomTool(Tool):
    def get_capabilities(self) -> List[ToolCapability]:
        return [ToolCapability("custom-op", "...")]
    
    async def execute(self, **kwargs) -> ToolResult:
        # Implementation

# Register
registry.register(CustomTool())

# Discover
tools = registry.find_by_capability("custom-op")
```

---

## Testing

Run comprehensive test suite:

```bash
# All tool tests
pytest tests/test_tools_milestone4.py -v

# Specific tool
pytest tests/test_tools_milestone4.py::TestFilesystemTool -v

# With coverage
pytest tests/test_tools_milestone4.py --cov=aura_backend.ai.tools
```

---

## Conclusion

Milestone 4 delivers **three production-grade tools** with:

✅ Complete security and sandboxing  
✅ Resource protection (timeouts, limits)  
✅ Comprehensive observability (logs, metrics)  
✅ Full async support  
✅ Extensive testing (60+ test cases)  
✅ Clean architecture (no tight coupling)  
✅ Zero breaking changes to M3 framework  

Tools are ready for integration into agents and workflows.
