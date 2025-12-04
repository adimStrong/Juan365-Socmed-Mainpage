# Juan365 Social Media Report System

Professional social media analytics dashboard for Juan365 Facebook page. Generates interactive HTML reports from Meta Business Suite exports.

## Features

- **Global Dashboard Filtering** - Filter entire dashboard by post type and date range
- **KPI Cards** - Total posts, engagement, reactions, comments, shares
- **Post Type Analysis** - Performance breakdown by Photo, Video, Reel, Live, Text
- **Weekly/Monthly Metrics** - ISO week tracking with actual active dates
- **Interactive Charts** - Daily trends, monthly comparison, content distribution
- **Best Posting Times** - Day and time slot analysis
- **Top 15 Posts** - Highest performing content
- **All Posts Table** - Filterable, sortable post listing

## Quick Start

### 1. Export Data from Meta Business Suite
1. Go to [Meta Business Suite](https://business.facebook.com)
2. Navigate to **Content** → **Posts & Reels**
3. Click **Export** and download CSV
4. Save to `exports/` folder

### 2. Generate Report
```bash
# Double-click or run:
UPDATE_REPORT.bat
```

### 3. View Report
```bash
# Double-click or run:
START_REPORT_SERVER.bat
```
Opens at http://localhost:8080

## File Structure

```
juan365_engagement_project/
├── exports/                    # Meta Business Suite CSV exports
├── reports/
│   ├── generate_report.py     # Report generator
│   ├── serve_report.py        # Local HTTP server
│   ├── templates/
│   │   └── report_template.html
│   └── output/
│       └── Juan365_Report_LATEST.html
├── START_REPORT_SERVER.bat    # One-click server
└── UPDATE_REPORT.bat          # One-click report generation
```

## Requirements

- Python 3.x
- pandas
- jinja2

```bash
pip install pandas jinja2
```

## Usage

### Generate report with all data:
```bash
python reports/generate_report.py
```

### Generate report for last 60 days:
```bash
python reports/generate_report.py --days 60
```

## Dashboard Filters

The dashboard includes a sticky global filter bar that updates all sections:
- **Post Type**: All, Photo, Video, Reel, Live, Text
- **Date Range**: Custom start/end date picker
- **Reset All**: Return to full dataset

All KPIs, charts, tables, and metrics recalculate instantly when filters change.

## Data Refresh

Recommended: Export fresh data from Meta Business Suite every 3 days for up-to-date analytics.
