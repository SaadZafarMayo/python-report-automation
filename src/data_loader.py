#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Loader Module
==================

This module handles loading data from various sources including files,
databases, APIs, and cloud services.

Supported Sources:
    - CSV files (.csv)
    - Excel files (.xlsx, .xls)
    - JSON files (.json)
    - SQL databases (SQLite, MySQL, PostgreSQL)
    - REST APIs
    - Google Sheets

Usage:
    from data_loader import load_data, get_summary_stats
    
    # From file
    df = load_data("data.csv")
    df = load_data("data.json")
    
    # From database
    df = load_data("sqlite:///database.db", query="SELECT * FROM sales")
    
    # From API
    df = load_data("https://api.example.com/data", source_type="api")
    
    # From Google Sheets
    df = load_data("your-sheet-id", source_type="google_sheets")

Author: Data Analytics Team
License: MIT
"""

import pandas as pd
from pathlib import Path
import json
from typing import Optional, Union


# =============================================================================
# File Loaders
# =============================================================================

def load_csv(file_path: str) -> pd.DataFrame:
    """
    Load data from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file.
        
    Returns:
        pd.DataFrame: Loaded data as a pandas DataFrame.
    """
    return pd.read_csv(file_path)


def load_excel(file_path: str, sheet_name: str = None) -> pd.DataFrame:
    """
    Load data from an Excel file.
    
    Args:
        file_path (str): Path to the Excel file.
        sheet_name (str, optional): Specific sheet to load.
        
    Returns:
        pd.DataFrame: Loaded data as a pandas DataFrame.
    """
    return pd.read_excel(file_path, sheet_name=sheet_name)


def load_json(file_path: str) -> pd.DataFrame:
    """
    Load data from a JSON file.
    
    Supports both JSON arrays and JSON objects with nested data.
    
    Args:
        file_path (str): Path to the JSON file.
        
    Returns:
        pd.DataFrame: Loaded data as a pandas DataFrame.
        
    Example:
        >>> df = load_json("data.json")
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Handle different JSON structures
    if isinstance(data, list):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
        # Check if it's a nested structure with a data key
        for key in ['data', 'results', 'records', 'items']:
            if key in data and isinstance(data[key], list):
                return pd.DataFrame(data[key])
        # Otherwise normalize the dict
        return pd.json_normalize(data)
    else:
        raise ValueError("JSON structure not supported. Expected array or object.")


# =============================================================================
# Database Loaders
# =============================================================================

def load_sql(
    connection_string: str,
    query: str = None,
    table: str = None
) -> pd.DataFrame:
    """
    Load data from a SQL database.
    
    Supports SQLite, MySQL, and PostgreSQL databases.
    
    Args:
        connection_string (str): Database connection string.
            - SQLite: "sqlite:///path/to/database.db"
            - MySQL: "mysql+pymysql://user:password@host:port/database"
            - PostgreSQL: "postgresql://user:password@host:port/database"
        query (str, optional): SQL query to execute.
        table (str, optional): Table name to load (alternative to query).
        
    Returns:
        pd.DataFrame: Query results as a pandas DataFrame.
        
    Example:
        >>> df = load_sql("sqlite:///sales.db", query="SELECT * FROM orders")
        >>> df = load_sql("sqlite:///sales.db", table="customers")
    """
    try:
        from sqlalchemy import create_engine
    except ImportError:
        raise ImportError("SQLAlchemy is required for database connections. Install with: pip install sqlalchemy")
    
    engine = create_engine(connection_string)
    
    if query:
        return pd.read_sql_query(query, engine)
    elif table:
        return pd.read_sql_table(table, engine)
    else:
        raise ValueError("Either 'query' or 'table' must be provided for SQL loading.")


# =============================================================================
# API Loader
# =============================================================================

def load_api(
    url: str,
    method: str = "GET",
    headers: dict = None,
    params: dict = None,
    json_path: str = None
) -> pd.DataFrame:
    """
    Load data from a REST API endpoint.
    
    Args:
        url (str): API endpoint URL.
        method (str, optional): HTTP method. Defaults to "GET".
        headers (dict, optional): Request headers (e.g., for authentication).
        params (dict, optional): Query parameters.
        json_path (str, optional): Dot-notation path to data in response.
            Example: "data.results" for {"data": {"results": [...]}}
        
    Returns:
        pd.DataFrame: API response data as a pandas DataFrame.
        
    Example:
        >>> df = load_api("https://api.example.com/users")
        >>> df = load_api(
        ...     "https://api.example.com/data",
        ...     headers={"Authorization": "Bearer token"},
        ...     json_path="data.items"
        ... )
    """
    try:
        import requests
    except ImportError:
        raise ImportError("Requests library is required for API calls. Install with: pip install requests")
    
    # Make the request
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        params=params
    )
    response.raise_for_status()
    
    data = response.json()
    
    # Navigate to nested data if json_path specified
    if json_path:
        for key in json_path.split('.'):
            data = data[key]
    
    # Convert to DataFrame
    if isinstance(data, list):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
        # Try common data keys
        for key in ['data', 'results', 'records', 'items']:
            if key in data and isinstance(data[key], list):
                return pd.DataFrame(data[key])
        return pd.json_normalize(data)
    else:
        raise ValueError("API response format not supported.")


# =============================================================================
# Google Sheets Loader
# =============================================================================

