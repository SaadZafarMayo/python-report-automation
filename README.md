# 📊 Python Report Automation

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

A powerful Python automation tool that transforms **any data source** into professional PowerPoint presentations and PDF reports with auto-generated visualizations.

![Report Generation Flow](https://img.shields.io/badge/Data-→_Charts_→_Reports_→_Email-orange)

---

## ✨ Features

- 🔌 **Multiple Data Sources** — CSV, Excel, JSON, MySQL, PostgreSQL, REST APIs, Google Sheets
- 📈 **Smart Visualizations** — Auto-generates bar, line, and pie charts based on your data
- 📑 **PowerPoint Generation** — Professional presentations with branded slides
- 📄 **PDF Export** — Clean PDF reports with embedded charts
- 📧 **Email Delivery** — Automated email sending with attachments
- ⏰ **Scheduling** — Daily, weekly, or interval-based automation
- ⚙️ **Fully Configurable** — YAML-based settings with smart auto-detection

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/SaadZafarMayo/python-report-automation.git
cd python-report-automation

# Install dependencies
pip install -r requirements.txt

# Run the report generator
python main.py
```

---

## 📁 Project Structure

```
python-report-automation/
│
├── main.py                 # Entry point - run this to generate reports
├── run_scheduled.py        # Run this for scheduled automation
├── config.yaml             # Configuration file (customize here!)
├── requirements.txt        # Python dependencies
├── README.md
│
├── src/                    # Source code modules
│   ├── __init__.py
│   ├── data_loader.py      # Multi-source data loading
│   ├── visualizer.py       # Chart generation (matplotlib)
│   ├── ppt_generator.py    # PowerPoint creation
│   ├── pdf_exporter.py     # PDF report generation
│   ├── email_sender.py     # Email delivery
│   ├── scheduler.py        # Scheduling utilities
│   └── config_loader.py    # Configuration management
│
├── sample_data/            # Sample data files
│   └── sales_data.json
│
└── output/                 # Generated reports
    ├── charts/
    ├── presentations/
    └── pdf/
```

---

## 🔌 Supported Data Sources

| Source | Format | Connection Example |
|--------|--------|-------------------|
| **CSV** | `.csv` | `sample_data/sales.csv` |
| **Excel** | `.xlsx`, `.xls` | `reports/data.xlsx` |
| **JSON** | `.json` | `sample_data/data.json` |
| **MySQL** | Connection string | `mysql+pymysql://user:pass@localhost:3306/db` |
| **PostgreSQL** | Connection string | `postgresql://user:pass@localhost:5432/db` |
| **SQLite** | Connection string | `sqlite:///database.db` |
| **REST API** | URL | `https://api.example.com/data` |
| **Google Sheets** | Sheet ID | `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms` |

---

## ⚙️ Configuration

All settings are managed in `config.yaml`. The file is fully commented with examples.

### Data Source Configuration

```yaml
data:
  # File-based sources
  default_file: "sample_data/sales_data.json"
  
  # Database (uncomment to use)
  # default_file: "mysql+pymysql://user:password@localhost:3306/database"
  # source_type: "sql"
  # table: "sales_table"
  # query: "SELECT * FROM sales WHERE year = 2024"  # Optional: custom query
  
  # REST API (uncomment to use)
  # default_file: "https://api.example.com/data"
  # source_type: "api"
```

### Chart Customization

```yaml
charts:
  bar_chart:
    enabled: true
    category_column: "auto"      # Or specify: "region", "company", etc.
    value_column: "auto"         # Or specify: "revenue", "sales", etc.
    aggregation: "sum"           # Options: sum, mean, count, max, min
    title: "auto"                # Or custom: "Sales by Region"
    top_n: 15                    # Show top N categories

  pie_chart:
    enabled: true
    category_column: "auto"
    value_column: "auto"
    aggregation: "sum"
    title: "auto"
    top_n: 10                    # Ideal: 3-10 categories for pie charts

  line_chart:
    enabled: true
    x_column: "auto"
    y_columns: "auto"
    title: "auto"
```

### Email Settings

```yaml
email:
  enabled: true
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  sender_email: "your-email@gmail.com"
  sender_password: "your-app-password"    # Use App Password for Gmail
  recipients:
    - "recipient1@example.com"
    - "recipient2@example.com"
```

### Schedule Settings

```yaml
schedule:
  enabled: true
  frequency: "weekly"      # Options: daily, weekly, interval
  time: "09:00"            # 24-hour format
  day: "monday"            # For weekly
  interval_minutes: 60     # For interval
```

---

## 📖 Usage Examples

### Basic Usage

```python
from main import generate_report

# Generate report using config.yaml settings
outputs = generate_report()

# Generate and send via email
outputs = generate_report(send_email=True)
```

### Loading from Different Sources

```python
from src.data_loader import load_data

# CSV / Excel / JSON (auto-detected)
df = load_data("data.csv")
df = load_data("report.xlsx")
df = load_data("data.json")

# MySQL Database
df = load_data(
    "mysql+pymysql://root:password@localhost:3306/mydb",
    source_type="sql",
    table="sales"
)

# With Custom Query
df = load_data(
    "mysql+pymysql://root:password@localhost:3306/mydb",
    source_type="sql",
    query="SELECT * FROM sales WHERE year = 2024"
)

# REST API
df = load_data(
    "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd",
    source_type="api"
)

# Google Sheets
df = load_data(
    "your-sheet-id",
    source_type="google_sheets",
    credentials_file="credentials.json"
)
```

### Scheduled Reports

```bash
# Configure schedule in config.yaml, then run:
python run_scheduled.py
```

Or programmatically:

```python
from src.scheduler import schedule_weekly, run_scheduler
from main import generate_report

schedule_weekly(generate_report, day="monday", time_str="09:00")
run_scheduler()  # Runs indefinitely
```

---

## 🔧 Setup Guides

### Gmail Setup (for email delivery)

1. Enable **2-Factor Authentication** on your Google account
2. Generate an **App Password**: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Use the App Password in `config.yaml` (not your regular password)

### MySQL Setup

```bash
pip install pymysql
```

```yaml
data:
  default_file: "mysql+pymysql://user:password@localhost:3306/database"
  source_type: "sql"
  table: "your_table"
```

### PostgreSQL Setup

```bash
pip install psycopg2-binary
```

```yaml
data:
  default_file: "postgresql://user:password@localhost:5432/database"
  source_type: "sql"
  table: "your_table"
```

### Google Sheets Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project & enable **Google Sheets API**
3. Create **Service Account** credentials
4. Download JSON key as `credentials.json`
5. Share your Google Sheet with the service account email

---

## 🧠 How Auto-Detection Works

The tool intelligently analyzes your data:

1. **Numeric columns** → Used for chart values (revenue, sales, counts)
2. **Categorical columns** → Used for grouping (region, company, category)
3. **Pie charts** → Automatically selects categories with 3-10 unique values
4. **Titles** → Auto-generated from column names

Works with any data structure — sales, analytics, surveys, inventory, and more.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `pandas` | Data manipulation |
| `matplotlib` | Chart generation |
| `python-pptx` | PowerPoint creation |
| `reportlab` | PDF generation |
| `schedule` | Task scheduling |
| `PyYAML` | Configuration |
| `requests` | REST API calls |
| `sqlalchemy` | Database connections |
| `pymysql` | MySQL driver |
| `gspread` | Google Sheets |

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🚀 Future Improvements

- 🤖 **AI Integration (Gemini)** — Auto-generate insights and executive summaries
- 💬 **Natural Language Queries** — Ask questions about your data in plain English
- 📊 **Smart Chart Recommendations** — AI-powered visualization suggestions
- 📱 **Dashboard Generation** — Interactive web dashboards
- 🔄 **Real-time Data Sync** — Live data updates from APIs

---

## 🙏 Acknowledgments

- Built with Python and open-source libraries
- Inspired by the need for automated reporting workflows

---

<p align="center">
  Made with ❤️ for data automation
</p>
