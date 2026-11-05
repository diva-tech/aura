"""M13 Phase 4 Tests: Production Readiness – Dashboard, Metrics, Optimization."""



from aura_backend.publishing import (  # Phase 4; Phase 1-3
    MetricsAggregator,
    PerformanceOptimizer,
    PlatformType,
    PublishingDashboard,
    PublishingJob,
)

# ============================================================================
# METRICS AGGREGATOR TESTS
# ============================================================================


class TestMetricsAggregator:
    """Test metrics aggregation"""

    def test_aggregator_creation(self):
        """Create metrics aggregator"""
        aggregator = MetricsAggregator()

        assert aggregator is not None

    def test_add_and_retrieve_metrics(self):
        """Add and retrieve metrics"""
        aggregator = MetricsAggregator()

        aggregator.add_metrics(
            {
                "provider": "mock",
                "upload_seconds": 10.0,
                "success": True,
                "retry_count": 0,
            }
        )

        throughput = aggregator.get_throughput_metrics()
        assert throughput.jobs_completed >= 1

    def test_failure_rate_calculation(self):
        """Calculate failure rate"""
        aggregator = MetricsAggregator()

        aggregator.add_metrics({"success": True})
        aggregator.add_metrics({"success": True})
        aggregator.add_metrics({"success": False})

        rate = aggregator.get_failure_rate()
        assert rate > 0

    def test_provider_metrics(self):
        """Get provider metrics"""
        aggregator = MetricsAggregator()

        aggregator.add_metrics(
            {
                "provider": "youtube",
                "upload_seconds": 15.0,
                "success": True,
            }
        )
        aggregator.add_metrics(
            {
                "provider": "youtube",
                "upload_seconds": 20.0,
                "success": True,
            }
        )

        metrics = aggregator.get_provider_metrics("youtube")

        assert metrics is not None
        assert metrics.total_jobs >= 2

    def test_retry_statistics(self):
        """Get retry statistics"""
        aggregator = MetricsAggregator()

        aggregator.add_metrics({"retry_count": 0})
        aggregator.add_metrics({"retry_count": 1})
        aggregator.add_metrics({"retry_count": 2})

        stats = aggregator.get_retry_statistics()

        assert stats["avg"] > 0
        assert stats["max"] >= 2


# ============================================================================
# DASHBOARD TESTS
# ============================================================================


class TestPublishingDashboard:
    """Test publishing dashboard"""

    def test_dashboard_creation(self):
        """Create dashboard"""
        aggregator = MetricsAggregator()
        dashboard = PublishingDashboard(aggregator)

        assert dashboard is not None

    def test_register_job(self):
        """Register job for tracking"""
        aggregator = MetricsAggregator()
        dashboard = PublishingDashboard(aggregator)

        dashboard.register_job("job-1", ["youtube", "tiktok"])

        progress = dashboard.get_job_progress("job-1")

        assert progress is not None
        assert progress.job_id == "job-1"

    def test_queue_status(self):
        """Get queue status"""
        aggregator = MetricsAggregator()
        dashboard = PublishingDashboard(aggregator)

        status = dashboard.get_queue_status()

        assert "queued_jobs" in status
        assert "active_jobs" in status

    def test_provider_status(self):
        """Get provider health"""
        aggregator = MetricsAggregator()
        dashboard = PublishingDashboard(aggregator)

        status = dashboard.get_provider_status()

        assert isinstance(status, dict)

    def test_dashboard_summary(self):
        """Get complete dashboard summary"""
        aggregator = MetricsAggregator()
        dashboard = PublishingDashboard(aggregator)

        aggregator.add_metrics({"success": True})

        summary = dashboard.get_dashboard_summary()

        assert "summary" in summary
        assert "queue" in summary
        assert "providers" in summary


# ============================================================================
# PERFORMANCE OPTIMIZER TESTS
# ============================================================================


