#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Exporter Module
===================

This module generates PDF reports using ReportLab. It creates professional
documents with titles, summaries, and embedded chart images.

Features:
    - Executive summary with key metrics
    - Embedded chart images
    - Professional styling and formatting
    - DataFrame to PDF table export

Usage:
    from pdf_exporter import create_pdf_report
    
    pdf_path = create_pdf_report(
        "Report Title",
        "Subtitle",
        {'Total': 1000, 'Average': 100},
        ['chart1.png', 'chart2.png'],
        "output.pdf"
    )

Author: Data Analytics Team
License: MIT
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from pathlib import Path
from datetime import datetime
import pandas as pd


# =============================================================================
# Configuration
# =============================================================================

# Output directory for PDF files
OUTPUT_DIR = Path("output/pdf")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Brand color
BRAND_COLOR = colors.HexColor('#2E75B6')


def create_pdf_report(
    title: str,
    subtitle: str,
    summary_data: dict,
    chart_paths: list,
    filename: str = None
) -> str:
    """
    Create a PDF report with summary and charts.
    
    Generates a professional PDF document containing an executive summary
    section with key metrics and embedded chart images.
    
    Args:
        title (str): Report title.
        subtitle (str): Report subtitle (typically date or period).
        summary_data (dict): Dictionary of summary statistics to display.
        chart_paths (list): List of paths to chart images to embed.
        filename (str, optional): Output filename. Auto-generated if None.
        
    Returns:
        str: Full path to the generated PDF file.
        
    Example:
        >>> summary = {'Total Revenue': 500000, 'Total Profit': 150000}
        >>> charts = ['charts/revenue.png', 'charts/profit.png']
        >>> path = create_pdf_report("Sales Report", "Q4 2024", summary, charts)
    """
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{timestamp}.pdf"
    
    filepath = OUTPUT_DIR / filename
    
    # Initialize document with margins
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # =========================================================================
    # Define Styles
    # =========================================================================
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=6,
        alignment=TA_CENTER,
        textColor=BRAND_COLOR
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.gray
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor=BRAND_COLOR
    )
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.gray
    )
    
    # =========================================================================
    # Build Content
    # =========================================================================
    content = []
    
    # --- Title Section ---
    content.append(Paragraph(title, title_style))
    content.append(Paragraph(subtitle, subtitle_style))
    content.append(Spacer(1, 20))
    
    # --- Executive Summary Section ---
    content.append(Paragraph("Executive Summary", heading_style))
    
    for key, value in summary_data.items():
        if isinstance(value, dict):
            # Handle nested dictionaries
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, (int, float)):
                    formatted = f"${sub_value:,.2f}" if sub_value > 100 else f"{sub_value:,.2f}"
                    content.append(Paragraph(f"• {sub_key}: {formatted}", styles['Normal']))
        else:
            # Simple key-value pairs
            if isinstance(value, (int, float)):
                formatted = f"${value:,.2f}" if value > 100 else f"{value:,.2f}"
            else:
                formatted = str(value)
            content.append(Paragraph(f"• {key}: {formatted}", styles['Normal']))
    
    content.append(Spacer(1, 20))
    
    # --- Charts Section ---
    content.append(Paragraph("Visualizations", heading_style))
    
    for chart_path in chart_paths:
        if Path(chart_path).exists():
            # Embed chart image with appropriate sizing
            img = Image(chart_path, width=6*inch, height=4*inch)
            content.append(img)
            content.append(Spacer(1, 15))
    
    # --- Footer ---
    content.append(Spacer(1, 30))
    content.append(Paragraph(
        f"Generated by Auto Report Generator | {datetime.now().strftime('%B %d, %Y')}",
        footer_style
    ))
    
    # Build the PDF
    doc.build(content)
    
    return str(filepath)


def dataframe_to_pdf(df: pd.DataFrame, title: str, filename: str = None) -> str:
    """
    Export a DataFrame directly to PDF as a formatted table.
    
    Creates a PDF document with the DataFrame rendered as a styled table.
    Useful for data exports and detailed reports.
    
    Args:
        df (pd.DataFrame): DataFrame to export.
        title (str): Document title.
        filename (str, optional): Output filename. Auto-generated if None.
        
    Returns:
        str: Full path to the generated PDF file.
        
    Example:
        >>> path = dataframe_to_pdf(sales_df, "Sales Data Export")
    """
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data_export_{timestamp}.pdf"
    
    filepath = OUTPUT_DIR / filename
    
    # Use landscape for wide tables
    doc = SimpleDocTemplate(str(filepath), pagesize=landscape(letter))
    
    styles = getSampleStyleSheet()
    content = []
    
    # Title
    content.append(Paragraph(title, styles['Heading1']))
    content.append(Spacer(1, 20))
    
    # Convert DataFrame to table data (headers + rows)
    table_data = [df.columns.tolist()] + df.values.tolist()
    
    # Create styled table
    table = Table(table_data)
    table.setStyle(TableStyle([
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows styling
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')])
    ]))
    
    content.append(table)
    doc.build(content)
    
    return str(filepath)


# =============================================================================
# Module Test
# =============================================================================
if __name__ == "__main__":
    # Test PDF generation
    test_summary = {
        'Total Revenue': 811000,
        'Total Profit': 312000,
        'Average Monthly Revenue': 67583.33
    }
    
    pdf_path = create_pdf_report(
        "Sales Report",
        "Q4 2024 Performance",
        test_summary,
        []  # No charts for test
    )
    print(f"Test PDF created: {pdf_path}")
