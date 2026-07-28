"""
Prompt system for rendering and managing prompts.

Supports templating and versioning for future prompt management.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class PromptVariable:
    """Variable in a prompt template"""

    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None


@dataclass
class PromptTemplate:
    """Prompt template with variables"""

    id: str
    name: str
    template: str
    description: str
    variables: List[PromptVariable] = field(default_factory=list)
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate_variables(self, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate provided variables"""
        errors = {}
        for var in self.variables:
            if var.required and var.name not in values:
                errors[var.name] = f"Missing required variable: {var.name}"
        return errors


@dataclass
class PromptVersion:
    """Versioned prompt"""

    template_id: str
    version: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    changes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class PromptLibrary:
    """Library of prompt templates"""

    def __init__(self):
        self._templates: Dict[str, PromptTemplate] = {}
        self._versions: Dict[str, List[PromptVersion]] = {}

    def register_template(self, template: PromptTemplate) -> None:
        """Register a prompt template"""
        self._templates[template.id] = template
        if template.id not in self._versions:
            self._versions[template.id] = []

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get template by ID"""
        return self._templates.get(template_id)

    def list_templates(self) -> List[PromptTemplate]:
        """List all templates"""
        return list(self._templates.values())

    def add_version(self, version: PromptVersion) -> None:
        """Add a new version of a template"""
        if version.template_id not in self._versions:
            self._versions[version.template_id] = []
        self._versions[version.template_id].append(version)

    def get_versions(self, template_id: str) -> List[PromptVersion]:
        """Get all versions of a template"""
        return self._versions.get(template_id, []).copy()

    def get_version(self, template_id: str, version: str) -> Optional[PromptVersion]:
        """Get specific version"""
        versions = self.get_versions(template_id)
        for v in versions:
            if v.version == version:
                return v
        return None


@dataclass
class PromptVariables:
    """Prompt variables for rendering"""

    variables: Dict[str, Any] = field(default_factory=dict)

    def set(self, key: str, value: Any) -> None:
        """Set a variable"""
        self.variables[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a variable"""
        return self.variables.get(key, default)

    def merge(self, other: PromptVariables) -> PromptVariables:
        """Merge with another variables object"""
        merged = PromptVariables()
        merged.variables = {**self.variables, **other.variables}
        return merged

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.variables.copy()
