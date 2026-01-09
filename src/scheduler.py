#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduler Module
================

This module provides scheduling functionality for automated report generation.
It wraps the 'schedule' library to provide simple interfaces for daily,
weekly, and interval-based scheduling.

Features:
    - Daily scheduling at specific times
    - Weekly scheduling on specific days
    - Interval-based scheduling (every N minutes)
    - Job management (list, clear)

Usage:
    from scheduler import schedule_daily, schedule_weekly, run_scheduler
    from main import generate_report
    
    schedule_weekly(generate_report, day="monday", time_str="09:00")
    run_scheduler()  # Blocks and runs scheduled jobs

Note:
    The scheduler must remain running for jobs to execute.
    For production use, consider using system schedulers (cron, Task Scheduler)
    or cloud-based solutions.

Author: Data Analytics Team
License: MIT
"""

import schedule
import time
from datetime import datetime
from pathlib import Path


def run_report_job(report_function, *args, **kwargs):
    """
    Wrapper to execute a report generation job with logging.
    
    Provides consistent logging and error handling for scheduled jobs.
    
    Args:
        report_function (callable): The report generation function to execute.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.
        
    Returns:
        Any: Result from the report function, or None if an error occurred.
    """
    print(f"\n{'='*50}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting scheduled report...")
    print(f"{'='*50}")
    
    try:
        result = report_function(*args, **kwargs)
        print(f"✓ Report generated successfully: {result}")
        return result
    except Exception as e:
        print(f"✗ Error generating report: {e}")
        return None


def schedule_daily(report_function, time_str: str = "09:00", *args, **kwargs):
    """
    Schedule a report to run daily at a specific time.
    
    Args:
        report_function (callable): The function to run.
        time_str (str): Time in HH:MM format (24-hour). Defaults to "09:00".
        *args: Additional positional arguments for the function.
        **kwargs: Additional keyword arguments for the function.
        
    Example:
        >>> schedule_daily(generate_report, "09:00")
        ✓ Scheduled daily report at 09:00
    """
    schedule.every().day.at(time_str).do(
        run_report_job, report_function, *args, **kwargs
    )
    print(f"✓ Scheduled daily report at {time_str}")


def schedule_weekly(report_function, day: str = "monday", time_str: str = "09:00", *args, **kwargs):
    """
    Schedule a report to run weekly on a specific day and time.
    
    Args:
        report_function (callable): The function to run.
        day (str): Day of week (monday, tuesday, wednesday, thursday, 
            friday, saturday, sunday). Defaults to "monday".
        time_str (str): Time in HH:MM format (24-hour). Defaults to "09:00".
        *args: Additional positional arguments for the function.
        **kwargs: Additional keyword arguments for the function.
        
    Example:
        >>> schedule_weekly(generate_report, day="monday", time_str="09:00")
        ✓ Scheduled weekly report on Monday at 09:00
    """
    # Get the appropriate day method from schedule
    getattr(schedule.every(), day.lower()).at(time_str).do(
        run_report_job, report_function, *args, **kwargs
    )
    print(f"✓ Scheduled weekly report on {day.title()} at {time_str}")


def schedule_interval(report_function, minutes: int = 60, *args, **kwargs):
    """
    Schedule a report to run at regular intervals.
    
    Args:
        report_function (callable): The function to run.
        minutes (int): Interval in minutes. Defaults to 60.
        *args: Additional positional arguments for the function.
        **kwargs: Additional keyword arguments for the function.
        
    Example:
        >>> schedule_interval(generate_report, minutes=30)
        ✓ Scheduled report every 30 minutes
    """
    schedule.every(minutes).minutes.do(
        run_report_job, report_function, *args, **kwargs
    )
    print(f"✓ Scheduled report every {minutes} minutes")


def run_scheduler():
    """
    Start the scheduler loop.
    
    This function blocks and continuously checks for pending jobs.
    Press Ctrl+C to stop the scheduler.
    
    Note:
        This function runs indefinitely until interrupted.
    """
    print("\n" + "="*50)
    print("SCHEDULER STARTED")
    print("="*50)
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Pending jobs:")
    
    for job in schedule.get_jobs():
        print(f"  - {job}")
    
    print("\nPress Ctrl+C to stop the scheduler")
    print("="*50 + "\n")
    
    # Main scheduler loop
    while True:
        schedule.run_pending()
        time.sleep(1)  # Check every second


def run_once(report_function, *args, **kwargs):
    """
    Run a report immediately (one-time execution).
    
    Useful for testing or manual report generation.
    
    Args:
        report_function (callable): The function to run.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.
        
    Returns:
        Any: Result from the report function.
        
    Example:
        >>> result = run_once(generate_report)
    """
    return run_report_job(report_function, *args, **kwargs)


def clear_all_jobs():
    """
    Clear all scheduled jobs.
    
    Removes all pending scheduled jobs from the scheduler.
    
    Example:
        >>> clear_all_jobs()
        ✓ All scheduled jobs cleared
    """
    schedule.clear()
    print("✓ All scheduled jobs cleared")


def list_jobs():
    """
    List all currently scheduled jobs.
    
    Returns:
        list: List of scheduled job objects.
        
    Example:
        >>> jobs = list_jobs()
        >>> print(f"Total jobs: {len(jobs)}")
    """
    jobs = schedule.get_jobs()
    print(f"Scheduled jobs ({len(jobs)}):")
    for job in jobs:
        print(f"  - {job}")
    return jobs


# =============================================================================
# Module Test
# =============================================================================
if __name__ == "__main__":
    # Demo: Schedule a simple test job
    def test_job():
        print("Test job executed!")
        return "test_output.txt"
    
    # Run once immediately
    print("Running test job once...")
    run_once(test_job)
    
    # Show scheduling demo
    print("\nScheduling demo (not actually running):")
    schedule_daily(test_job, "09:00")
    schedule_weekly(test_job, "monday", "10:00")
    schedule_interval(test_job, minutes=60)
    
    list_jobs()
    clear_all_jobs()
