"""Plugin SDK & Marketplace models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from studio_api.database.base import Base


class Plugin(Base):
    """Plugin registry and metadata."""

    __tablename__ = "plugins"

    id = Column(String(100), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    author = Column(String(255), nullable=False)
    author_url = Column(String(500), nullable=True)
    license = Column(String(50), default="MIT")
    repository_url = Column(String(500), nullable=True)
    documentation_url = Column(String(500), nullable=True)
    status = Column(String(50), default="published")  # draft, published, deprecated
    icon_url = Column(String(500), nullable=True)
    manifest = Column(Text, nullable=False)  # JSON
    api_types = Column(Text, nullable=False)  # JSON list
    permissions = Column(Text, nullable=False)  # JSON list
    settings_schema = Column(Text, nullable=True)  # JSON schema
    sandbox_enabled = Column(String(20), default="enabled")  # enabled, disabled
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class PluginInstallation(Base):
    """Plugin installation per project/user."""

    __tablename__ = "plugin_installations"

    id = Column(String(36), primary_key=True, index=True)
    plugin_id = Column(String(100), ForeignKey("plugins.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    version_installed = Column(String(20), nullable=False)
    status = Column(String(50), default="installed")  # installed, enabled, disabled, uninstalled
    auto_update = Column(String(20), default="enabled")
    settings = Column(Text, nullable=True)  # JSON
    installed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    enabled_at = Column(DateTime, nullable=True)
    disabled_at = Column(DateTime, nullable=True)


class PluginPermission(Base):
    """Plugin permission grants."""

    __tablename__ = "plugin_permissions"

    id = Column(String(36), primary_key=True, index=True)
    plugin_installation_id = Column(
        String(36), ForeignKey("plugin_installations.id"),
        nullable=False, index=True
    )
    permission = Column(String(100), nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PluginAPI(Base):
    """Registered plugin API extensions."""

    __tablename__ = "plugin_apis"

    id = Column(String(36), primary_key=True, index=True)
    plugin_id = Column(String(100), ForeignKey("plugins.id"), nullable=False, index=True)
    api_type = Column(String(50), nullable=False)  # timeline_tool, ai_model, render_filter, etc.
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    endpoint = Column(String(500), nullable=False)
    method = Column(String(20), default="POST")  # GET, POST, PUT
    version = Column(String(20), default="1.0.0")
    enabled = Column(String(20), default="enabled")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PluginMarketplaceEntry(Base):
    """Plugin marketplace metadata."""

    __tablename__ = "plugin_marketplace"

    id = Column(String(36), primary_key=True, index=True)
    plugin_id = Column(String(100), ForeignKey("plugins.id"), nullable=False, unique=True, index=True)
    downloads = Column(Integer, default=0)
    average_rating = Column(Float, default=5.0)
    total_ratings = Column(Integer, default=0)
    featured = Column(String(20), default="no")
    category = Column(String(50), nullable=True)  # video_editing, ai_models, publishing
    tags = Column(Text, nullable=True)  # JSON list
    changelog = Column(Text, nullable=True)
    verified = Column(String(20), default="no")  # no, pending, verified
    verified_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class PluginRating(Base):
    """Plugin ratings and reviews."""

    __tablename__ = "plugin_ratings"

    id = Column(String(36), primary_key=True, index=True)
    plugin_id = Column(String(100), ForeignKey("plugins.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-5
    title = Column(String(255), nullable=True)
    review = Column(Text, nullable=True)
    helpful_count = Column(Integer, default=0)
    unhelpful_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class PluginSettings(Base):
    """Plugin instance settings per installation."""

    __tablename__ = "plugin_settings"

    id = Column(String(36), primary_key=True, index=True)
    plugin_installation_id = Column(
        String(36), ForeignKey("plugin_installations.id"),
        nullable=False, index=True
    )
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class PluginOAuth(Base):
    """OAuth credentials for plugins."""

    __tablename__ = "plugin_oauth"

    id = Column(String(36), primary_key=True, index=True)
    plugin_installation_id = Column(
        String(36), ForeignKey("plugin_installations.id"),
        nullable=False, index=True
    )
    provider = Column(String(100), nullable=False)  # github, google, custom
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    scope = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
