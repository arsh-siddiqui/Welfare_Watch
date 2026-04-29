# WelfareWatch – Welfare Analytics Platform

A Flask-based open data platform that tracks and visualises government welfare scheme delivery across every district in India. WelfareWatch turns raw CSV welfare data into actionable analytics — welfare scores, trend charts, district comparisons, and citizen reports — all in one dashboard.

---

## Problem it Solves

Government welfare programmes (education, healthcare, food security, employment) reach citizens unevenly across India's districts. WelfareWatch makes this visible. Officials, researchers, and citizens can instantly see which districts are performing well, which are falling behind, and how delivery has changed over time.

---

## Key Features

| Feature | Description |
|---|---|
| 🗺️ India Welfare Map | Interactive dot map with state-level and district-level colour-coded scores |
| 📊 Dashboard Analytics | National score, KPI cards, top/bottom districts, year-over-year change |
| 📈 Trend Analysis | Year slider from 2018–2026, stacked bar, heatmap, indicator doughnut |
| ⚖️ District Comparison | Side-by-side comparison with bar chart, radar, doughnut, trend, and heatmap |
| 🔍 Search & Filter | Search by district/state name; filter by state and year |
| 📄 PDF Report | Print-ready welfare report per district (no external dependencies) |
| 🚩 Citizen Reports | Citizens can report welfare issues; admins review and respond |
| 📤 Dataset Upload | Data Analysts can upload CSVs, map columns, and run welfare analysis |
| 🔐 Role-based Auth | Admin, Researcher, Data Analyst, Citizen roles with different permissions |

---

## Tech Stack

- **Backend** — Python 3, Flask
- **Database** — SQLite (via `sqlite3`)
- **Frontend** — HTML5, CSS3, JavaScript (vanilla)
- **Charts** — Chart.js 4
- **Map** — Leaflet.js
- **Fonts & Icons** — Google Fonts (Bricolage Grotesque + Inter), Font Awesome 6

---

## Dataset Format

Upload CSV files with the following columns (column names are flexible — you map them during upload):

| Column | Description | Example |
|---|---|---|
| `State` | State name | Maharashtra |
| `District` | District name | Pune |
| `Year` | Data year | 2024 |
| `Education_Index` | Education & literacy score (0–100) | 72.4 |
| `Healthcare_Index` | Healthcare access score (0–100) | 68.1 |
| `Food_Security_Index` | Food security & nutrition score (0–100) | 65.0 |
| `Employment_Index` | Employment & income score (0–100) | 58.3 |

Higher values = better welfare delivery. All indicators should be normalised to 0–100.

---

## Welfare Score Formula

```
Welfare Score = 0.4 × Education
              + 0.3 × Healthcare
              + 0.2 × Food Security
              + 0.1 × Employment
```

**Score bands:**
- 80–100 → 🌟 Excellent
- 60–79  → ✅ Good
- 40–59  → ⚠️ Moderate
- 20–39  → 🔶 Weak
- 0–19   → 🚨 Critical

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/welfarewatch.git
cd welfarewatch
```

### 2. Install dependencies

```bash
pip install flask pandas werkzeug
```

> No other packages required. The PDF report feature uses native HTML print — no ReportLab needed.

### 3. Run the app

```bash
python app.py
```

Open your browser at `http://127.0.0.1:5000`

The database and tables are created automatically on first run. The official 2018–2026 dataset (450 records across 15 states) is also auto-imported on startup.

---

## Usage

### Viewing the Dashboard
1. Open the app and go to **Dashboard**
2. Use the year selector to switch between 2018–2026
3. The Key Insights panel shows the weakest indicator, year-over-year change, and districts needing support

### Uploading Your Own Dataset
1. Register or log in as a **Data Analyst**
2. Go to **Contribute Data**
3. Upload a CSV file
4. Map your columns to welfare indicators (State, District, Year, and 4 indicators)
5. Click **Run Analysis** — scores are computed automatically

### Comparing Districts
1. Go to **Compare Districts**
2. Select any two districts from the grouped dropdowns
3. View 5 chart types: bar chart, radar, trend line, doughnut, and heatmap

### Downloading a PDF Report
1. Search for any district in **Search Districts**
2. Click **PDF** in the results row
3. The print-ready report opens — click "Save as PDF / Print" to download

### Reporting an Issue
1. Go to **Report an Issue**
2. Select state, district, welfare scheme, and describe the problem
3. Admins review and update the status

---

## Demo Accounts

| Role | Username | Password |
|---|---|---|
| ⚙️ Admin | `admin` | `admin123` |
| 🔬 Researcher | `researcher1` | `demo123` |
| 📊 Data Analyst | `analyst1` | `demo123` |
| 👤 Citizen | `citizen1` | `demo123` |

---

## Project Structure

```
welfarewatch/
├── app.py                  # Main Flask app — all routes
├── risk_engine.py          # Welfare score calculation engine
├── commentary_engine.py    # Auto-generated district commentary
├── correlation_engine.py   # Indicator correlation analysis (backend)
├── database.db             # SQLite database (auto-created)
├── datasets/               # Uploaded CSV files
├── static/
│   ├── css/style.css       # Complete design system
│   └── js/
│       ├── charts.js       # Trend chart initialisation
│       ├── map.js          # Leaflet map with state+district dots
│       ├── dashboard.js    # Sidebar toggle, misc UI
│       └── theme.js        # Dark/light mode toggle
└── templates/              # Jinja2 HTML templates
    ├── base.html           # App shell (sidebar, topbar, footer)
    ├── home.html           # Landing page
    ├── dashboard.html      # Main analytics dashboard
    ├── risk_map.html       # India welfare map
    ├── trends.html         # Trend analysis page
    ├── compare.html        # District comparison
    ├── search.html         # Search with state/year filters
    ├── report_print.html   # Print-ready PDF report
    ├── admin.html          # Admin panel
    └── ...                 # Other pages
```

---

## Future Scope

- **Real-time data integration** — connect to government APIs (data.gov.in) for live updates
- **AI-based predictions** — forecast district welfare scores using ML models trained on historical data
- **SMS/WhatsApp alerts** — notify citizens when their district score drops below a threshold
- **Block-level granularity** — drill down below district to taluka/block level
- **Multilingual support** — Hindi, Tamil, Bengali and other regional languages
- **Mobile app** — React Native wrapper for the web dashboard

---

## License

MIT License — open data for a better India.

© 2026 WelfareWatch
# WelfareWatch
