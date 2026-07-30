"""API endpoint tests."""

import pytest
from fastapi.testclient import TestClient

from studio_api.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_project():
    """Test creating a project."""
    response = client.post(
        "/api/projects",
        json={
            "name": "Test Project",
            "description": "Test Description",
            "target_platform": "YouTube",
            "language": "en",
            "aspect_ratio": "16:9",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["status"] == "draft"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_projects():
    """Test listing projects."""
    # Create a project first
    client.post(
        "/api/projects",
        json={
            "name": "Test Project",
            "description": "Test",
            "target_platform": "YouTube",
        },
    )

    response = client.get("/api/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_project():
    """Test getting a project."""
    # Create a project
    create_response = client.post(
        "/api/projects",
        json={
            "name": "Test Project",
            "description": "Test",
            "target_platform": "YouTube",
        },
    )
    project_id = create_response.json()["id"]

    # Get the project
    response = client.get(f"/api/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Test Project"


@pytest.mark.asyncio
async def test_delete_project():
    """Test deleting a project."""
    # Create a project
    create_response = client.post(
        "/api/projects",
        json={
            "name": "Test Project",
            "description": "Test",
            "target_platform": "YouTube",
        },
    )
    project_id = create_response.json()["id"]

    # Delete the project
    response = client.delete(f"/api/projects/{project_id}")
    assert response.status_code == 204

    # Verify it's deleted
    response = client.get(f"/api/projects/{project_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_analyze_project():
    """Test queuing project for analysis."""
    # Create a project
    create_response = client.post(
        "/api/projects",
        json={
            "name": "Test Project",
            "description": "Test",
            "target_platform": "YouTube",
        },
    )
    project_id = create_response.json()["id"]

    # Queue for analysis
    response = client.post(f"/api/projects/{project_id}/analyze")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"


def test_project_not_found():
    """Test getting non-existent project."""
    response = client.get("/api/projects/non-existent-id")
    assert response.status_code == 404
