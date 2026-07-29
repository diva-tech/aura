"""M13 Phase 1 Tests: Publishing Foundation.

Comprehensive tests for domain models, profiles, scheduling, reporting, and retry policies.
"""

from datetime import datetime, timedelta

import pytest

from aura_backend.publishing import (  # Models; Profiles; Scheduling; Reporting; Manifest; Retry
    DEFAULT_RETRY_POLICY,
    RATE_LIMIT_RETRY_POLICY,
    TIKTOK_PROFILE,
    YOUTUBE_PROFILE,
    YOUTUBE_SHORTS_PROFILE,
    ImmediateSchedule,
    JobReport,
    PlatformType,
    PublishedAsset,
    PublishingJob,
    PublishingManifest,
    PublishingMetadata,
    PublishingReport,
    PublishingTask,
    RecurrencePattern,
    RecurringPublish,
    RetryableError,
    RetryPolicy,
    RetryStrategy,
    ScheduledPublish,
    ScheduleType,
    ThumbnailAsset,
    get_all_profiles,
    get_profile,
)

# ============================================================================
# MODEL CREATION TESTS
# ============================================================================


class TestPublishingJobCreation:
    """Test PublishingJob creation"""

    def test_create_publishing_job(self):
        """Create publishing job"""
        job = PublishingJob(
            artifact_bundle_id="bundle-1",
            session_id="s1",
            title="Test Video",
            platforms=(PlatformType.YOUTUBE, PlatformType.TIKTOK),
        )

        assert job.artifact_bundle_id == "bundle-1"
        assert job.status.value == "pending"
        assert len(job.platforms) == 2

    def test_job_to_dict(self):
        """PublishingJob serialization"""
        job = PublishingJob(title="Test")
        d = job.to_dict()

        assert d["title"] == "Test"
        assert "id" in d
        assert "created_at" in d


class TestPublishingTaskCreation:
    """Test PublishingTask creation"""

    def test_create_publishing_task(self):
        """Create publishing task"""
        task = PublishingTask(
            job_id="job-1",
            platform=PlatformType.YOUTUBE,
        )

        assert task.job_id == "job-1"
        assert task.platform == PlatformType.YOUTUBE
        assert task.status.value == "pending"

    def test_task_immutable(self):
        """PublishingTask is immutable"""
        task = PublishingTask()

        with pytest.raises(AttributeError):
            task.job_id = "new-job"


class TestPublishingMetadata:
    """Test PublishingMetadata"""

    def test_create_metadata(self):
        """Create publishing metadata"""
        metadata = PublishingMetadata(
            title="Video Title",
            description="Video description",
            tags=("tag1", "tag2"),
        )

        assert metadata.title == "Video Title"
        assert len(metadata.tags) == 2
        assert metadata.is_made_for_kids is False

    def test_metadata_immutable(self):
        """PublishingMetadata is immutable"""
        metadata = PublishingMetadata()

        with pytest.raises(AttributeError):
            metadata.title = "New Title"


class TestThumbnailAsset:
    """Test ThumbnailAsset"""

    def test_create_thumbnail(self):
        """Create thumbnail asset"""
        thumb = ThumbnailAsset(
            job_id="job-1",
            file_path="/path/to/thumb.jpg",
            width_pixels=1280,
            height_pixels=720,
        )

        assert thumb.width_pixels == 1280
        assert thumb.height_pixels == 720
        assert thumb.format == "jpg"


class TestPublishedAsset:
    """Test PublishedAsset"""

    def test_create_published_asset(self):
        """Create published asset"""
        asset = PublishedAsset(
            task_id="task-1",
            platform=PlatformType.YOUTUBE,
            platform_video_id="dQw4w9WgXcQ",
            view_count=1000,
        )

        assert asset.platform_video_id == "dQw4w9WgXcQ"
        assert asset.view_count == 1000


# ============================================================================
# PROFILE TESTS
# ============================================================================


