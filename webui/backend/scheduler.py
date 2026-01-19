"""
Scheduler for Kometa Web UI

Handles scheduled automatic runs of Kometa based on configured schedules.
"""

import asyncio
import logging
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable, Awaitable
from pathlib import Path
import re

import schedule

logger = logging.getLogger(__name__)


class KometaScheduler:
    """Manages scheduled Kometa runs."""

    def __init__(self):
        self._enabled = False
        self._schedule_expression: Optional[str] = None
        self._dry_run_only = True
        self._run_callback: Optional[Callable[..., Awaitable[Any]]] = None
        self._scheduler_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._next_run: Optional[datetime] = None
        self._last_run: Optional[datetime] = None
        self._run_count = 0
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_callback(self, callback: Callable[..., Awaitable[Any]], loop: asyncio.AbstractEventLoop):
        """Set the callback to run when schedule triggers."""
        self._run_callback = callback
        self._loop = loop

    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status."""
        return {
            "enabled": self._enabled,
            "schedule": self._schedule_expression,
            "dry_run_only": self._dry_run_only,
            "next_run": self._next_run.isoformat() if self._next_run else None,
            "last_run": self._last_run.isoformat() if self._last_run else None,
            "run_count": self._run_count,
        }

    def configure(
        self,
        enabled: bool,
        schedule_expression: Optional[str] = None,
        dry_run_only: bool = True
    ) -> Dict[str, Any]:
        """Configure the scheduler."""
        was_enabled = self._enabled

        self._enabled = enabled
        self._schedule_expression = schedule_expression
        self._dry_run_only = dry_run_only

        # Clear existing jobs
        schedule.clear()

        if enabled and schedule_expression:
            self._setup_schedule(schedule_expression)

            if not was_enabled:
                self._start_scheduler_thread()
        elif not enabled and was_enabled:
            self._stop_scheduler_thread()

        return self.get_status()

    def _setup_schedule(self, expression: str):
        """Parse schedule expression and setup schedule jobs."""
        schedule.clear()

        expression = expression.lower().strip()

        try:
            if expression == "hourly":
                schedule.every().hour.at(":00").do(self._trigger_run)
                self._next_run = self._calculate_next_hourly()

            elif expression == "daily":
                schedule.every().day.at("00:00").do(self._trigger_run)
                self._next_run = self._calculate_next_daily()

            elif expression.startswith("weekly("):
                # Extract day of week
                match = re.match(r"weekly\((\w+)\)", expression)
                if match:
                    day = match.group(1)
                    day_map = {
                        "monday": schedule.every().monday,
                        "tuesday": schedule.every().tuesday,
                        "wednesday": schedule.every().wednesday,
                        "thursday": schedule.every().thursday,
                        "friday": schedule.every().friday,
                        "saturday": schedule.every().saturday,
                        "sunday": schedule.every().sunday,
                    }
                    if day in day_map:
                        day_map[day].at("00:00").do(self._trigger_run)
                        self._next_run = self._calculate_next_weekly(day)

            elif expression.startswith("monthly("):
                # Monthly on specific day
                match = re.match(r"monthly\((\d+)\)", expression)
                if match:
                    day = int(match.group(1))
                    # Schedule library doesn't have monthly, so we check daily
                    schedule.every().day.at("00:00").do(
                        lambda: self._trigger_run() if datetime.now().day == day else None
                    )
                    self._next_run = self._calculate_next_monthly(day)

            elif expression.startswith("hourly("):
                # Specific hour
                match = re.match(r"hourly\((\d+)\)", expression)
                if match:
                    hour = int(match.group(1))
                    schedule.every().day.at(f"{hour:02d}:00").do(self._trigger_run)
                    self._next_run = self._calculate_next_at_hour(hour)

            else:
                logger.warning("Unsupported schedule expression: %s", expression)
                return

            logger.info("Scheduler configured: %s, next run: %s", expression, self._next_run)

        except Exception as e:
            logger.error("Failed to setup schedule: %s", e)

    def _trigger_run(self):
        """Trigger a scheduled run."""
        if not self._run_callback or not self._loop:
            logger.warning("No run callback configured")
            return

        self._last_run = datetime.now()
        self._run_count += 1

        logger.info("Scheduler triggering run #%d", self._run_count)

        # Schedule the async callback on the event loop
        asyncio.run_coroutine_threadsafe(
            self._execute_run(),
            self._loop
        )

        # Update next run time
        self._update_next_run()

    async def _execute_run(self):
        """Execute the scheduled run."""
        try:
            await self._run_callback(
                dry_run=self._dry_run_only,
                run_type=None,
                libraries=None,
                collections=None
            )
        except Exception as e:
            logger.error("Scheduled run failed: %s", e)

    def _update_next_run(self):
        """Update the next run time based on schedule."""
        next_job = schedule.next_run()
        if next_job:
            self._next_run = next_job

    def _calculate_next_hourly(self) -> datetime:
        """Calculate next hourly run time."""
        now = datetime.now()
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        return next_hour

    def _calculate_next_daily(self) -> datetime:
        """Calculate next daily run time."""
        now = datetime.now()
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return tomorrow

    def _calculate_next_weekly(self, day: str) -> datetime:
        """Calculate next weekly run time."""
        day_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
        }
        target_day = day_map.get(day, 0)
        now = datetime.now()
        days_ahead = target_day - now.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_run = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_ahead)
        return next_run

    def _calculate_next_monthly(self, day: int) -> datetime:
        """Calculate next monthly run time."""
        now = datetime.now()
        if now.day >= day:
            # Next month
            if now.month == 12:
                next_run = now.replace(year=now.year + 1, month=1, day=day,
                                       hour=0, minute=0, second=0, microsecond=0)
            else:
                next_run = now.replace(month=now.month + 1, day=day,
                                       hour=0, minute=0, second=0, microsecond=0)
        else:
            next_run = now.replace(day=day, hour=0, minute=0, second=0, microsecond=0)
        return next_run

    def _calculate_next_at_hour(self, hour: int) -> datetime:
        """Calculate next run at specific hour."""
        now = datetime.now()
        next_run = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
        return next_run

    def _start_scheduler_thread(self):
        """Start the scheduler thread."""
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            return

        self._stop_event.clear()
        self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()
        logger.info("Scheduler thread started")

    def _stop_scheduler_thread(self):
        """Stop the scheduler thread."""
        self._stop_event.set()
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)
            self._scheduler_thread = None
        schedule.clear()
        self._next_run = None
        logger.info("Scheduler thread stopped")

    def _run_scheduler(self):
        """Run the scheduler loop in a separate thread."""
        while not self._stop_event.is_set():
            schedule.run_pending()
            self._stop_event.wait(timeout=30)  # Check every 30 seconds

    def stop(self):
        """Stop the scheduler completely."""
        self._enabled = False
        self._stop_scheduler_thread()


# Global scheduler instance
scheduler = KometaScheduler()
