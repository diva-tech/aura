"""M13 Phase 1: Publishing Foundation — Scheduling Models.

Immutable scheduling models for immediate, scheduled, and recurring publishing.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum


class ScheduleType(StrEnum):
    """Schedule type"""

    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    RECURRING = "recurring"


class RecurrencePattern(StrEnum):
    """Recurrence pattern for recurring schedules"""

    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


class WeekDay(StrEnum):
    """Days of week"""

    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


@dataclass(frozen=True)
class PublishSchedule:
    """Immutable publishing schedule"""

    schedule_type: ScheduleType = ScheduleType.IMMEDIATE
    timezone: str = "UTC"
    publish_at: datetime | None = None
    recurrence_pattern: RecurrencePattern | None = None
    recurrence_start_date: datetime | None = None
    recurrence_end_date: datetime | None = None
    recurrence_interval: int = 1  # Every N days/weeks/months
    recurrence_weekdays: tuple[WeekDay, ...] = ()  # For weekly recurrence
    recurrence_day_of_month: int | None = None  # For monthly recurrence
    max_occurrences: int | None = None
    occurrence_count: int = 0

    def is_immediate(self) -> bool:
        return self.schedule_type == ScheduleType.IMMEDIATE

    def is_scheduled(self) -> bool:
        return self.schedule_type == ScheduleType.SCHEDULED

    def is_recurring(self) -> bool:
        return self.schedule_type == ScheduleType.RECURRING

    def get_next_publish_time(self, base_time: datetime) -> datetime | None:
        """Calculate next publish time from base time"""
        if self.schedule_type == ScheduleType.IMMEDIATE:
            return base_time

        if self.schedule_type == ScheduleType.SCHEDULED:
            if self.publish_at and self.publish_at > base_time:
                return self.publish_at
            return None

        if self.schedule_type == ScheduleType.RECURRING:
            if not self.recurrence_pattern or not self.recurrence_start_date:
                return None

            current = max(self.recurrence_start_date, base_time)

            if self.recurrence_end_date and current > self.recurrence_end_date:
                return None

            if self.max_occurrences and self.occurrence_count >= self.max_occurrences:
                return None

            if self.recurrence_pattern == RecurrencePattern.DAILY:
                return current + timedelta(days=self.recurrence_interval)

            if self.recurrence_pattern == RecurrencePattern.WEEKLY:
                return current + timedelta(weeks=self.recurrence_interval)

            if self.recurrence_pattern == RecurrencePattern.BIWEEKLY:
                return current + timedelta(weeks=2)

            if self.recurrence_pattern == RecurrencePattern.MONTHLY:
                month = current.month + self.recurrence_interval
                year = current.year
                while month > 12:
                    month -= 12
                    year += 1
                day = min(current.day, 28)  # Avoid invalid dates
                return current.replace(year=year, month=month, day=day)

            if self.recurrence_pattern == RecurrencePattern.QUARTERLY:
                month = current.month + (self.recurrence_interval * 3)
                year = current.year
                while month > 12:
                    month -= 12
                    year += 1
                day = min(current.day, 28)
                return current.replace(year=year, month=month, day=day)

            if self.recurrence_pattern == RecurrencePattern.ANNUALLY:
                year = current.year + self.recurrence_interval
                return current.replace(year=year)

        return None

    def to_dict(self) -> dict:
        result = {
            "schedule_type": self.schedule_type.value,
            "timezone": self.timezone,
        }

        if self.schedule_type == ScheduleType.SCHEDULED:
            result["publish_at"] = self.publish_at.isoformat() if self.publish_at else None

        if self.schedule_type == ScheduleType.RECURRING:
            result["recurrence_pattern"] = (
                self.recurrence_pattern.value if self.recurrence_pattern else None
            )
            result["recurrence_start_date"] = (
                self.recurrence_start_date.isoformat() if self.recurrence_start_date else None
            )
            result["recurrence_end_date"] = (
                self.recurrence_end_date.isoformat() if self.recurrence_end_date else None
            )
            result["max_occurrences"] = self.max_occurrences
            result["occurrence_count"] = self.occurrence_count

        return result


@dataclass(frozen=True)
class ImmediateSchedule(PublishSchedule):
    """Publish immediately"""

    schedule_type: ScheduleType = ScheduleType.IMMEDIATE
    timezone: str = "UTC"


@dataclass(frozen=True)
class ScheduledPublish(PublishSchedule):
    """Publish at specific time"""

    schedule_type: ScheduleType = ScheduleType.SCHEDULED
    timezone: str = "UTC"
    publish_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.schedule_type == ScheduleType.SCHEDULED and not self.publish_at:
            raise ValueError("publish_at required for scheduled publishing")


@dataclass(frozen=True)
class RecurringPublish(PublishSchedule):
    """Publish on recurring schedule"""

    schedule_type: ScheduleType = ScheduleType.RECURRING
    timezone: str = "UTC"
    recurrence_pattern: RecurrencePattern | None = None
    recurrence_start_date: datetime | None = None

    def __post_init__(self) -> None:
        if self.schedule_type == ScheduleType.RECURRING:
            if not self.recurrence_pattern:
                raise ValueError("recurrence_pattern required for recurring publishing")
            if not self.recurrence_start_date:
                raise ValueError("recurrence_start_date required for recurring publishing")