class TestPublishingProfiles:
    """Test publishing profiles"""

    def test_youtube_profile(self):
        """YouTube profile configuration"""
        profile = YOUTUBE_PROFILE

        assert profile.platform == PlatformType.YOUTUBE
        assert profile.max_duration_seconds == 12 * 60 * 60
        assert "16:9" in profile.supported_aspect_ratios
        assert profile.supports_monetization is True

    def test_youtube_shorts_profile(self):
        """YouTube Shorts profile configuration"""
        profile = YOUTUBE_SHORTS_PROFILE

        assert profile.platform == PlatformType.YOUTUBE_SHORTS
        assert profile.max_duration_seconds == 60
        assert profile.required_aspect_ratio == "9:16"

    def test_tiktok_profile(self):
        """TikTok profile configuration"""
        profile = TIKTOK_PROFILE

        assert profile.platform == PlatformType.TIKTOK
        assert profile.max_duration_seconds == 10 * 60
        assert profile.supports_scheduling is True

    def test_get_profile(self):
        """Retrieve profile by platform"""
        profile = get_profile(PlatformType.INSTAGRAM_REEL)

        assert profile.platform == PlatformType.INSTAGRAM_REEL
        assert profile.max_duration_seconds == 90

    def test_get_all_profiles(self):
        """Get all built-in profiles"""
        profiles = get_all_profiles()

        assert "youtube" in profiles
        assert "tiktok" in profiles
        assert "instagram_reel" in profiles
        assert len(profiles) >= 8

    def test_profile_serialization(self):
        """Profile serialization"""
        profile = YOUTUBE_PROFILE
        d = profile.to_dict()

        assert d["platform"] == "youtube"
        assert d["max_duration_seconds"] > 0


# ============================================================================
# SCHEDULING TESTS
# ============================================================================


class TestImmediateSchedule:
    """Test immediate publishing schedule"""

    def test_immediate_schedule(self):
        """Create immediate schedule"""
        schedule = ImmediateSchedule()

        assert schedule.is_immediate() is True
        assert schedule.is_scheduled() is False
        assert schedule.schedule_type == ScheduleType.IMMEDIATE

    def test_immediate_next_publish_time(self):
        """Immediate schedule next publish time"""
        schedule = ImmediateSchedule()
        base_time = datetime.utcnow()

        next_time = schedule.get_next_publish_time(base_time)

        assert next_time == base_time


class TestScheduledPublish:
    """Test scheduled publishing"""

    def test_scheduled_publish(self):
        """Create scheduled publish"""
        publish_time = datetime.utcnow() + timedelta(hours=1)
        schedule = ScheduledPublish(publish_at=publish_time)

        assert schedule.is_scheduled() is True
        assert schedule.publish_at == publish_time

    def test_scheduled_requires_publish_at(self):
        """Scheduled schedule requires publish_at"""
        with pytest.raises(ValueError):
            ScheduledPublish(publish_at=None)


class TestRecurringPublish:
    """Test recurring publishing"""

    def test_recurring_daily(self):
        """Create daily recurring schedule"""
        start = datetime.utcnow()
        schedule = RecurringPublish(
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_start_date=start,
            recurrence_interval=1,
        )

        assert schedule.is_recurring() is True
        assert schedule.recurrence_pattern == RecurrencePattern.DAILY

    def test_recurring_requires_pattern(self):
        """Recurring requires pattern"""
        with pytest.raises(ValueError):
            RecurringPublish(recurrence_pattern=None, recurrence_start_date=datetime.utcnow())

    def test_recurring_next_publish_time_daily(self):
        """Calculate next publish time for daily recurrence"""
        start = datetime(2025, 1, 1, 10, 0, 0)
        schedule = RecurringPublish(
            recurrence_pattern=RecurrencePattern.DAILY,
            recurrence_start_date=start,
            recurrence_interval=1,
        )

        base = datetime(2025, 1, 1, 12, 0, 0)
        next_time = schedule.get_next_publish_time(base)

        assert next_time is not None
        assert next_time.day == 2  # Next day


