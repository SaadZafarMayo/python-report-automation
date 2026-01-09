#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Config Loader Module
====================

This module handles loading and managing application configuration from
YAML files. It provides default values when configuration is missing.

Features:
    - YAML configuration file loading
    - Default configuration fallback
    - Section-specific config getters

Configuration File:
    The default configuration file is 'config.yaml' in the same directory
    as this module.

Usage:
    from config_loader import load_config, get_email_config
    
    config = load_config()
    email_settings = get_email_config()

Author: Data Analytics Team
License: MIT
"""

import yaml
from pathlib import Path


# =============================================================================
# Configuration
# =============================================================================

# Path to the configuration file (project root directory)
CONFIG_FILE = Path(__file__).parent.parent / "config.yaml"


def load_config() -> dict:
    """
    Load configuration from config.yaml.
    
    Reads the YAML configuration file and returns it as a dictionary.
    Falls back to default configuration if the file doesn't exist.
    
    Returns:
        dict: Configuration dictionary with all settings.
        
    Example:
        >>> config = load_config()
        >>> print(config['report']['title'])
        'Data Analysis Report'
    """
    if not CONFIG_FILE.exists():
        print(f"Warning: Config file not found at {CONFIG_FILE}")
        return get_default_config()
    
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def get_default_config() -> dict:
    """
    Return default configuration values.
    
    Provides sensible defaults when config.yaml is missing or incomplete.
    
    Returns:
        dict: Default configuration dictionary.
    """
    return {
        'data': {
            'default_file': 'sample_data/data.csv'
        },
        'report': {
            'title': 'Data Analysis Report',
            'author': 'Auto Report Generator',
            'company': 'Company Name'
        },
        'charts': {
            'bar_chart': {
                'enabled': True,
                'category_column': 'auto',
                'value_column': 'auto',
                'aggregation': 'sum',
                'top_n': 15
            },
            'pie_chart': {
                'enabled': True,
                'category_column': 'auto',
                'value_column': 'auto',
                'aggregation': 'sum',
                'top_n': 10
            },
            'line_chart': {
                'enabled': True,
                'x_column': 'auto',
                'y_columns': 'auto'
            }
        },
        'email': {
            'enabled': False
        },
        'schedule': {
            'enabled': False
        },
        'output': {
            'formats': ['pptx'],
            'charts_dir': 'output/charts',
            'presentations_dir': 'output/presentations',
            'pdf_dir': 'output/pdf'
        }
    }


def get_email_config() -> dict:
    """
    Get email-specific configuration.
    
    Convenience function to extract just the email settings.
    
    Returns:
        dict: Email configuration section.
        
    Example:
        >>> email_config = get_email_config()
        >>> if email_config.get('enabled'):
        ...     print("Email is enabled")
    """
    config = load_config()
    return config.get('email', {})


def get_schedule_config() -> dict:
    """
    Get schedule-specific configuration.
    
    Convenience function to extract just the schedule settings.
    
    Returns:
        dict: Schedule configuration section.
        
    Example:
        >>> schedule_config = get_schedule_config()
        >>> print(schedule_config.get('frequency'))
        'weekly'
    """
    config = load_config()
    return config.get('schedule', {})


def get_chart_config() -> dict:
    """
    Get chart-specific configuration.
    
    Convenience function to extract just the chart settings.
    
    Returns:
        dict: Charts configuration section.
    """
    config = load_config()
    return config.get('charts', {})


# =============================================================================
# Module Test / Config Display
# =============================================================================
if __name__ == "__main__":
    config = load_config()
    
    print("Current Configuration:")
    print("="*40)
    
    for section, values in config.items():
        print(f"\n[{section}]")
        if isinstance(values, dict):
            for key, value in values.items():
                # Hide sensitive information
                if 'password' in key.lower():
                    value = '****'
                print(f"  {key}: {value}")