def load_google_sheets(
    sheet_id: str,
    sheet_name: str = None,
    credentials_file: str = "credentials.json"
) -> pd.DataFrame:
    """
    Load data from a Google Sheets spreadsheet.
    
    Requires Google Sheets API credentials. See setup instructions:
    https://developers.google.com/sheets/api/quickstart/python
    
    Args:
        sheet_id (str): Google Sheets document ID (from the URL).
        sheet_name (str, optional): Specific sheet/tab name. Defaults to first sheet.
        credentials_file (str, optional): Path to Google API credentials JSON.
        
    Returns:
        pd.DataFrame: Sheet data as a pandas DataFrame.
        
    Setup:
        1. Enable Google Sheets API in Google Cloud Console
        2. Create credentials (OAuth or Service Account)
        3. Download credentials.json
        4. Place in project directory
        
    Example:
        >>> df = load_google_sheets("1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        raise ImportError(
            "Google Sheets libraries required. Install with: "
            "pip install gspread google-auth"
        )
    
    # Define scopes
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    # Authenticate
    credentials = Credentials.from_service_account_file(
        credentials_file,
        scopes=scopes
    )
    client = gspread.authorize(credentials)
    
    # Open spreadsheet
    spreadsheet = client.open_by_key(sheet_id)
    
    # Get specific sheet or first sheet
    if sheet_name:
        worksheet = spreadsheet.worksheet(sheet_name)
    else:
        worksheet = spreadsheet.sheet1
    
    # Get all data and convert to DataFrame
    data = worksheet.get_all_records()
    return pd.DataFrame(data)


# =============================================================================
# Main Loader Function
# =============================================================================

def load_data(
    source: str,
    source_type: str = "auto",
    **kwargs
) -> pd.DataFrame:
    """
    Universal data loader - auto-detects source type and loads data.
    
    This is the main entry point for loading data from any supported source.
    
    Args:
        source (str): Data source path, URL, or connection string.
        source_type (str, optional): Type of source. Options:
            - "auto": Auto-detect from source string (default)
            - "csv": CSV file
            - "excel": Excel file
            - "json": JSON file
            - "sql": SQL database
            - "api": REST API
            - "google_sheets": Google Sheets
        **kwargs: Additional arguments passed to specific loaders.
            - For SQL: query, table
            - For API: method, headers, params, json_path
            - For Google Sheets: sheet_name, credentials_file
        
    Returns:
        pd.DataFrame: Loaded data as a pandas DataFrame.
        
    Examples:
        >>> # Auto-detect file type
        >>> df = load_data("sales.csv")
        >>> df = load_data("data.json")
        
        >>> # SQL database
        >>> df = load_data("sqlite:///db.sqlite", query="SELECT * FROM users")
        
        >>> # REST API
        >>> df = load_data("https://api.example.com/data", source_type="api")
        
        >>> # Google Sheets
        >>> df = load_data("sheet_id_here", source_type="google_sheets")
    """
    # Auto-detect source type
    if source_type == "auto":
        source_lower = source.lower()
        
        if source_lower.endswith('.csv'):
            source_type = "csv"
        elif source_lower.endswith(('.xlsx', '.xls')):
            source_type = "excel"
        elif source_lower.endswith('.json'):
            source_type = "json"
        elif source_lower.startswith(('sqlite:', 'mysql:', 'postgresql:', 'postgres:')):
            source_type = "sql"
        elif source_lower.startswith(('http://', 'https://')):
            source_type = "api"
        else:
            raise ValueError(
                f"Could not auto-detect source type for: {source}\n"
                "Please specify source_type parameter."
            )
    
    # Route to appropriate loader
    if source_type == "csv":
        return load_csv(source)
    
    elif source_type == "excel":
        return load_excel(source, sheet_name=kwargs.get('sheet_name'))
    
    elif source_type == "json":
        return load_json(source)
    
    elif source_type == "sql":
        return load_sql(
            source,
            query=kwargs.get('query'),
            table=kwargs.get('table')
        )
    
    elif source_type == "api":
        return load_api(
            source,
            method=kwargs.get('method', 'GET'),
            headers=kwargs.get('headers'),
            params=kwargs.get('params'),
            json_path=kwargs.get('json_path')
        )
    
    elif source_type == "google_sheets":
        return load_google_sheets(
            source,
            sheet_name=kwargs.get('sheet_name'),
            credentials_file=kwargs.get('credentials_file', 'credentials.json')
        )
    
    else:
        raise ValueError(f"Unsupported source type: {source_type}")


# =============================================================================
# Summary Statistics
# =============================================================================

def get_summary_stats(df: pd.DataFrame) -> dict:
    """
    Generate comprehensive summary statistics from a DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame to analyze.
        
    Returns:
        dict: Summary statistics containing:
            - 'total_rows': Number of rows
            - 'columns': List of column names
            - 'numeric_summary': Stats for each numeric column
    """
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    summary = {
        'total_rows': len(df),
        'columns': list(df.columns),
        'numeric_summary': {}
    }
    
    for col in numeric_cols:
        summary['numeric_summary'][col] = {
            'total': df[col].sum(),
            'average': df[col].mean(),
            'max': df[col].max(),
            'min': df[col].min()
        }
    
    return summary


# =============================================================================
# Module Test
# =============================================================================
if __name__ == "__main__":
    print("Data Loader Module")
    print("="*40)
    print("\nSupported sources:")
    print("  - CSV files (.csv)")
    print("  - Excel files (.xlsx, .xls)")
    print("  - JSON files (.json)")
    print("  - SQL databases (SQLite, MySQL, PostgreSQL)")
    print("  - REST APIs")
    print("  - Google Sheets")
    
    # Test with local file
    print("\n\nTesting with sample data...")
    df = load_data("sample_data/layoffs.csv")
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    print(df.head())