class TestScheduleSerialization:
    """Test schedule serialization"""

    def test_schedule_to_dict(self):
        """Schedule serialization"""
        schedule = ImmediateSchedule()
        d = schedule.to_dict()

        assert d["schedule_type"] == "immediate"
        assert "timezone" in d


# ============================================================================
# REPORTING TESTS
# ============================================================================


class TestPublishingReport:
    """Test publishing reports"""

    def test_create_report(self):
        """Create publishing report"""
        report = PublishingReport(
            job_id="job-1",
            task_id="task-1",
            platform=PlatformType.YOUTUBE,
            platform_video_id="video123",
        )

        assert report.job_id == "job-1"
        assert report.platform_video_id == "video123"

    def test_report_immutable(self):
        """PublishingReport is immutable"""
        report = PublishingReport()

        with pytest.raises(AttributeError):
            report.job_id = "new-job"


class TestJobReport:
    """Test job reports"""

    def test_create_job_report(self):
        """Create job report"""
        report = JobReport(
            job_id="job-1",
            total_tasks=5,
            completed_tasks=3,
            successful_tasks=3,
        )

        assert report.total_tasks == 5
        assert report.success_rate == 60.0

    def test_job_report_success_rate(self):
        """Job report success rate calculation"""
        report = JobReport(
            total_tasks=10,
            successful_tasks=8,
        )

        assert report.success_rate == 80.0


# ============================================================================
# MANIFEST TESTS
# ============================================================================


class TestPublishingManifest:
    """Test publishing manifest"""

    def test_create_manifest(self):
        """Create publishing manifest"""
        job = PublishingJob(artifact_bundle_id="bundle-1")
        task = PublishingTask(job_id=job.id)

        manifest = PublishingManifest(
            job=job,
            tasks=(task,),
            artifact_bundle_id="bundle-1",
        )

        assert manifest.job.artifact_bundle_id == "bundle-1"
        assert len(manifest.tasks) == 1

    def test_manifest_to_dict(self):
        """Manifest serialization"""
        job = PublishingJob()
        manifest = PublishingManifest(job=job)
        d = manifest.to_dict()

        assert "id" in d
        assert "job" in d
        assert "task_count" in d

    def test_manifest_task_queries(self):
        """Query tasks from manifest"""
        job = PublishingJob(id="job-1")
        task1 = PublishingTask(id="task-1", job_id="job-1")
        task2 = PublishingTask(id="task-2", job_id="job-1")

        report1 = PublishingReport(
            task_id="task-1",
            publish_status="published",
        )
        report2 = PublishingReport(
            task_id="task-2",
            publish_status="failed",
        )

        manifest = PublishingManifest(
            job=job,
            tasks=(task1, task2),
            reports=(report1, report2),
        )

        assert len(manifest.get_successful_tasks()) == 1
        assert len(manifest.get_failed_tasks()) == 1

    def test_manifest_immutable(self):
        """PublishingManifest is immutable"""
        manifest = PublishingManifest()

        with pytest.raises(AttributeError):
            manifest.artifact_bundle_id = "new-id"


# ============================================================================
# RETRY POLICY TESTS
# ============================================================================


