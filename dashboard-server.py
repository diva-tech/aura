#!/usr/bin/env python3
"""
Standalone AURA Dashboard Server

Serves the web dashboard without requiring the full backend to be running.
Perfect for demonstrating the AURA platform.

Usage:
    python3 dashboard-server.py

Then open: http://localhost:8000
"""

import json
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse


class AuraDashboardHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for AURA dashboard"""

    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path

        # Serve dashboard HTML
        if path == "/" or path == "/dashboard":
            self.serve_dashboard()
            return

        # API endpoints for dashboard data
        if path == "/api/dashboard":
            self.serve_json(self.get_dashboard())
            return
        if path == "/api/architecture":
            self.serve_json(self.get_architecture())
            return
        if path == "/api/milestones":
            self.serve_json(self.get_milestones())
            return
        if path == "/api/providers":
            self.serve_json(self.get_providers())
            return
        if path == "/api/agents":
            self.serve_json(self.get_agents())
            return
        if path == "/api/learning":
            self.serve_json(self.get_learning())
            return
        if path == "/api/publishing":
            self.serve_json(self.get_publishing())
            return

        # 404
        self.send_response(404)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Not Found")

    def serve_dashboard(self):
        """Serve the dashboard HTML"""
        dashboard_path = Path(__file__).parent / "apps/backend/static/index.html"
        if dashboard_path.exists():
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(dashboard_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Dashboard not found")

    def serve_json(self, data):
        """Serve JSON response"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def get_dashboard(self):
        """Get dashboard summary"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "platform": {
                "name": "AURA v1.0",
                "version": "1.0.0",
                "status": "running",
            },
            "metrics": {
                "jobs_completed": 1,
                "jobs_active": 0,
                "jobs_failed": 0,
                "recommendations_generated": 12,
                "providers_healthy": 11,
                "agents_active": 15,
            },
            "recent_activity": [
                {
                    "type": "job_completed",
                    "timestamp": "2026-07-30T10:05:00Z",
                    "description": "Learning optimization completed",
                },
            ],
        }

    def get_architecture(self):
        """Get system architecture"""
        return {
            "layers": [
                {
                    "name": "Learning System",
                    "milestone": "M14",
                    "phases": 4,
                    "components": [
                        "Learning Foundation",
                        "Analytics Providers",
                        "Learning Orchestration",
                        "Production Readiness",
                    ],
                },
                {
                    "name": "Production Systems",
                    "milestones": ["M12", "M13"],
                    "components": ["Rendering Engine", "Publishing Platform"],
                },
                {
                    "name": "Domain Intelligence",
                    "milestones": ["M9", "M10", "M11"],
                    "components": ["Video Intelligence", "Content Intelligence", "Intelligent Editing"],
                },
                {
                    "name": "Intelligence Engines",
                    "milestones": ["M5", "M6", "M7", "M8"],
                    "components": ["LLM Runtime", "Agent Runtime", "Memory Platform", "Task Orchestration"],
                },
                {
                    "name": "AI & Tool Frameworks",
                    "milestones": ["M3", "M4", "M4.5"],
                    "components": ["AI Framework", "Tool Platform"],
                },
                {
                    "name": "Runtime Infrastructure",
                    "milestones": ["M2", "M2.5"],
                    "components": ["Event Bus", "Plugin System", "Service Container"],
                },
                {
                    "name": "Foundation",
                    "milestone": "M1",
                    "components": ["Core Abstractions", "Type System", "Plugin Architecture"],
                },
            ],
            "pattern": "Planner → DAG → M8 → M6 → Provider",
            "key_characteristics": [
                "Immutable Domain Models",
                "Provider Abstraction",
                "Stateless Agents",
                "Event Sourcing",
                "DAG-Based Orchestration",
                "Capability Negotiation",
            ],
        }

    def get_milestones(self):
        """Get all milestones"""
        milestones = {
            "M1": {"name": "Foundation", "status": "complete", "components": 5},
            "M2": {"name": "Runtime", "status": "complete", "components": 4},
            "M2.5": {"name": "Runtime Hardening", "status": "complete", "components": 3},
            "M3": {"name": "AI Framework", "status": "complete", "components": 3},
            "M4": {"name": "Tool Platform", "status": "complete", "components": 4},
            "M4.5": {"name": "Tool Platform Hardening", "status": "complete", "components": 2},
            "M5": {"name": "LLM Runtime", "status": "complete", "components": 3},
            "M6": {"name": "Agent Runtime", "status": "complete", "components": 20},
            "M7": {"name": "Memory Platform", "status": "complete", "components": 5},
            "M8": {"name": "Task Orchestration", "status": "complete", "components": 4},
            "M9": {"name": "Video Intelligence", "status": "complete", "components": 5},
            "M10": {"name": "Content Intelligence", "status": "complete", "components": 4},
            "M11": {"name": "Intelligent Editing", "status": "complete", "components": 3},
            "M12": {"name": "Rendering Engine", "status": "complete", "components": 4},
            "M13": {"name": "Publishing Platform", "status": "complete", "components": 6},
            "M14": {
                "name": "Learning Engine",
                "status": "complete",
                "phases": 4,
                "components": 50,
            },
        }
        return {
            "total": len(milestones),
            "completed": len(milestones),
            "milestones": milestones,
        }

    def get_providers(self):
        """Get all providers"""
        return {
            "rendering": [
                {"name": "GPU Renderer", "status": "available", "capabilities": ["4K", "HDR", "GPU-accelerated"]},
                {"name": "Software Renderer", "status": "available", "capabilities": ["CPU rendering", "Quality"]},
            ],
            "publishing": [
                {"name": "YouTube Publisher", "status": "available", "platforms": ["YouTube"], "capabilities": ["Batch", "Scheduling"]},
                {"name": "TikTok Publisher", "status": "available", "platforms": ["TikTok"], "capabilities": ["Batch"]},
                {"name": "Instagram Publisher", "status": "available", "platforms": ["Instagram"], "capabilities": ["Batch", "Stories"]},
                {"name": "LinkedIn Publisher", "status": "available", "platforms": ["LinkedIn"], "capabilities": ["Batch"]},
                {"name": "Podcast Publisher", "status": "available", "platforms": ["Podcast"], "capabilities": ["Distribution"]},
            ],
            "analytics": [
                {
                    "name": "YouTube Analytics",
                    "status": "available",
                    "capabilities": ["Video Metrics", "Retention", "Revenue"],
                    "lookback_days": 365,
                },
                {
                    "name": "TikTok Analytics",
                    "status": "available",
                    "capabilities": ["Revenue", "Demographics"],
                    "lookback_days": 30,
                },
                {
                    "name": "Instagram Analytics",
                    "status": "available",
                    "capabilities": ["Revenue", "Demographics"],
                    "lookback_days": 90,
                },
                {
                    "name": "LinkedIn Analytics",
                    "status": "available",
                    "capabilities": ["Demographics", "Engagement"],
                    "lookback_days": 180,
                },
                {
                    "name": "Podcast Analytics",
                    "status": "available",
                    "capabilities": ["Revenue", "Demographics"],
                    "lookback_days": 365,
                },
                {"name": "Mock Analytics", "status": "available", "capabilities": ["All"], "lookback_days": 365},
            ],
        }

    def get_agents(self):
        """Get all M6 agents"""
        return {
            "total": 20,
            "by_milestone": {
                "M6": [
                    {"id": "agent:research", "name": "Research Agent", "status": "active"},
                    {"id": "agent:planning", "name": "Planning Agent", "status": "active"},
                    {"id": "agent:execution", "name": "Execution Agent", "status": "active"},
                    {"id": "agent:validation", "name": "Validation Agent", "status": "active"},
                ],
                "M9": [
                    {"id": "agent:video_analysis", "name": "Video Analysis Agent", "status": "active"},
                ],
                "M14": [
                    {"id": "agent:validation", "name": "Learning Validator", "status": "active"},
                    {"id": "agent:auth", "name": "Authentication Agent", "status": "active"},
                    {"id": "agent:metrics", "name": "Metrics Retrieval Agent", "status": "active"},
                    {"id": "agent:analysis", "name": "Analysis Agent", "status": "active"},
                    {"id": "agent:recommendations", "name": "Recommendations Agent", "status": "active"},
                    {"id": "agent:profile", "name": "Profile Update Agent", "status": "active"},
                    {"id": "agent:memory", "name": "Memory Update Agent", "status": "active"},
                ],
            },
        }

    def get_learning(self):
        """Get learning system status"""
        return {
            "phases": {
                "Phase 1": {
                    "name": "Learning Foundation",
                    "status": "complete",
                    "models": 22,
                    "components": ["LearningJob", "LearningTask", "CreatorProfile", "AudienceProfile"],
                },
                "Phase 2": {
                    "name": "Analytics Providers",
                    "status": "complete",
                    "providers": 6,
                    "capabilities": ["video_metrics", "retention", "audience", "revenue", "ctr"],
                },
                "Phase 3": {
                    "name": "Learning Orchestration",
                    "status": "complete",
                    "agents": 7,
                    "stages": 10,
                },
                "Phase 4": {
                    "name": "Production Readiness",
                    "status": "complete",
                    "features": ["Dashboard", "Metrics", "Optimization"],
                },
            },
            "recommendations_pending": 0,
            "creators_tracked": 0,
        }

    def get_publishing(self):
        """Get publishing platform status"""
        return {
            "status": "ready",
            "platforms": [
                {
                    "name": "YouTube",
                    "status": "connected",
                    "videos_published": 0,
                    "capabilities": ["Videos", "Shorts", "Scheduling"],
                },
                {
                    "name": "TikTok",
                    "status": "connected",
                    "videos_published": 0,
                    "capabilities": ["Videos", "Duets"],
                },
                {
                    "name": "Instagram",
                    "status": "connected",
                    "videos_published": 0,
                    "capabilities": ["Reels", "Stories", "Feed"],
                },
                {
                    "name": "LinkedIn",
                    "status": "connected",
                    "videos_published": 0,
                    "capabilities": ["Videos", "Articles"],
                },
                {
                    "name": "Podcast",
                    "status": "connected",
                    "episodes_published": 0,
                    "capabilities": ["Distribution", "Scheduling"],
                },
            ],
            "pending_publishes": 0,
        }

    def log_message(self, format, *args):
        """Suppress default logging"""
        if "GET" in format or "POST" in format:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")


def run_server():
    """Run the dashboard server"""
    host = "0.0.0.0"
    port = 8000
    server_address = (host, port)
    httpd = HTTPServer(server_address, AuraDashboardHandler)

    print("=" * 60)
    print("🚀 AURA v1.0 Dashboard Server")
    print("=" * 60)
    print(f"🌐 Dashboard: http://localhost:{port}")
    print(f"📚 API: http://localhost:{port}/api")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard server stopped")


if __name__ == "__main__":
    run_server()