class TestPerformanceOptimizer:
    """Test performance optimization"""

    def test_provider_selection(self):
        """Select best provider"""
        provider_metrics = {
            "mock": {"success_rate": 100.0, "avg_duration": 1.0},
            "youtube": {"success_rate": 95.0, "avg_duration": 15.0},
        }

        best = PerformanceOptimizer.select_best_provider(["youtube"], provider_metrics)

        assert best == "mock" or best == "youtube"

    def test_parallel_jobs_calculation(self):
        """Calculate parallel job limit"""
        parallel = PerformanceOptimizer.calculate_parallel_jobs(100, 4)

        assert parallel == 4

    def test_parallel_jobs_limited_by_queue(self):
        """Parallel jobs limited by queue depth"""
        parallel = PerformanceOptimizer.calculate_parallel_jobs(2, 4)

        assert parallel == 2

    def test_retry_backoff_exponential(self):
        """Calculate exponential backoff"""
        delay_0 = PerformanceOptimizer.optimize_retry_backoff(0, base_delay=1)
        delay_1 = PerformanceOptimizer.optimize_retry_backoff(1, base_delay=1)
        delay_2 = PerformanceOptimizer.optimize_retry_backoff(2, base_delay=1)

        assert delay_0 == 1
        assert delay_1 == 2
        assert delay_2 == 4

    def test_queue_clearance_estimation(self):
        """Estimate queue clearance time"""
        time_needed = PerformanceOptimizer.estimate_queue_clearance(
            queue_depth=100,
            avg_duration_seconds=10.0,
            concurrent_jobs=4,
        )

        # 100 jobs / 4 concurrent = 25 batches * 10 seconds = 250 seconds
        assert time_needed == 250.0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestPhase4Integration:
    """Integration tests for Phase 4 components"""

    def test_multi_platform_publishing_metrics(self):
        """Track multi-platform publishing"""
        aggregator = MetricsAggregator()

        for platform in ["youtube", "tiktok", "instagram"]:
            aggregator.add_metrics(
                {
                    "provider": platform,
                    "upload_seconds": 15.0,
                    "success": True,
                }
            )

        throughput = aggregator.get_throughput_metrics()
        assert throughput.jobs_completed >= 3

    def test_scheduling_workflow(self):
        """Test scheduled publishing workflow"""
        aggregator = MetricsAggregator()
        dashboard = PublishingDashboard(aggregator)

        job = PublishingJob(
            artifact_bundle_id="bundle-1",
            platforms=(PlatformType.YOUTUBE,),
        )

        dashboard.register_job(job.id, ["youtube"])
        progress = dashboard.get_job_progress(job.id)

        assert progress is not None

    def test_retry_recovery_workflow(self):
        """Test retry recovery"""
        aggregator = MetricsAggregator()

        # Initial failure
        aggregator.add_metrics(
            {
                "provider": "youtube",
                "success": False,
                "retry_count": 0,
            }
        )

        # Retry succeeds
        aggregator.add_metrics(
            {
                "provider": "youtube",
                "success": True,
                "retry_count": 1,
            }
        )

        stats = aggregator.get_retry_statistics()
        assert stats["total"] >= 1

    def test_provider_fallback_scenario(self):
        """Test provider fallback"""
        aggregator = MetricsAggregator()

        # YouTube fails
        aggregator.add_metrics(
            {
                "provider": "youtube",
                "success": False,
                "upload_seconds": 20.0,
            }
        )

        # Fallback to mock succeeds
        aggregator.add_metrics(
            {
                "provider": "mock",
                "success": True,
                "upload_seconds": 1.0,
            }
        )

        mock_metrics = aggregator.get_provider_metrics("mock")
        assert mock_metrics is not None

    def test_large_queue_optimization(self):
        """Optimize large publishing queue"""
        queue_depth = 1000
        max_concurrent = 8
        avg_duration = 20.0

        parallel = PerformanceOptimizer.calculate_parallel_jobs(queue_depth, max_concurrent)
        time_needed = PerformanceOptimizer.estimate_queue_clearance(
            queue_depth,
            avg_duration,
            parallel,
        )

        assert parallel == max_concurrent
        assert time_needed > 0

    def test_dashboard_with_active_jobs(self):
        """Dashboard tracks active jobs"""
        aggregator = MetricsAggregator()
        dashboard = PublishingDashboard(aggregator)

        # Register multiple jobs
        for i in range(5):
            dashboard.register_job(f"job-{i}", ["youtube", "tiktok"])

        summary = dashboard.get_dashboard_summary()
        assert summary["active_jobs"] == 5