class TestRetryPolicy:
    """Test retry policies"""

    def test_default_retry_policy(self):
        """Default retry policy"""
        policy = DEFAULT_RETRY_POLICY

        assert policy.max_retries == 3
        assert policy.retry_strategy == RetryStrategy.EXPONENTIAL_BACKOFF
        assert policy.should_retry(0) is True
        assert policy.should_retry(3) is False

    def test_no_retry_policy(self):
        """No retry policy"""
        policy = RetryPolicy(retry_strategy=RetryStrategy.NONE)

        assert policy.should_retry(0) is False

    def test_fixed_delay_strategy(self):
        """Fixed delay retry strategy"""
        policy = RetryPolicy(
            max_retries=3,
            retry_strategy=RetryStrategy.FIXED_DELAY,
            initial_delay_seconds=5,
        )

        delay = policy.get_next_delay_seconds(0)
        assert delay == 5
        delay = policy.get_next_delay_seconds(1)
        assert delay == 5

    def test_linear_backoff_strategy(self):
        """Linear backoff retry strategy"""
        policy = RetryPolicy(
            max_retries=3,
            retry_strategy=RetryStrategy.LINEAR_BACKOFF,
            initial_delay_seconds=1,
        )

        delay0 = policy.get_next_delay_seconds(0)
        delay1 = policy.get_next_delay_seconds(1)

        assert delay0 < delay1

    def test_exponential_backoff_strategy(self):
        """Exponential backoff retry strategy"""
        policy = RetryPolicy(
            max_retries=3,
            retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            initial_delay_seconds=1,
            backoff_multiplier=2.0,
        )

        delay0 = policy.get_next_delay_seconds(0)
        delay1 = policy.get_next_delay_seconds(1)
        delay2 = policy.get_next_delay_seconds(2)

        assert delay0 < delay1 < delay2

    def test_retryable_error_check(self):
        """Check if error is retryable"""
        policy = DEFAULT_RETRY_POLICY

        assert policy.is_retryable("network_error") is True
        assert policy.is_retryable("timeout") is True
        assert policy.is_retryable("unknown_error") is False

    def test_rate_limit_retry_policy(self):
        """Rate limit retry policy"""
        policy = RATE_LIMIT_RETRY_POLICY

        assert RetryableError.RATE_LIMIT in policy.retryable_errors
        assert policy.max_retries == 10

    def test_retry_policy_max_delay_enforcement(self):
        """Max delay is enforced"""
        policy = RetryPolicy(
            max_retries=10,
            retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            initial_delay_seconds=1,
            max_delay_seconds=100,
            backoff_multiplier=10.0,
        )

        delay = policy.get_next_delay_seconds(5)
        assert delay <= policy.max_delay_seconds

    def test_retry_policy_serialization(self):
        """Retry policy serialization"""
        policy = DEFAULT_RETRY_POLICY
        d = policy.to_dict()

        assert d["max_retries"] == 3
        assert d["retry_strategy"] == "exponential_backoff"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestM13Phase1Integration:
    """Integration tests for Phase 1 components"""

    def test_job_with_tasks_and_reports(self):
        """Create job with tasks and reports"""
        job = PublishingJob(
            artifact_bundle_id="bundle-1",
            title="Test Video",
            platforms=(PlatformType.YOUTUBE, PlatformType.TIKTOK),
            total_tasks=2,
        )

        tasks = (
            PublishingTask(job_id=job.id, platform=PlatformType.YOUTUBE),
            PublishingTask(job_id=job.id, platform=PlatformType.TIKTOK),
        )

        reports = (
            PublishingReport(
                job_id=job.id,
                task_id=tasks[0].id,
                platform=PlatformType.YOUTUBE,
                publish_status="published",
            ),
            PublishingReport(
                job_id=job.id,
                task_id=tasks[1].id,
                platform=PlatformType.TIKTOK,
                publish_status="published",
            ),
        )

        manifest = PublishingManifest(
            artifact_bundle_id="bundle-1",
            job=job,
            tasks=tasks,
            reports=reports,
        )

        assert len(manifest.tasks) == 2
        assert len(manifest.reports) == 2
        assert len(manifest.get_successful_tasks()) == 2

    def test_manifest_with_profiles_and_scheduling(self):
        """Combine manifest, profiles, and scheduling"""
        job = PublishingJob(
            platforms=(PlatformType.YOUTUBE, PlatformType.YOUTUBE_SHORTS),
        )

        yt_profile = get_profile(PlatformType.YOUTUBE)
        shorts_profile = get_profile(PlatformType.YOUTUBE_SHORTS)

        schedule = ScheduledPublish(
            publish_at=datetime.utcnow() + timedelta(hours=1),
        )

        manifest = PublishingManifest(
            job=job,
            artifact_bundle_id="bundle-1",
        )

        assert manifest.job.platforms[0] == PlatformType.YOUTUBE
        assert yt_profile.max_duration_seconds > shorts_profile.max_duration_seconds
        assert schedule.is_scheduled() is True
