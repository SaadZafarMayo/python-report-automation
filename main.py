#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Report Generator - Main Module
====================================

This module serves as the entry point for the Auto Report Generator application.
It orchestrates the entire report generation pipeline including data loading,
visualization creation, presentation building, and optional email delivery.

Features:
    - Generic data support (works with any CSV/Excel file)
    - Auto-detection of column types for smart chart generation
    - PowerPoint and PDF report generation
    - Optional email delivery with attachments

Usage:
    python main.py

Author: Data Analytics Team
License: MIT
"""

import pandas as pd
from datetime import datetime

# Local module imports
from data_loader import load_data, get_summary_stats
from visualizer import create_bar_chart, create_line_chart, create_pie_chart
from ppt_generator import (
    create_presentation,
    add_chart_slide,
    add_summary_slide,
    save_presentation
)
from pdf_exporter import create_pdf_report
from email_sender import send_report_email, create_report_email_body
from config_loader import load_config


def auto_detect_columns(df: pd.DataFrame) -> dict:
    """
    Automatically detect and categorize columns by their data types.
    
    This function analyzes the DataFrame to identify numeric, categorical,
    and date columns, filtering out columns with too many null values.
    
    Args:
        df (pd.DataFrame): Input DataFrame to analyze.
        
    Returns:
        dict: Dictionary containing:
            - 'numeric': List of numeric column names
            - 'categorical': List of categorical column names
            - 'date': List of date-related column names
            - 'best_numeric': Best numeric column for default charts
            - 'best_categorical': Best categorical column for default charts
            
    Example:
        >>> detected = auto_detect_columns(df)
        >>> print(detected['numeric'])
        ['revenue', 'profit', 'expenses']
    """
    # Identify column types using pandas dtype detection
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Detect date columns by name pattern
    date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
    
    # Filter columns with sufficient non-null values (>30% valid data)
    valid_numeric = [col for col in numeric_cols if df[col].notna().sum() > len(df) * 0.3]
    valid_categorical = [col for col in categorical_cols if df[col].notna().sum() > len(df) * 0.3]
    
    return {
        'numeric': valid_numeric,
        'categorical': valid_categorical,
        'date': date_cols,
        'best_numeric': valid_numeric[0] if valid_numeric else None,
        'best_categorical': valid_categorical[0] if valid_categorical else None,
    }


def get_chart_config(config: dict, chart_type: str, detected: dict) -> dict:
    """
    Resolve chart configuration, using auto-detection for 'auto' values.
    
    This function merges user-specified configuration with auto-detected
    column assignments, allowing flexible chart customization.
    
    Args:
        config (dict): Full application configuration from config.yaml.
        chart_type (str): Type of chart ('bar_chart', 'pie_chart', 'line_chart').
        detected (dict): Auto-detected column information from auto_detect_columns().
        
    Returns:
        dict: Resolved chart configuration with all 'auto' values replaced.
    """
    chart_conf = config.get('charts', {}).get(chart_type, {})
    
    result = {}
    for key, value in chart_conf.items():
        if value == "auto" or value is None:
            # Auto-assign based on key name and detected columns
            if 'category' in key:
                result[key] = detected['best_categorical']
            elif 'value' in key or 'y_col' in key:
                result[key] = detected['best_numeric']
            elif 'x_col' in key:
                result[key] = detected['best_categorical'] or (detected['date'][0] if detected['date'] else None)
            elif key == 'y_columns':
                result[key] = detected['numeric'][:3]  # Use top 3 numeric columns
            elif key == 'title':
                result[key] = None  # Will be auto-generated later
            else:
                result[key] = value
        else:
            result[key] = value
    
    return result


def generate_report(
    data_file: str = None,
    output_formats: list = None,
    send_email: bool = False
) -> dict:
    """
    Generate a complete report with charts and summary from any data source.
    
    This is the main report generation function that orchestrates the entire
    pipeline from data loading to final output creation.
    
    Args:
        data_file (str, optional): Path to the data file. Uses config default if None.
        output_formats (list, optional): List of output formats ['pptx', 'pdf'].
            Uses config default if None.
        send_email (bool, optional): Whether to send report via email. Defaults to False.
        
    Returns:
        dict: Dictionary mapping format names to output file paths.
            Example: {'pptx': 'output/report.pptx', 'pdf': 'output/report.pdf'}
            
    Raises:
        FileNotFoundError: If the specified data file doesn't exist.
        ValueError: If the data file format is not supported.
    """
    # Load application configuration
    config = load_config()
    
    # Use defaults from config if not specified
    if data_file is None:
        data_file = config['data']['default_file']
    
    if output_formats is None:
        output_formats = config['output'].get('formats', ['pptx'])
    
    # Get source type from config (for API, database, etc.)
    source_type = config['data'].get('source_type', 'auto')
    
    # Get additional parameters for SQL/API
    extra_params = {}
    if config['data'].get('table'):
        extra_params['table'] = config['data']['table']
    if config['data'].get('query'):
        extra_params['query'] = config['data']['query']
    
    # =========================================================================
    # STEP 1: Load and analyze data
    # =========================================================================
    print(f"Loading data from: {data_file}")
    print(f"Source type: {source_type}")
    df = load_data(data_file, source_type=source_type, **extra_params)
    summary = get_summary_stats(df)
    detected = auto_detect_columns(df)
    
    print(f"  Rows: {len(df)}, Columns: {len(df.columns)}")
    print(f"  Numeric columns: {detected['numeric']}")
    print(f"  Categorical columns: {detected['categorical'][:5]}...")
    
    # =========================================================================
    # STEP 2: Create visualizations
    # =========================================================================
    print("\nCreating visualizations...")
    chart_paths = []
    chart_info = []
    
    charts_config = config.get('charts', {})
    
    # --- Bar Chart ---
    bar_conf = get_chart_config(config, 'bar_chart', detected)
    if charts_config.get('bar_chart', {}).get('enabled', True) and bar_conf.get('category_column') and bar_conf.get('value_column'):
        cat_col = bar_conf['category_column']
        val_col = bar_conf['value_column']
        agg = bar_conf.get('aggregation', 'sum')
        top_n = bar_conf.get('top_n', 15)
        
        # Aggregate data by category
        if agg == 'count':
            agg_data = df.groupby(cat_col).size().reset_index(name=val_col)
        else:
            agg_data = df.groupby(cat_col)[val_col].agg(agg).reset_index()
        
        # Sort and limit to top N
        agg_data = agg_data.dropna().sort_values(val_col, ascending=False)
        if top_n > 0:
            agg_data = agg_data.head(top_n)
        
        # Generate title if not specified
        title = bar_conf.get('title') or f"{val_col.replace('_', ' ').title()} by {cat_col.replace('_', ' ').title()}"
        
        bar_path = create_bar_chart(agg_data, cat_col, val_col, title, 'bar_chart.png')
        chart_paths.append(bar_path)
        chart_info.append({'title': title, 'path': bar_path, 'desc': f"Top {len(agg_data)} {cat_col} by {val_col}"})
        print(f"  ✓ Bar chart: {title}")
    
    # --- Pie Chart ---
    pie_conf = get_chart_config(config, 'pie_chart', detected)
    if charts_config.get('pie_chart', {}).get('enabled', True) and pie_conf.get('category_column') and pie_conf.get('value_column'):
        cat_col = pie_conf['category_column']
        val_col = pie_conf['value_column']
        agg = pie_conf.get('aggregation', 'sum')
        top_n = pie_conf.get('top_n', 10)
        
        # For pie charts, prefer columns with fewer unique values
        if cat_col == detected['best_categorical']:
            # Find a better categorical column with fewer unique values (ideal: 3-8)
            for col in detected['categorical']:
                unique_count = df[col].nunique()
                if 3 <= unique_count <= 8:
                    cat_col = col
                    break
        
        # Aggregate data for pie chart
        if agg == 'count':
            pie_data = df.groupby(cat_col).size().reset_index(name=val_col)
        else:
            pie_data = df.groupby(cat_col)[val_col].agg(agg).reset_index()
        
        pie_data = pie_data.dropna().sort_values(val_col, ascending=False)
        if top_n > 0 and len(pie_data) > top_n:
            # Group small slices into "Other"
            top_data = pie_data.head(top_n - 1)
            other_sum = pie_data.iloc[top_n - 1:][val_col].sum()
            other_row = pd.DataFrame({cat_col: ['Other'], val_col: [other_sum]})
            pie_data = pd.concat([top_data, other_row], ignore_index=True)
        
        title = pie_conf.get('title') or f"{val_col.replace('_', ' ').title()} by {cat_col.replace('_', ' ').title()}"
        
        pie_path = create_pie_chart(pie_data, val_col, cat_col, title, 'pie_chart.png')
        chart_paths.append(pie_path)
        chart_info.append({'title': title, 'path': pie_path, 'desc': f"Distribution across {cat_col}"})
        print(f"  ✓ Pie chart: {title}")
    
    # --- Line Chart ---
    line_conf = get_chart_config(config, 'line_chart', detected)
    if charts_config.get('line_chart', {}).get('enabled', True) and len(detected['numeric']) >= 2:
        x_col = line_conf.get('x_column') or detected['best_categorical']
        y_cols = line_conf.get('y_columns') or detected['numeric'][:3]
        
        if x_col and y_cols:
            # Aggregate numeric columns by x-axis category
            line_data = df.groupby(x_col)[y_cols].sum().reset_index()
            line_data = line_data.dropna().head(20)  # Limit data points for readability
            
            if len(line_data) > 1:
                title = line_conf.get('title') or "Numeric Trends Comparison"
                line_path = create_line_chart(line_data, x_col, y_cols if isinstance(y_cols, list) else [y_cols], title, 'line_chart.png')
                chart_paths.append(line_path)
                chart_info.append({'title': title, 'path': line_path, 'desc': f"Trends across {x_col}"})
                print(f"  ✓ Line chart: {title}")
    
    # =========================================================================
    # STEP 3: Build PowerPoint presentation
    # =========================================================================
    print("\nBuilding presentation...")
    
    prs = create_presentation(
        config['report']['title'],
        f"Generated on {datetime.now().strftime('%B %d, %Y')}",
        config['report'].get('author', 'Auto Report Generator')
    )
    
    # Prepare summary data for display
    summary_display = {
        'Total Records': summary['total_rows'],
        'Columns Analyzed': len(summary['columns']),
    }
    
    # Add top numeric column summaries
    for col, stats in list(summary['numeric_summary'].items())[:3]:
        summary_display[f"{col.replace('_', ' ').title()}"] = {
            col: {
                'Total': f"{stats['total']:,.0f}",
                'Average': f"{stats['average']:,.2f}",
                'Max': f"{stats['max']:,.0f}",
            }
        }
    
    add_summary_slide(prs, "Data Summary", summary_display)
    
    # Add chart slides
    for info in chart_info:
        add_chart_slide(prs, info['title'], info['path'], info['desc'])
    
    # =========================================================================
    # STEP 4: Save outputs
    # =========================================================================
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    outputs = {}
    
    # Save PowerPoint
    if 'pptx' in output_formats:
        filename = f"report_{timestamp}.pptx"
        output_path = save_presentation(prs, filename)
        outputs['pptx'] = output_path
        print(f"✓ PowerPoint saved: {output_path}")
    
    # Save PDF
    if 'pdf' in output_formats:
        pdf_summary = {}
        for col, stats in list(summary['numeric_summary'].items())[:4]:
            pdf_summary[f"Total {col.replace('_', ' ').title()}"] = stats['total']
        pdf_summary['Total Records'] = summary['total_rows']
        
        pdf_path = create_pdf_report(
            config['report']['title'],
            f"Generated on {datetime.now().strftime('%B %d, %Y')}",
            pdf_summary,
            chart_paths,
            f"report_{timestamp}.pdf"
        )
        outputs['pdf'] = pdf_path
        print(f"✓ PDF saved: {pdf_path}")
    
    # =========================================================================
    # STEP 5: Send email (if enabled)
    # =========================================================================
    if send_email and config['email'].get('enabled'):
        email_config = config['email']
        email_body = create_report_email_body(
            config['report']['title'],
            {'Records Analyzed': summary['total_rows']}
        )
        send_report_email(
            to_emails=email_config.get('recipients', []),
            subject=f"📊 {config['report']['title']} - {datetime.now().strftime('%B %d, %Y')}",
            body=email_body,
            attachments=list(outputs.values()),
            config=email_config
        )
    
    return outputs


def main():
    """
    Main entry point for the Auto Report Generator.
    
    Loads configuration and generates reports with all enabled output formats.
    Email is sent if enabled in configuration.
    """
    print("="*60)
    print("  AUTO REPORT GENERATOR (Generic)")
    print("  Works with any CSV/Excel data")
    print("="*60)
    print()
    
    config = load_config()
    
    outputs = generate_report(
        output_formats=['pptx', 'pdf'],
        send_email=config['email'].get('enabled', False)
    )
    
    print()
    print("="*60)
    print("  REPORT GENERATION COMPLETE!")
    print("="*60)
    for fmt, path in outputs.items():
        print(f"  {fmt.upper()}: {path}")
    print("="*60)
    
    return outputs


# =============================================================================
# Script Entry Point
# =============================================================================
if __name__ == "__main__":
    main()
