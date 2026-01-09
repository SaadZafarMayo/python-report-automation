#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduled Report Runner
=======================

This script reads schedule settings from config.yaml and runs the report
generator automatically based on the configured schedule.

Configuration (in config.yaml):
    schedule:
      enabled: true
      frequency: "weekly"     # daily, weekly, or interval
      time: "09:00"           # Time in 24-hour format
      day: "monday"           # For weekly only
      interval_minutes: 60    # For interval only

Usage:
    python run_scheduled.py

Note:
    This script must remain running for scheduled jobs to execute.
    Press Ctrl+C to stop the scheduler.

Author: Data Analytics Team
License: MIT
"""

from scheduler import schedule_daily, schedule_weekly, schedule_interval, run_scheduler
from config_loader import load_config
from main import generate_report


def main():
    """
    Main entry point for the scheduled report runner.
    
    Reads configuration and sets up the appropriate schedule based on
    the 'schedule' section in config.yaml.
    """
    # Load configuration
    config = load_config()
    schedule_config = config.get('schedule', {})
    
    # Check if scheduling is enabled
    if not schedule_config.get('enabled', False):
        print("Scheduling is disabled in config.yaml")
        print("Set 'schedule.enabled: true' to enable.")
        exit()
    
    # Extract schedule settings
    frequency = schedule_config.get('frequency', 'daily')
    time_str = schedule_config.get('time', '09:00')
    
    # Configure schedule based on frequency type
    if frequency == 'daily':
        schedule_daily(generate_report, time_str)
        print(f"Scheduled: Daily at {time_str}")
    
    elif frequency == 'weekly':
        day = schedule_config.get('day', 'monday')
        schedule_weekly(generate_report, day=day, time_str=time_str)
        print(f"Scheduled: Every {day.title()} at {time_str}")
    
    elif frequency == 'interval':
        minutes = schedule_config.get('interval_minutes', 60)
        schedule_interval(generate_report, minutes=minutes)
        print(f"Scheduled: Every {minutes} minutes")
    
    else:
        print(f"Unknown frequency: {frequency}")
        print("Supported: daily, weekly, interval")
        exit()
    
    # Start the scheduler loop
    print("\nScheduler is running! Press Ctrl+C to stop.\n")
    run_scheduler()


# =============================================================================
# Script Entry Point
# =============================================================================
if __name__ == "__main__":
    main()
