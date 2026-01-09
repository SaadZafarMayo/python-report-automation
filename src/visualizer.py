#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualizer Module
=================

This module creates various chart types from pandas DataFrames using matplotlib.
All charts are saved as PNG images for inclusion in reports.

Chart Types:
    - Bar charts (categorical comparisons)
    - Line charts (trends over time/sequence)
    - Pie charts (distribution/proportions)

Usage:
    from visualizer import create_bar_chart, create_line_chart, create_pie_chart
    
    bar_path = create_bar_chart(df, 'category', 'value', 'Title', 'output.png')

Author: Data Analytics Team
License: MIT
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server/script usage

from pathlib import Path
import pandas as pd


# =============================================================================
# Configuration
# =============================================================================

# Output directory for generated charts
CHARTS_DIR = Path("output/charts")
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# Default color palette (professional blue theme)
DEFAULT_COLORS = ['#4472C4', '#ED7D31', '#70AD47', '#FFC000', '#5B9BD5']


def create_bar_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    filename: str,
    color: str = "#4472C4"
) -> str:
    """
    Create a bar chart and save to file.
    
    Generates a vertical bar chart suitable for comparing values across
    categories. Automatically rotates x-axis labels for readability.
    
    Args:
        data (pd.DataFrame): DataFrame containing the chart data.
        x_col (str): Column name for x-axis (categories).
        y_col (str): Column name for y-axis (values).
        title (str): Chart title.
        filename (str): Output filename (saved in CHARTS_DIR).
        color (str, optional): Bar color in hex format. Defaults to blue.
        
    Returns:
        str: Full path to the saved chart image.
        
    Example:
        >>> path = create_bar_chart(df, 'month', 'revenue', 'Monthly Revenue', 'revenue.png')
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bar chart
    ax.bar(data[x_col], data[y_col], color=color)
    
    # Configure labels and title
    ax.set_xlabel(x_col.replace('_', ' ').title(), fontsize=12)
    ax.set_ylabel(y_col.replace('_', ' ').title(), fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Rotate x-axis labels for better readability
    ax.tick_params(axis='x', rotation=45)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save and close
    filepath = CHARTS_DIR / filename
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    return str(filepath)


def create_line_chart(
    data: pd.DataFrame,
    x_col: str,
    y_cols: list,
    title: str,
    filename: str
) -> str:
    """
    Create a multi-line chart and save to file.
    
    Generates a line chart with multiple series, useful for comparing
    trends across different metrics over time or categories.
    
    Args:
        data (pd.DataFrame): DataFrame containing the chart data.
        x_col (str): Column name for x-axis.
        y_cols (list): List of column names for y-axis lines.
        title (str): Chart title.
        filename (str): Output filename (saved in CHARTS_DIR).
        
    Returns:
        str: Full path to the saved chart image.
        
    Example:
        >>> path = create_line_chart(df, 'month', ['revenue', 'expenses'], 'Trends', 'trends.png')
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot each series with different colors
    for i, col in enumerate(y_cols):
        ax.plot(
            data[x_col], 
            data[col], 
            marker='o',
            label=col.replace('_', ' ').title(),
            color=DEFAULT_COLORS[i % len(DEFAULT_COLORS)],
            linewidth=2
        )
    
    # Configure labels and styling
    ax.set_xlabel(x_col.replace('_', ' ').title(), fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend()
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3)  # Light grid for readability
    
    plt.tight_layout()
    
    # Save and close
    filepath = CHARTS_DIR / filename
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    return str(filepath)


def create_pie_chart(
    data: pd.DataFrame,
    values_col: str,
    labels_col: str,
    title: str,
    filename: str
) -> str:
    """
    Create a pie chart and save to file.
    
    Generates a pie chart showing proportional distribution of values
    across categories. Includes percentage labels on each slice.
    
    Args:
        data (pd.DataFrame): DataFrame containing the chart data.
        values_col (str): Column name for slice sizes.
        labels_col (str): Column name for slice labels.
        title (str): Chart title.
        filename (str): Output filename (saved in CHARTS_DIR).
        
    Returns:
        str: Full path to the saved chart image.
        
    Example:
        >>> path = create_pie_chart(df, 'revenue', 'region', 'Revenue by Region', 'pie.png')
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Explode the largest slice slightly for emphasis
    explode = [0.05 if i == 0 else 0 for i in range(len(data))]
    
    # Create pie chart with percentage labels
    wedges, texts, autotexts = ax.pie(
        data[values_col],
        labels=data[labels_col],
        autopct='%1.1f%%',
        colors=DEFAULT_COLORS[:len(data)] if len(data) <= len(DEFAULT_COLORS) else plt.cm.Set3.colors[:len(data)],
        startangle=90,
        explode=explode,
        shadow=True,
        textprops={'fontsize': 11}
    )
    
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_fontweight('bold')
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Equal aspect ratio ensures circular pie
    ax.axis('equal')
    
    plt.tight_layout()
    
    # Save and close
    filepath = CHARTS_DIR / filename
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return str(filepath)


# =============================================================================
# Module Test
# =============================================================================
if __name__ == "__main__":
    from data_loader import load_data
    
    # Test with sample data
    df = load_data("sample_data/layoffs.csv")
    
    # Create sample charts
    print("Creating test charts...")
    
    # Aggregate data for bar chart
    bar_data = df.groupby('industry')['total_laid_off'].sum().reset_index()
    bar_data = bar_data.dropna().sort_values('total_laid_off', ascending=False).head(10)
    bar_path = create_bar_chart(bar_data, 'industry', 'total_laid_off', 
                                'Layoffs by Industry', 'test_bar.png')
    print(f"Bar chart saved: {bar_path}")
