"""Plugin SDK & Marketplace service."""

import json
from datetime import datetime
from typing import Optional

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from studio_api.models.plugin import (
    Plugin,
    PluginAPI,
    PluginInstallation,
    PluginMarketplaceEntry,
    PluginOAuth,
    PluginPermission,
    PluginRating,
    PluginSettings,
)


class PluginService:
    """Plugin SDK and Marketplace service."""

    async def register_plugin(
        self,
        db: AsyncSession,
        plugin_id: str,
        name: str,
        version: str,
        description: str,
        author: str,
        permissions: list[str],
        api_types: list[str],
        manifest: dict,
        author_url: Optional[str] = None,
        license: str = "MIT",
        repository_url: Optional[str] = None,
        documentation_url: Optional[str] = None,
        icon_url: Optional[str] = None,
        settings_schema: Optional[dict] = None,
    ) -> Plugin:
        """Register a new plugin."""
        plugin = Plugin(
            id=plugin_id,
            name=name,
            version=version,
            description=description,
            author=author,
            author_url=author_url,
            license=license,
            repository_url=repository_url,
            documentation_url=documentation_url,
            icon_url=icon_url,
            manifest=json.dumps(manifest),
            api_types=json.dumps(api_types),
            permissions=json.dumps(permissions),
            settings_schema=json.dumps(settings_schema) if settings_schema else None,
        )
        db.add(plugin)
        await db.commit()
        await db.refresh(plugin)

        # Create marketplace entry
        marketplace = PluginMarketplaceEntry(
            id=f"mkt_{plugin_id}",
            plugin_id=plugin_id,
        )
        db.add(marketplace)
        await db.commit()

        return plugin

    async def get_plugin(self, db: AsyncSession, plugin_id: str) -> Optional[Plugin]:
        """Get plugin by ID."""
        query = select(Plugin).where(Plugin.id == plugin_id)
        result = await db.execute(query)
        return result.scalar()

    async def list_plugins(
        self,
        db: AsyncSession,
        status: str = "published",
        limit: int = 50,
    ) -> list[Plugin]:
        """List plugins with status filter."""
        query = (
            select(Plugin)
            .where(Plugin.status == status)
            .order_by(desc(Plugin.updated_at))
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def install_plugin(
        self,
        db: AsyncSession,
        plugin_id: str,
        project_id: str,
        version: Optional[str] = None,
        auto_update: bool = True,
    ) -> PluginInstallation:
        """Install plugin to project."""
        plugin = await self.get_plugin(db, plugin_id)
        if not plugin:
            raise ValueError(f"Plugin {plugin_id} not found")

        version_to_install = version or plugin.version

        installation = PluginInstallation(
            id=f"inst_{plugin_id}_{project_id}",
            plugin_id=plugin_id,
            project_id=project_id,
            version_installed=version_to_install,
            auto_update="enabled" if auto_update else "disabled",
        )
        db.add(installation)

        # Grant permissions
        permissions = json.loads(plugin.permissions)
        for perm in permissions:
            permission = PluginPermission(
                id=f"perm_{plugin_id}_{project_id}_{perm}",
                plugin_installation_id=installation.id,
                permission=perm,
            )
            db.add(permission)

        # Update marketplace downloads
        marketplace = select(PluginMarketplaceEntry).where(
            PluginMarketplaceEntry.plugin_id == plugin_id
        )
        result = await db.execute(marketplace)
        entry = result.scalar()
        if entry:
            entry.downloads += 1

        await db.commit()
        await db.refresh(installation)
        return installation

    async def uninstall_plugin(
        self,
        db: AsyncSession,
        plugin_id: str,
        project_id: str,
    ) -> PluginInstallation:
        """Uninstall plugin from project."""
        query = select(PluginInstallation).where(
            and_(
                PluginInstallation.plugin_id == plugin_id,
                PluginInstallation.project_id == project_id,
            )
        )
        result = await db.execute(query)
        installation = result.scalar()

        if installation:
            installation.status = "uninstalled"
            await db.commit()
            await db.refresh(installation)

        return installation

    async def enable_plugin(
        self,
        db: AsyncSession,
        plugin_id: str,
        project_id: str,
    ) -> PluginInstallation:
        """Enable plugin."""
        query = select(PluginInstallation).where(
            and_(
                PluginInstallation.plugin_id == plugin_id,
                PluginInstallation.project_id == project_id,
            )
        )
        result = await db.execute(query)
        installation = result.scalar()

        if installation:
            installation.status = "enabled"
            installation.enabled_at = datetime.utcnow()
            await db.commit()
            await db.refresh(installation)

        return installation

    async def disable_plugin(
        self,
        db: AsyncSession,
        plugin_id: str,
        project_id: str,
    ) -> PluginInstallation:
        """Disable plugin."""
        query = select(PluginInstallation).where(
            and_(
                PluginInstallation.plugin_id == plugin_id,
                PluginInstallation.project_id == project_id,
            )
        )
        result = await db.execute(query)
        installation = result.scalar()

        if installation:
            installation.status = "disabled"
            installation.disabled_at = datetime.utcnow()
            await db.commit()
            await db.refresh(installation)

        return installation

    async def register_plugin_api(
        self,
        db: AsyncSession,
        plugin_id: str,
        api_type: str,
        name: str,
        description: str,
        endpoint: str,
        method: str = "POST",
        version: str = "1.0.0",
    ) -> PluginAPI:
        """Register plugin API extension."""
        api = PluginAPI(
            id=f"api_{plugin_id}_{api_type}",
            plugin_id=plugin_id,
            api_type=api_type,
            name=name,
            description=description,
            endpoint=endpoint,
            method=method,
            version=version,
        )
        db.add(api)
        await db.commit()
        await db.refresh(api)
        return api

    async def get_plugin_apis(
        self,
        db: AsyncSession,
        plugin_id: str,
    ) -> list[PluginAPI]:
        """Get plugin APIs."""
        query = select(PluginAPI).where(PluginAPI.plugin_id == plugin_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_apis_by_type(
        self,
        db: AsyncSession,
        api_type: str,
    ) -> list[PluginAPI]:
        """Get all APIs of a specific type."""
        query = select(PluginAPI).where(
            and_(PluginAPI.api_type == api_type, PluginAPI.enabled == "enabled")
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def update_plugin_settings(
        self,
        db: AsyncSession,
        plugin_installation_id: str,
        settings: dict,
    ) -> PluginInstallation:
        """Update plugin settings."""
        query = select(PluginInstallation).where(
            PluginInstallation.id == plugin_installation_id
        )
        result = await db.execute(query)
        installation = result.scalar()

        if installation:
            installation.settings = json.dumps(settings)
            await db.commit()
            await db.refresh(installation)

        return installation

    async def rate_plugin(
        self,
        db: AsyncSession,
        plugin_id: str,
        project_id: str,
        rating: int,
        title: Optional[str] = None,
        review: Optional[str] = None,
    ) -> PluginRating:
        """Rate plugin."""
        # Check for existing rating
        query = select(PluginRating).where(
            and_(
                PluginRating.plugin_id == plugin_id,
                PluginRating.project_id == project_id,
            )
        )
        result = await db.execute(query)
        existing = result.scalar()

        if existing:
            existing.rating = rating
            existing.title = title
            existing.review = review
            existing.updated_at = datetime.utcnow()
            rating_obj = existing
        else:
            rating_obj = PluginRating(
                id=f"rate_{plugin_id}_{project_id}",
                plugin_id=plugin_id,
                project_id=project_id,
                rating=rating,
                title=title,
                review=review,
            )
            db.add(rating_obj)

        # Update marketplace average
        all_ratings = select(PluginRating).where(
            PluginRating.plugin_id == plugin_id
        )
        result = await db.execute(all_ratings)
        ratings = result.scalars().all()

        if ratings:
            avg = sum(r.rating for r in ratings) / len(ratings)
            marketplace = select(PluginMarketplaceEntry).where(
                PluginMarketplaceEntry.plugin_id == plugin_id
            )
            result = await db.execute(marketplace)
            entry = result.scalar()
            if entry:
                entry.average_rating = avg
                entry.total_ratings = len(ratings)

        await db.commit()
        await db.refresh(rating_obj)
        return rating_obj

    async def get_marketplace_entries(
        self,
        db: AsyncSession,
        category: Optional[str] = None,
        limit: int = 50,
    ) -> list[PluginMarketplaceEntry]:
        """Get marketplace entries."""
        query = select(PluginMarketplaceEntry).order_by(
            desc(PluginMarketplaceEntry.downloads)
        )

        if category:
            query = query.where(PluginMarketplaceEntry.category == category)

        query = query.limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def add_oauth_credential(
        self,
        db: AsyncSession,
        plugin_installation_id: str,
        provider: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> PluginOAuth:
        """Store OAuth credentials for plugin."""
        oauth = PluginOAuth(
            id=f"oauth_{plugin_installation_id}_{provider}",
            plugin_installation_id=plugin_installation_id,
            provider=provider,
            access_token=access_token,
            refresh_token=refresh_token,
            scope=scope,
        )
        db.add(oauth)
        await db.commit()
        await db.refresh(oauth)
        return oauth

    async def get_plugin_installations(
        self,
        db: AsyncSession,
        project_id: str,
    ) -> list[PluginInstallation]:
        """Get all plugin installations for a project."""
        query = (
            select(PluginInstallation)
            .where(PluginInstallation.project_id == project_id)
            .order_by(desc(PluginInstallation.installed_at))
        )
        result = await db.execute(query)
        return result.scalars().all()
