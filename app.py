import os, json, sqlite3, io, csv
from functools import wraps
from flask import (Flask, render_template, redirect, url_for, flash,
                   request, jsonify, session, g, send_file, Response)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pandas as pd
from commentary_engine import generate_commentary, generate_state_commentary
from correlation_engine import compute_correlation_analysis
from risk_engine import (
    compute_welfare_score, categorize_welfare, analyze_dataframe,
    compute_insights, welfare_label,
    INDICATOR_LABELS, INDICATOR_WEIGHTS, INDICATOR_ICONS,
    INDICATOR_DESCRIPTIONS, SCORE_BANDS,
)

app = Flask(__name__)

@app.template_filter('clean_cols')
def clean_cols_filter(s):
    if not s: return ''
    import json
    try:
        return ', '.join(json.loads(s))
    except:
        return s.strip('[]').replace('"','').replace("'",'')

app.config['SECRET_KEY'] = 'welfarewatch-secret-2024'
app.config['DATABASE']   = os.path.join(os.path.dirname(__file__), 'database.db')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'datasets')
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Constants
INDIA_STATES = [
    'Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chhattisgarh',
    'Goa','Gujarat','Haryana','Himachal Pradesh','Jharkhand','Karnataka',
    'Kerala','Madhya Pradesh','Maharashtra','Manipur','Meghalaya','Mizoram',
    'Nagaland','Odisha','Punjab','Rajasthan','Sikkim','Tamil Nadu','Telangana',
    'Tripura','Uttar Pradesh','Uttarakhand','West Bengal',
    'Delhi','Jammu & Kashmir','Ladakh','Puducherry'
]
WELFARE_SCHEMES = [
    'MGNREGA (Job Guarantee)','PM-KISAN (Farmer Income)','NFSA / PDS (Ration)',
    'Ayushman Bharat (Health Insurance)','PM Awas Yojana (Housing)',
    'Ujjwala Yojana (LPG Gas)','Sukanya Samriddhi (Girl Child)',
    'PM Scholarship','Jal Jeevan Mission (Water)','Other'
]

ROLES = {
    'citizen': {
        'icon':'👤','label':'Citizen','color':'#14B8A6',
        'tagline':'Check your area & report issues',
        'features': {'dashboard':'simple','trends':'basic','compare':'simple',
                     'explorer':False,'download':False,'contribute':False,'api':False},
        'perks': ['View welfare scores for your state & district',
                  'Submit welfare issue reports',
                  'Track your submitted reports',
                  'View India Welfare Map',
                  'Basic district comparison'],
        'locked': ['Download datasets (CSV)','Full trend analysis',
                   'API access','Upload own datasets'],
    },
    'researcher': {
        'icon':'🔬','label':'Researcher','color':'#8B5CF6',
        'tagline':'Full data access + API for academic use',
        'features': {'dashboard':'full','trends':'full','compare':'full',
                     'explorer':True,'download':True,'contribute':False,'api':True},
        'perks': ['Everything in Citizen',
                  'Download all official datasets (CSV)',
                  'Full trend analysis with all 4 indicators',
                  'API access for data export',
                  'Export charts & comparisons'],
        'locked': ['Upload your own datasets','Run custom analysis'],
    },
    'data_analyst': {
        'icon':'📊','label':'Data Analyst','color':'#F59E0B',
        'tagline':'Full access + upload & run your own analysis',
        'features': {'dashboard':'full','trends':'full','compare':'full',
                     'explorer':True,'download':True,'contribute':True,'api':True},
        'perks': ['Everything in Researcher',
                  'Upload your own CSV datasets',
                  'Run welfare analysis on your data',
                  'Custom indicator name mapping'],
        'locked': [],
    },
    'admin': {
        'icon':'⚙️','label':'Admin','color':'#EF4444',
        'tagline':'Full platform control',
        'features': {'dashboard':'full','trends':'full','compare':'full',
                     'explorer':True,'download':True,'contribute':True,'api':True},
        'perks': ['Complete access to all features'],
        'locked': [],
    },
}

def get_features(user_type=None):
    return ROLES.get(user_type or 'citizen', ROLES['citizen'])['features']

app.jinja_env.globals.update(
    INDICATOR_LABELS=INDICATOR_LABELS, INDICATOR_WEIGHTS=INDICATOR_WEIGHTS,
    INDICATOR_ICONS=INDICATOR_ICONS, INDICATOR_DESCRIPTIONS=INDICATOR_DESCRIPTIONS,
    ROLES=ROLES, get_features=get_features,
    welfare_label=welfare_label, SCORE_BANDS=SCORE_BANDS,
    INDIA_STATES=INDIA_STATES, WELFARE_SCHEMES=WELFARE_SCHEMES,
)

# DB
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db: db.close()

def init_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'citizen',
        user_type TEXT DEFAULT 'citizen',
        state TEXT DEFAULT '',
        district TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        source TEXT DEFAULT '',
        domain TEXT DEFAULT '',
        filename TEXT NOT NULL,
        columns TEXT,
        indicator_names TEXT,
        row_count INTEGER DEFAULT 0,
        is_official INTEGER DEFAULT 0,
        uploaded_by INTEGER,
        uploaded_at TEXT DEFAULT (datetime('now')),
        active INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS citizen_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        state TEXT NOT NULL,
        district TEXT NOT NULL,
        scheme TEXT NOT NULL,
        issue_type TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        admin_note TEXT DEFAULT '',
        submitted_at TEXT DEFAULT (datetime('now')),
        reporter_id INTEGER
    );
    CREATE TABLE IF NOT EXISTS risk_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        state TEXT NOT NULL,
        district TEXT NOT NULL,
        year INTEGER NOT NULL,
        risk_score REAL DEFAULT 0,
        risk_category TEXT DEFAULT 'Moderate',
        indicator_1 REAL DEFAULT 0,
        indicator_2 REAL DEFAULT 0,
        indicator_3 REAL DEFAULT 0,
        indicator_4 REAL DEFAULT 0,
        dataset_id INTEGER,
        computed_at TEXT DEFAULT (datetime('now'))
    );
    """)
    for col_def in [
        "ALTER TABLE users ADD COLUMN user_type TEXT DEFAULT 'citizen'",
        "ALTER TABLE users ADD COLUMN state TEXT DEFAULT ''",
        "ALTER TABLE users ADD COLUMN district TEXT DEFAULT ''",
        "ALTER TABLE datasets ADD COLUMN description TEXT DEFAULT ''",
        "ALTER TABLE datasets ADD COLUMN source TEXT DEFAULT ''",
        "ALTER TABLE datasets ADD COLUMN domain TEXT DEFAULT ''",
        "ALTER TABLE datasets ADD COLUMN indicator_names TEXT",
        "ALTER TABLE datasets ADD COLUMN is_official INTEGER DEFAULT 0",
        "ALTER TABLE citizen_reports ADD COLUMN admin_note TEXT DEFAULT ''",
        "ALTER TABLE citizen_reports ADD COLUMN category TEXT DEFAULT ''",
        "ALTER TABLE citizen_reports ADD COLUMN severity TEXT DEFAULT 'Medium'",
        "ALTER TABLE citizen_reports ADD COLUMN impact TEXT DEFAULT 'Few (1-50)'",
    ]:
        try: db.execute(col_def)
        except: pass
    db.commit()
    db.close()

# Auth helpers
def login_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if 'user_id' not in session:
            flash('Please sign in to continue.', 'info')
            return redirect(url_for('auth_login', next=request.url))
        return f(*a, **kw)
    return dec

def admin_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if session.get('user_role') != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*a, **kw)
    return dec

def researcher_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if 'user_id' not in session:
            flash('Sign in to access this feature.', 'info')
            return redirect(url_for('auth_login'))
        if session.get('user_type', 'citizen') not in ('researcher', 'data_analyst', 'admin'):
            flash('Researcher or Data Analyst account required.', 'error')
            return redirect(url_for('upgrade'))
        return f(*a, **kw)
    return dec

def analyst_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if 'user_id' not in session:
            flash('Sign in to access this feature.', 'info')
            return redirect(url_for('auth_login'))
        if session.get('user_type', 'citizen') not in ('data_analyst', 'admin'):
            flash('Data Analyst account required.', 'error')
            return redirect(url_for('upgrade'))
        return f(*a, **kw)
    return dec

def current_user():
    if 'user_id' not in session: return None
    return {'id': session['user_id'], 'username': session.get('user_name', ''),
            'role': session.get('user_role', 'citizen'),
            'user_type': session.get('user_type', 'citizen')}

app.jinja_env.globals['current_user'] = current_user

# Auth routes
@app.route('/login', methods=['GET','POST'])
def auth_login():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        u, p = request.form.get('username','').strip(), request.form.get('password','')
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=?", (u,)).fetchone()
        if user and check_password_hash(user['password_hash'], p):
            session.update({'user_id': user['id'], 'user_name': user['username'],
                            'user_role': user['role'],
                            'user_type': user['user_type'] or 'citizen'})
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(request.args.get('next') or url_for('dashboard'))
        flash('Incorrect username or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def auth_register():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        email    = request.form.get('email','').strip()
        password = request.form.get('password','')
        confirm  = request.form.get('confirm_password','')
        user_type= request.form.get('user_type','citizen')
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')
        db = get_db()
        if db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone():
            flash('Username already taken.', 'error')
            return render_template('register.html')
        if db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        db.execute("INSERT INTO users (username,email,password_hash,role,user_type,state,district) VALUES (?,?,?,?,?,?,?)",
            (username, email, generate_password_hash(password), 'citizen', user_type,
             request.form.get('state',''), request.form.get('district','')))
        db.commit()
        flash(f'Account created as {ROLES[user_type]["label"]}! Please sign in.', 'success')
        return redirect(url_for('auth_login'))
    return render_template('register.html')

@app.route('/logout')
def auth_logout():
    name = session.get('user_name','')
    session.clear()
    flash(f'Signed out. See you soon{", "+name if name else ""}!', 'info')
    return redirect(url_for('home'))

# Home
@app.route('/')
def home():
    db = get_db()
    total_districts = db.execute("SELECT COUNT(DISTINCT district) FROM risk_records").fetchone()[0]
    total_states    = db.execute("SELECT COUNT(DISTINCT state) FROM risk_records").fetchone()[0]
    total_reports   = db.execute("SELECT COUNT(*) FROM citizen_reports").fetchone()[0]
    latest_year = db.execute("SELECT MAX(year) y FROM risk_records").fetchone()['y'] or 2026
    nat_score = db.execute("SELECT ROUND(AVG(risk_score),1) avg FROM risk_records WHERE year=?",
                           (latest_year,)).fetchone()['avg'] or 0
    nat_2023  = db.execute("SELECT ROUND(AVG(risk_score),1) avg FROM risk_records WHERE year=2023").fetchone()['avg'] or 0
    at_risk  = db.execute("SELECT state,ROUND(AVG(risk_score),1) avg FROM risk_records WHERE year=? GROUP BY state ORDER BY avg ASC  LIMIT 3", (latest_year,)).fetchall()
    best     = db.execute("SELECT state,ROUND(AVG(risk_score),1) avg FROM risk_records WHERE year=? GROUP BY state ORDER BY avg DESC LIMIT 3", (latest_year,)).fetchall()
    datasets = db.execute("SELECT COUNT(*) FROM datasets WHERE is_official=0").fetchone()[0]
    years_avail = [r['year'] for r in db.execute("SELECT DISTINCT year FROM risk_records ORDER BY year").fetchall()]
    return render_template('home.html',
        total_districts=total_districts, total_states=total_states,
        total_reports=total_reports, nat_2023=nat_2023,
        nat_score=nat_score, latest_year=latest_year,
        nat_wl=welfare_label(nat_score), at_risk=at_risk, best=best,
        datasets=datasets, years_avail=years_avail)

# Dashboard
@app.route('/dashboard')
def dashboard():
    db  = get_db()
    cu  = current_user()
    utype = cu['user_type'] if cu else 'citizen'
    feats = get_features(utype)

    total_states    = db.execute("SELECT COUNT(DISTINCT state)    FROM risk_records").fetchone()[0]
    total_districts = db.execute("SELECT COUNT(DISTINCT district) FROM risk_records").fetchone()[0]
    total_reports   = db.execute("SELECT COUNT(*) FROM citizen_reports").fetchone()[0]
    pending_reports = db.execute("SELECT COUNT(*) FROM citizen_reports WHERE status='pending'").fetchone()[0]

    latest_year = db.execute("SELECT MAX(year) y FROM risk_records").fetchone()['y'] or 2026
    sel_year    = request.args.get('year', type=int, default=latest_year)
    years_avail = [r['year'] for r in db.execute("SELECT DISTINCT year FROM risk_records ORDER BY year").fetchall()]

    # Category counts for selected year
    cat_counts = {}
    for cat in ['Excellent','Good','Moderate','Weak','Critical']:
        cat_counts[cat] = db.execute(
            "SELECT COUNT(DISTINCT district) FROM risk_records WHERE risk_category=? AND year=?",
            (cat, sel_year)).fetchone()[0]

    nat_avg = db.execute(
        "SELECT ROUND(AVG(risk_score),1) avg FROM risk_records WHERE year=?",
        (sel_year,)).fetchone()['avg'] or 0
    wl = welfare_label(nat_avg)

    # State bar — sorted best first for selected year
    state_rows = db.execute("""SELECT state, ROUND(AVG(risk_score),1) avg
        FROM risk_records WHERE year=? GROUP BY state ORDER BY avg DESC LIMIT 15""",
        (sel_year,)).fetchall()

    def score_color(s):
        if s >= 80: return '#10B981'
        if s >= 60: return '#3B82F6'
        if s >= 40: return '#F59E0B'
        if s >= 20: return '#F97316'
        return '#EF4444'

    state_bar = {
        'labels': [r['state'] for r in state_rows],
        'scores': [r['avg'] for r in state_rows],
        'colors': [score_color(r['avg']) for r in state_rows],
    }

    year_rows = db.execute("""SELECT year, ROUND(AVG(risk_score),1) avg,
        ROUND(AVG(indicator_1),1) i1, ROUND(AVG(indicator_2),1) i2,
        ROUND(AVG(indicator_3),1) i3, ROUND(AVG(indicator_4),1) i4
        FROM risk_records GROUP BY year ORDER BY year""").fetchall()
    trend = {
        'years':  [r['year'] for r in year_rows],
        'scores': [r['avg'] for r in year_rows],
        'i1': [r['i1'] for r in year_rows], 'i2': [r['i2'] for r in year_rows],
        'i3': [r['i3'] for r in year_rows], 'i4': [r['i4'] for r in year_rows],
    }

    ind_avgs = db.execute("""SELECT ROUND(AVG(indicator_1),1) i1, ROUND(AVG(indicator_2),1) i2,
        ROUND(AVG(indicator_3),1) i3, ROUND(AVG(indicator_4),1) i4
        FROM risk_records WHERE year=?""", (sel_year,)).fetchone()

    # Most improved vs previous year
    prev_year = sel_year - 1
    improved = db.execute(f"""
        SELECT a.district, a.state,
               ROUND(a.risk_score,1) s23, ROUND(b.risk_score,1) s22,
               ROUND(a.risk_score - b.risk_score, 1) delta
        FROM risk_records a JOIN risk_records b ON a.district=b.district
        WHERE a.year={sel_year} AND b.year={prev_year}
        GROUP BY a.district ORDER BY delta DESC LIMIT 5
    """).fetchall()

    weakest = db.execute("""SELECT district, state, ROUND(AVG(risk_score),1) avg
        FROM risk_records WHERE year=? GROUP BY district ORDER BY avg ASC LIMIT 5
    """, (sel_year,)).fetchall()

    top_districts = db.execute("""SELECT district, state, ROUND(AVG(risk_score),1) avg
        FROM risk_records WHERE year=? GROUP BY district ORDER BY avg DESC LIMIT 5
    """, (sel_year,)).fetchall()

    recent_reports = db.execute(
        "SELECT * FROM citizen_reports ORDER BY submitted_at DESC LIMIT 5").fetchall()
    datasets = db.execute(
        "SELECT id,name FROM datasets WHERE active=1 ORDER BY is_official DESC,uploaded_at DESC").fetchall()
    sel_ds = request.args.get('dataset', type=int)

    # Report insights for dashboard
    report_insights = {}
    try:
        for cat in ['Education', 'Healthcare', 'Food Security', 'Employment']:
            report_insights[cat] = db.execute(
                "SELECT COUNT(*) n FROM citizen_reports WHERE category=?", (cat,)
            ).fetchone()['n']
        report_insights['high_severity'] = db.execute(
            "SELECT COUNT(*) n FROM citizen_reports WHERE severity='High'"
        ).fetchone()['n']
        report_insights['total'] = db.execute(
            "SELECT COUNT(*) n FROM citizen_reports"
        ).fetchone()['n']
        # Districts with many HIGH severity reports → ground signal
        ground_signal_districts = db.execute("""
            SELECT district, state, COUNT(*) n FROM citizen_reports
            WHERE severity='High' GROUP BY district, state
            HAVING n >= 2 ORDER BY n DESC LIMIT 5
        """).fetchall()
        report_insights['ground_signal'] = [
            {'district': r['district'], 'state': r['state'], 'count': r['n']}
            for r in ground_signal_districts
        ]
    except Exception:
        report_insights = {'ground_signal': []}

    # Key Insights Panel
    # Lowest performing indicator
    ind_names = {
        'i1': 'Education & Literacy', 'i2': 'Healthcare Access',
        'i3': 'Food Security',        'i4': 'Employment & Income'
    }
    ind_vals = {
        'i1': ind_avgs['i1'] or 0, 'i2': ind_avgs['i2'] or 0,
        'i3': ind_avgs['i3'] or 0, 'i4': ind_avgs['i4'] or 0,
    }
    lowest_ind_key  = min(ind_vals, key=ind_vals.get)
    highest_ind_key = max(ind_vals, key=ind_vals.get)
    lowest_ind  = {'name': ind_names[lowest_ind_key],  'score': ind_vals[lowest_ind_key]}
    highest_ind = {'name': ind_names[highest_ind_key], 'score': ind_vals[highest_ind_key]}

    needs_improvement_count = db.execute(
        "SELECT COUNT(DISTINCT district) n FROM risk_records WHERE year=? AND risk_score < 60",
        (sel_year,)).fetchone()['n']
    excellent_count = cat_counts.get('Excellent', 0) + cat_counts.get('Good', 0)

    # Year-over-year change in national score
    prev_nat = db.execute(
        "SELECT ROUND(AVG(risk_score),1) avg FROM risk_records WHERE year=?",
        (sel_year - 1,)).fetchone()['avg'] or nat_avg
    yoy_change = round(nat_avg - prev_nat, 1)

    key_insights = {
        'lowest_ind': lowest_ind,
        'highest_ind': highest_ind,
        'needs_improvement': needs_improvement_count,
        'excellent_count': excellent_count,
        'yoy_change': yoy_change,
        'nat_avg': nat_avg,
    }

    # Enhanced top/bottom 5 with state filter
    top5 = db.execute("""
        SELECT district, state, ROUND(AVG(risk_score),1) avg,
               ROUND(AVG(indicator_1),1) i1, ROUND(AVG(indicator_2),1) i2,
               ROUND(AVG(indicator_3),1) i3, ROUND(AVG(indicator_4),1) i4
        FROM risk_records WHERE year=?
        GROUP BY district ORDER BY avg DESC LIMIT 5
    """, (sel_year,)).fetchall()
    bottom5 = db.execute("""
        SELECT district, state, ROUND(AVG(risk_score),1) avg,
               ROUND(AVG(indicator_1),1) i1, ROUND(AVG(indicator_2),1) i2,
               ROUND(AVG(indicator_3),1) i3, ROUND(AVG(indicator_4),1) i4
        FROM risk_records WHERE year=?
        GROUP BY district ORDER BY avg ASC LIMIT 5
    """, (sel_year,)).fetchall()
    corr_insights = []
    try:
        corr_records = db.execute("""
            SELECT indicator_1, indicator_2, indicator_3, indicator_4, risk_score
            FROM risk_records WHERE year=?
        """, (sel_year,)).fetchall()
        corr_records = [dict(r) for r in corr_records]
        if len(corr_records) >= 10:
            analysis = compute_correlation_analysis(corr_records)
            if analysis and analysis.get('correlations'):
                for pair, val in sorted(analysis['correlations'].items(),
                                        key=lambda x: abs(x[1]), reverse=True)[:3]:
                    parts = pair.split('_vs_')
                    if len(parts) == 2:
                        label_map = {
                            'indicator_1': 'Education', 'indicator_2': 'Healthcare',
                            'indicator_3': 'Food Security', 'indicator_4': 'Employment',
                            'risk_score': 'Overall Score'
                        }
                        a_lbl = label_map.get(parts[0], parts[0])
                        b_lbl = label_map.get(parts[1], parts[1])
                        strength = 'strong' if abs(val) > 0.7 else 'moderate' if abs(val) > 0.4 else 'weak'
                        direction = 'positive' if val > 0 else 'negative'
                        corr_insights.append({
                            'pair': f'{a_lbl} ↔ {b_lbl}',
                            'value': round(val, 2),
                            'strength': strength,
                            'direction': direction,
                            'color': '#10B981' if val > 0.4 else '#EF4444' if val < -0.4 else '#F59E0B'
                        })
    except Exception:
        pass

    return render_template('dashboard.html',
        total_states=total_states, total_districts=total_districts,
        total_reports=total_reports, pending_reports=pending_reports,
        cat_counts=cat_counts, nat_avg=nat_avg, wl=wl,
        feats=feats, utype=utype,
        state_bar=json.dumps(state_bar), trend=json.dumps(trend),
        ind_avgs=ind_avgs, improved=improved,
        weakest=weakest, top_districts=top_districts,
        top5=top5, bottom5=bottom5,
        recent_reports=recent_reports, datasets=datasets, sel_ds=sel_ds,
        cat_json=json.dumps(cat_counts),
        sel_year=sel_year, latest_year=latest_year, years_avail=years_avail,
        corr_insights=corr_insights,
        key_insights=key_insights,
        report_insights=report_insights)

# Risk Map
@app.route('/risk-map')
def risk_map():
    db = get_db()
    rows = db.execute("""SELECT state, ROUND(AVG(risk_score),1) avg,
        COUNT(DISTINCT district) cnt,
        ROUND(AVG(indicator_1),1) i1, ROUND(AVG(indicator_2),1) i2,
        ROUND(AVG(indicator_3),1) i3, ROUND(AVG(indicator_4),1) i4
        FROM risk_records GROUP BY state""").fetchall()
    state_data = {}
    for r in rows:
        wl = welfare_label(r['avg'])
        state_data[r['state']] = {
            'score': r['avg'], 'label': wl['label'], 'color': wl['color'],
            'cls': wl['cls'], 'count': r['cnt'],
            'i1': r['i1'], 'i2': r['i2'], 'i3': r['i3'], 'i4': r['i4'],
        }
    return render_template('risk_map.html', state_data=json.dumps(state_data))

# Explorer
@app.route('/explorer')
def explorer():
    db  = get_db()
    cu  = current_user()
    feats = get_features(cu['user_type'] if cu else None)
    datasets = db.execute("SELECT * FROM datasets WHERE active=1 AND is_official=0 ORDER BY uploaded_at DESC").fetchall()
    return render_template('explorer.html', datasets=datasets, feats=feats)

@app.route('/explorer/<int:dataset_id>')
def explorer_detail(dataset_id):
    db  = get_db()
    cu  = current_user()
    feats = get_features(cu['user_type'] if cu else None)
    dataset = db.execute("SELECT * FROM datasets WHERE id=?", (dataset_id,)).fetchone()
    if not dataset: flash('Dataset not found.','error'); return redirect(url_for('explorer'))
    columns  = json.loads(dataset['columns']) if dataset['columns'] else []
    ind_names= json.loads(dataset['indicator_names']) if dataset['indicator_names'] else {}
    try:
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], dataset['filename']), nrows=25)
        preview = df.fillna('').to_dict(orient='records')
        stats = {col: {'min': round(float(df[col].min()),1), 'max': round(float(df[col].max()),1),
                       'mean': round(float(df[col].mean()),1)} 
                 for col in df.select_dtypes(include='number').columns}
    except: preview = []; stats = {}
    return render_template('explorer_detail.html', dataset=dataset,
        columns=columns, preview=preview, ind_names=ind_names,
        feats=feats, stats=stats)

@app.route('/explorer/<int:dataset_id>/download')
@researcher_required
def download_dataset(dataset_id):
    db = get_db()
    ds = db.execute("SELECT * FROM datasets WHERE id=?", (dataset_id,)).fetchone()
    if not ds: flash('Not found.','error'); return redirect(url_for('explorer'))
    fp = os.path.join(app.config['UPLOAD_FOLDER'], ds['filename'])
    if not os.path.exists(fp): flash('File unavailable.','error'); return redirect(url_for('explorer'))
    return send_file(fp, as_attachment=True, download_name=ds['filename'])

# Compare
@app.route('/compare', methods=['GET','POST'])
def compare():
    db   = get_db()
    cu   = current_user()
    feats= get_features(cu['user_type'] if cu else None)

    # Group districts by state for optgroup
    state_districts = {}
    rows = db.execute("SELECT DISTINCT state, district FROM risk_records ORDER BY state, district").fetchall()
    for r in rows:
        state_districts.setdefault(r['state'], []).append(r['district'])

    comp_data = comparison = trend_chart = radar_data = None
    district_a = district_b = state_a = state_b = None

    if request.method == 'POST':
        district_a = request.form.get('district_a')
        district_b = request.form.get('district_b')
        if district_a and district_b and district_a != district_b:
            def get_full(d):
                r = db.execute("""SELECT AVG(indicator_1) i1, AVG(indicator_2) i2,
                    AVG(indicator_3) i3, AVG(indicator_4) i4, AVG(risk_score) rs, state
                    FROM risk_records WHERE district=? GROUP BY state""", (d,)).fetchone()
                if not r: return {}
                s = round(r['rs'] or 0, 1)
                return {
                    'indicator_1': round(r['i1'] or 0, 1), 'indicator_2': round(r['i2'] or 0, 1),
                    'indicator_3': round(r['i3'] or 0, 1), 'indicator_4': round(r['i4'] or 0, 1),
                    'risk_score': s, 'state': r['state'], 'wl': welfare_label(s),
                }
            comp_data = {district_a: get_full(district_a), district_b: get_full(district_b)}
            if comp_data.get(district_a): state_a = comp_data[district_a].get('state','')
            if comp_data.get(district_b): state_b = comp_data[district_b].get('state','')

            da, db2 = comp_data.get(district_a,{}), comp_data.get(district_b,{})
            ind_labels = list(INDICATOR_LABELS.values())
            comparison = json.dumps({
                'labels': ind_labels + ['Overall Score'],
                'a': {'name': district_a, 'values': [
                    da.get('indicator_1',0), da.get('indicator_2',0),
                    da.get('indicator_3',0), da.get('indicator_4',0), da.get('risk_score',0)]},
                'b': {'name': district_b, 'values': [
                    db2.get('indicator_1',0), db2.get('indicator_2',0),
                    db2.get('indicator_3',0), db2.get('indicator_4',0), db2.get('risk_score',0)]},
            })
            # Radar chart data (4 indicators only)
            radar_data = json.dumps({
                'labels': ind_labels,
                'a': {'name': district_a, 'values': [
                    da.get('indicator_1',0), da.get('indicator_2',0),
                    da.get('indicator_3',0), da.get('indicator_4',0)]},
                'b': {'name': district_b, 'values': [
                    db2.get('indicator_1',0), db2.get('indicator_2',0),
                    db2.get('indicator_3',0), db2.get('indicator_4',0)]},
            })
            def get_trend(d):
                rows = get_db().execute("""SELECT year, ROUND(AVG(risk_score),1) rs
                    FROM risk_records WHERE district=? GROUP BY year ORDER BY year""",(d,)).fetchall()
                return {'years':[r['year'] for r in rows],'scores':[r['rs'] for r in rows]}
            trend_chart = json.dumps({
                'a': {'name': district_a, **get_trend(district_a)},
                'b': {'name': district_b, **get_trend(district_b)},
            })

            # Difference summary
            ind_label_map = {
                'indicator_1': 'Education & Literacy',
                'indicator_2': 'Healthcare Access',
                'indicator_3': 'Food Security',
                'indicator_4': 'Employment & Income',
            }
            diff_summary = []
            for ind_key, ind_label in ind_label_map.items():
                val_a = da.get(ind_key, 0)
                val_b = db2.get(ind_key, 0)
                diff  = round(val_a - val_b, 1)
                if diff != 0:
                    leader   = district_a if diff > 0 else district_b
                    trailer  = district_b if diff > 0 else district_a
                    abs_diff = abs(diff)
                    pct_diff = round(abs_diff / max(val_b if diff > 0 else val_a, 1) * 100, 1)
                    diff_summary.append({
                        'indicator': ind_label,
                        'leader': leader,
                        'trailer': trailer,
                        'diff': abs_diff,
                        'pct': pct_diff,
                        'val_a': val_a,
                        'val_b': val_b,
                    })
            # Sort by biggest gap first
            diff_summary.sort(key=lambda x: x['diff'], reverse=True)

            overall_diff = round(da.get('risk_score', 0) - db2.get('risk_score', 0), 1)
            overall_leader = district_a if overall_diff >= 0 else district_b
            overall_gap    = abs(overall_diff)

    return render_template('compare.html',
        state_districts=state_districts, comparison=comparison,
        trend_chart=trend_chart, radar_data=radar_data,
        district_a=district_a, district_b=district_b,
        comp_data=comp_data, state_a=state_a, state_b=state_b, feats=feats,
        diff_summary=diff_summary if comparison else [],
        overall_leader=overall_leader if comparison else '',
        overall_gap=overall_gap if comparison else 0)

# Trends
@app.route('/trends')
def trends():
    db = get_db()
    cu = current_user()
    feats = get_features(cu['user_type'] if cu else None)
    years  = [r['year']  for r in db.execute("SELECT DISTINCT year  FROM risk_records ORDER BY year").fetchall()]
    states = [r['state'] for r in db.execute("SELECT DISTINCT state FROM risk_records ORDER BY state").fetchall()]

    # Trend insight text
    trend_insight = {}
    if len(years) >= 2:
        first_yr, last_yr = years[0], years[-1]
        score_first = db.execute(
            "SELECT ROUND(AVG(risk_score),1) a FROM risk_records WHERE year=?", (first_yr,)
        ).fetchone()['a'] or 0
        score_last = db.execute(
            "SELECT ROUND(AVG(risk_score),1) a FROM risk_records WHERE year=?", (last_yr,)
        ).fetchone()['a'] or 0
        # Pct change relative to first year
        pct_change = round(((score_last - score_first) / score_first * 100), 1) if score_first else 0
        # Compare to 5 years ago (or earliest available)
        five_yr_ago = max(years[0], last_yr - 5)
        score_5ago = db.execute(
            "SELECT ROUND(AVG(risk_score),1) a FROM risk_records WHERE year=?", (five_yr_ago,)
        ).fetchone()['a'] or score_first
        pct_5yr = round(((score_last - score_5ago) / score_5ago * 100), 1) if score_5ago else 0

        # Best and worst year
        yr_avgs = db.execute(
            "SELECT year, ROUND(AVG(risk_score),1) a FROM risk_records GROUP BY year ORDER BY a DESC"
        ).fetchall()
        best_yr  = yr_avgs[0]['year']  if yr_avgs else last_yr
        worst_yr = yr_avgs[-1]['year'] if yr_avgs else first_yr

        # Most improved state overall
        improved_states = db.execute("""
            SELECT a.state, ROUND(a.avg_s - b.avg_s, 1) delta
            FROM (SELECT state, AVG(risk_score) avg_s FROM risk_records WHERE year=? GROUP BY state) a
            JOIN (SELECT state, AVG(risk_score) avg_s FROM risk_records WHERE year=? GROUP BY state) b
              ON a.state=b.state
            ORDER BY delta DESC LIMIT 1
        """, (last_yr, first_yr)).fetchone()

        trend_insight = {
            'first_yr': first_yr, 'last_yr': last_yr,
            'score_first': score_first, 'score_last': score_last,
            'pct_change': pct_change, 'pct_5yr': pct_5yr,
            'five_yr_ago': five_yr_ago,
            'direction': 'improved' if pct_change > 0 else 'declined',
            'direction_5yr': 'improved' if pct_5yr > 0 else 'declined',
            'best_yr': best_yr, 'worst_yr': worst_yr,
            'most_improved_state': improved_states['state'] if improved_states else '—',
            'most_improved_delta': improved_states['delta'] if improved_states else 0,
        }

    return render_template('trends.html', years=years, states=states, feats=feats,
                           utype=cu['user_type'] if cu else 'citizen',
                           trend_insight=trend_insight)

@app.route('/api/heatmap-data')
def api_heatmap_data():
    """Return state × year matrix for heatmap."""
    db      = get_db()
    state_f = request.args.get('state', '').strip()
    if state_f:
        rows = db.execute("""SELECT state, year, ROUND(AVG(risk_score),1) avg
            FROM risk_records WHERE state=? GROUP BY state, year ORDER BY state, year""",
            (state_f,)).fetchall()
    else:
        rows = db.execute("""SELECT state, year, ROUND(AVG(risk_score),1) avg
            FROM risk_records GROUP BY state, year ORDER BY state, year""").fetchall()
    result = {}
    for r in rows:
        result.setdefault(r['state'], {})[str(r['year'])] = r['avg']
    return jsonify(result)

@app.route('/api/search-suggest')
def api_search_suggest():
    q = request.args.get('q','').strip()
    if len(q) < 2: return jsonify([])
    db = get_db()
    like = f'%{q}%'
    rows = db.execute("""SELECT district, state, ROUND(AVG(risk_score),1) avg, risk_category
        FROM risk_records WHERE district LIKE ? OR state LIKE ?
        GROUP BY district, state ORDER BY avg DESC LIMIT 10""", (like, like)).fetchall()
    return jsonify([{'district': r['district'], 'state': r['state'],
                     'avg': r['avg'], 'category': r['risk_category']} for r in rows])

@app.route('/api/trends')
def api_trends():
    from risk_engine import compute_insights
    db = get_db()
    year_max = request.args.get('year', type=int, default=2023)
    state_f  = request.args.get('state','').strip()
    district_f = request.args.get('district','').strip()

    params = []; cond = f"WHERE year <= {year_max}"
    if state_f:    cond += " AND state = ?";    params.append(state_f)
    if district_f: cond += " AND district = ?"; params.append(district_f)

    yearly = db.execute(f"""SELECT year,
        ROUND(AVG(risk_score),1) avg,
        ROUND(AVG(indicator_1),1) i1, ROUND(AVG(indicator_2),1) i2,
        ROUND(AVG(indicator_3),1) i3, ROUND(AVG(indicator_4),1) i4
        FROM risk_records {cond} GROUP BY year ORDER BY year""", params).fetchall()

    state_avgs = db.execute(f"""SELECT state, ROUND(AVG(risk_score),1) avg
        FROM risk_records {cond} GROUP BY state ORDER BY avg DESC LIMIT 15""", params).fetchall()

    yt = {str(r['year']): {'avg':r['avg'],'i1':r['i1'],'i2':r['i2'],'i3':r['i3'],'i4':r['i4']}
          for r in yearly}
    year_scores = {str(yr): vals['avg'] for yr, vals in yt.items()}
    insights = compute_insights(year_scores)

    return jsonify({
        'yearly_trend': yt,
        'state_data':   {r['state']: r['avg'] for r in state_avgs},
        'ind_labels':   list(INDICATOR_LABELS.values()),
        'insights':     insights,
    })

# Report
@app.route('/report', methods=['GET','POST'])
def report():
    if request.method == 'POST':
        db = get_db()
        db.execute("""INSERT INTO citizen_reports
            (state,district,scheme,issue_type,description,reporter_id,category,severity,impact)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (request.form.get('state',''),
             request.form.get('district',''),
             request.form.get('category',''),          # scheme field reused for category (backward compat)
             request.form.get('category',''),           # issue_type kept for compat
             request.form.get('description',''),
             session.get('user_id'),
             request.form.get('category',''),
             request.form.get('severity','Medium'),
             request.form.get('impact','Few (1-50)')))
        db.commit()
        flash('✅ Report submitted! Thank you for helping improve welfare delivery.','success')
        return redirect(url_for('my_reports') if 'user_id' in session else url_for('report'))
    return render_template('report.html')

@app.route('/my-reports')
@login_required
def my_reports():
    db = get_db()
    reports = db.execute(
        "SELECT * FROM citizen_reports WHERE reporter_id=? ORDER BY submitted_at DESC",
        (session['user_id'],)).fetchall()
    return render_template('my_reports.html', reports=reports)

# Methodology
@app.route('/methodology')
def methodology():
    return render_template('methodology.html')

# Upgrade
@app.route('/upgrade', methods=['GET','POST'])
def upgrade():
    if request.method == 'POST' and 'user_id' in session:
        new_type = request.form.get('user_type','citizen')
        if new_type in ROLES and new_type != 'admin':
            db = get_db()
            db.execute("UPDATE users SET user_type=? WHERE id=?", (new_type, session['user_id']))
            db.commit()
            session['user_type'] = new_type
            flash(f'Account upgraded to {ROLES[new_type]["label"]}!','success')
            return redirect(url_for('dashboard'))
    return render_template('upgrade.html', cu=current_user())

# Contribute
@app.route('/contribute/delete/<int:dataset_id>', methods=['POST'])
@analyst_required
def delete_own_dataset(dataset_id):
    db = get_db()
    ds = db.execute("SELECT * FROM datasets WHERE id=? AND uploaded_by=?",
                    (dataset_id, session['user_id'])).fetchone()
    if not ds:
        flash('Dataset not found or not yours.', 'error')
        return redirect(url_for('contribute'))
    db.execute("DELETE FROM risk_records WHERE dataset_id=?", (dataset_id,))
    db.execute("DELETE FROM datasets WHERE id=?", (dataset_id,))
    db.commit()
    fp = os.path.join(app.config['UPLOAD_FOLDER'], ds['filename'])
    if os.path.exists(fp):
        try: os.remove(fp)
        except: pass
    flash(f'Dataset "{ds["name"]}" deleted.', 'success')
    return redirect(url_for('contribute'))

@app.route('/contribute', methods=['GET','POST'])
@analyst_required
def contribute():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected.','error'); return redirect(url_for('contribute'))
        f = request.files['file']
        if not f or not f.filename.endswith('.csv'):
            flash('CSV files only.','error'); return redirect(url_for('contribute'))
        filename = secure_filename(f'contrib_{session["user_id"]}_{f.filename}')
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(filepath)
        try:
            df = pd.read_csv(filepath); columns = json.dumps(list(df.columns)); rc = len(df)
        except: columns='[]'; rc=0
        db = get_db()
        db.execute("INSERT INTO datasets (name,description,filename,columns,row_count,is_official,uploaded_by) VALUES (?,?,?,?,?,0,?)",
            (request.form.get('name',f.filename), request.form.get('description',''), filename, columns, rc, session['user_id']))
        db.commit()
        flash(f'Dataset uploaded — {rc:,} rows detected.','success')
        return redirect(url_for('contribute'))
    db = get_db()
    my_ds = db.execute("SELECT * FROM datasets WHERE uploaded_by=? ORDER BY uploaded_at DESC", (session['user_id'],)).fetchall()
    return render_template('contribute.html', my_datasets=my_ds)

@app.route('/contribute/analyze/<int:dataset_id>', methods=['POST'])
@analyst_required
def analyst_analyze(dataset_id):
    db = get_db()
    ds = db.execute("SELECT * FROM datasets WHERE id=? AND uploaded_by=?", (dataset_id, session['user_id'])).fetchone()
    if not ds: flash('Not found.','error'); return redirect(url_for('contribute'))
    col_map = {k: request.form.get(v) or '' for k,v in [
        ('state','col_state'),('district','col_district'),('year','col_year'),
        ('indicator_1','col_i1'),('indicator_2','col_i2'),('indicator_3','col_i3'),('indicator_4','col_i4')]}
    ind_names = json.dumps({
        'indicator_1': request.form.get('name_i1') or INDICATOR_LABELS['indicator_1'],
        'indicator_2': request.form.get('name_i2') or INDICATOR_LABELS['indicator_2'],
        'indicator_3': request.form.get('name_i3') or INDICATOR_LABELS['indicator_3'],
        'indicator_4': request.form.get('name_i4') or INDICATOR_LABELS['indicator_4'],
    })
    try:
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], ds['filename']))
        results = analyze_dataframe(df, col_map)
        db.execute("DELETE FROM risk_records WHERE dataset_id=?", (dataset_id,))
        db.executemany("""INSERT INTO risk_records
            (state,district,year,indicator_1,indicator_2,indicator_3,indicator_4,
             risk_score,risk_category,dataset_id) VALUES (?,?,?,?,?,?,?,?,?,?)""",
            [(r['state'],r['district'],r['year'],r['indicator_1'],r['indicator_2'],
              r['indicator_3'],r['indicator_4'],r['risk_score'],r['risk_category'],dataset_id)
             for r in results])
        db.execute("UPDATE datasets SET indicator_names=? WHERE id=?", (ind_names, dataset_id))
        db.commit()
        flash(f'Analysis complete — {len(results):,} records processed.','success')
    except Exception as e: flash(f'Analysis failed: {str(e)}','error')
    return redirect(url_for('contribute'))

# State Profile
@app.route('/state/<state_name>')
def state_profile(state_name):
    db = get_db()
    districts = db.execute("""SELECT district, ROUND(AVG(risk_score),1) avg,
        ROUND(AVG(indicator_1),1) i1, ROUND(AVG(indicator_2),1) i2,
        ROUND(AVG(indicator_3),1) i3, ROUND(AVG(indicator_4),1) i4
        FROM risk_records WHERE state=? GROUP BY district ORDER BY avg DESC""",
        (state_name,)).fetchall()
    if not districts: flash(f'No data for {state_name}.','error'); return redirect(url_for('risk_map'))
    yearly = db.execute("SELECT year, ROUND(AVG(risk_score),1) avg FROM risk_records WHERE state=? GROUP BY year ORDER BY year", (state_name,)).fetchall()
    state_avg = db.execute("SELECT ROUND(AVG(risk_score),1) avg FROM risk_records WHERE state=?", (state_name,)).fetchone()['avg'] or 0
    wl = welfare_label(state_avg)
    state_reports = db.execute("SELECT * FROM citizen_reports WHERE state=? ORDER BY submitted_at DESC LIMIT 5", (state_name,)).fetchall()
    trend = {'years':[r['year'] for r in yearly],'scores':[r['avg'] for r in yearly]}
    return render_template('state_profile.html',
        state_name=state_name, districts=districts, state_avg=state_avg,
        wl=wl, trend=json.dumps(trend), state_reports=state_reports)

# Search
@app.route('/search')
def search():
    q          = request.args.get('q', '').strip()
    state_f    = request.args.get('state', '').strip()
    year_f     = request.args.get('year', type=int, default=0)
    db         = get_db()
    results    = []
    all_states = [r['state'] for r in db.execute("SELECT DISTINCT state FROM risk_records ORDER BY state").fetchall()]
    all_years  = [r['year']  for r in db.execute("SELECT DISTINCT year  FROM risk_records ORDER BY year DESC").fetchall()]

    conditions = []
    params     = []

    if q and len(q) >= 2:
        conditions.append("(r.district LIKE ? OR r.state LIKE ?)")
        params.extend([f'%{q}%', f'%{q}%'])
    if state_f:
        conditions.append("r.state = ?")
        params.append(state_f)
    if year_f:
        conditions.append("r.year = ?")
        params.append(year_f)

    if conditions or state_f or year_f:
        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        results = db.execute(f"""
            SELECT r.district, r.state,
                   ROUND(AVG(r.risk_score),1) avg, r.risk_category
            FROM risk_records r {where}
            GROUP BY r.district, r.state
            ORDER BY avg DESC LIMIT 30
        """, params).fetchall()

    return render_template('search.html', q=q, results=results,
                           state_f=state_f, year_f=year_f,
                           all_states=all_states, all_years=all_years)

# Export
@app.route('/export/dashboard')
@researcher_required
def export_dashboard():
    """Export dashboard summary as CSV."""
    db = get_db()
    rows = db.execute("""SELECT state, ROUND(AVG(risk_score),1) welfare_score,
        ROUND(AVG(indicator_1),1) education, ROUND(AVG(indicator_2),1) healthcare,
        ROUND(AVG(indicator_3),1) food_security, ROUND(AVG(indicator_4),1) employment,
        risk_category
        FROM risk_records WHERE year=2023 GROUP BY state ORDER BY welfare_score DESC
    """).fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['State','Welfare Score','Education','Healthcare','Food Security','Employment','Category'])
    for r in rows:
        writer.writerow([r['state'], r['welfare_score'], r['education'],
                         r['healthcare'], r['food_security'], r['employment'], r['risk_category']])
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=welfarewatch_state_summary_2023.csv'})

@app.route('/export/district/<district_name>')
@researcher_required
def export_district(district_name):
    """Export district trend data as CSV."""
    db = get_db()
    rows = db.execute("""SELECT year, ROUND(AVG(risk_score),1) welfare_score,
        ROUND(AVG(indicator_1),1) education, ROUND(AVG(indicator_2),1) healthcare,
        ROUND(AVG(indicator_3),1) food_security, ROUND(AVG(indicator_4),1) employment,
        state FROM risk_records WHERE district=? GROUP BY year ORDER BY year""",
        (district_name,)).fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['District','State','Year','Welfare Score','Education','Healthcare','Food Security','Employment'])
    for r in rows:
        writer.writerow([district_name, r['state'], r['year'], r['welfare_score'],
                         r['education'], r['healthcare'], r['food_security'], r['employment']])
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={district_name}_welfare_trend.csv'})

# Leaderboard
@app.route('/leaderboard')
def leaderboard():
    db  = get_db()
    cat  = request.args.get('cat', default='districts')  # districts, states

    years_avail = [r['year'] for r in db.execute("SELECT DISTINCT year FROM risk_records ORDER BY year").fetchall()]
    latest_year = years_avail[-1] if years_avail else 2026
    year = request.args.get('year', type=int, default=latest_year)

    top_states = db.execute(f"""SELECT state, ROUND(AVG(risk_score),1) avg,
        COUNT(DISTINCT district) districts
        FROM risk_records WHERE year={year} GROUP BY state ORDER BY avg DESC""").fetchall()

    top_districts = db.execute(f"""SELECT district, state, ROUND(AVG(risk_score),1) avg
        FROM risk_records WHERE year={year} GROUP BY district ORDER BY avg DESC LIMIT 20""").fetchall()

    bottom_districts = db.execute(f"""SELECT district, state, ROUND(AVG(risk_score),1) avg
        FROM risk_records WHERE year={year} GROUP BY district ORDER BY avg ASC LIMIT 20""").fetchall()

    # Most improved since first year
    first_year = years_avail[0] if years_avail else 2018
    most_improved = db.execute(f"""SELECT a.district, a.state,
        ROUND(a.risk_score,1) cur, ROUND(b.risk_score,1) prev,
        ROUND(a.risk_score - b.risk_score, 1) delta
        FROM risk_records a JOIN risk_records b ON a.district=b.district
        WHERE a.year={year} AND b.year={first_year}
        GROUP BY a.district ORDER BY delta DESC LIMIT 10""").fetchall()

    return render_template('leaderboard.html',
        top_states=top_states, top_districts=top_districts,
        bottom_districts=bottom_districts, most_improved=most_improved,
        year=year, years_avail=years_avail, cat=cat)

# Admin
@app.route('/admin')
@admin_required
def admin():
    db = get_db()
    datasets = db.execute("SELECT * FROM datasets ORDER BY is_official DESC,uploaded_at DESC").fetchall()

    # Report filters
    cat_f = request.args.get('cat_filter', '').strip()
    sev_f = request.args.get('sev_filter', '').strip()
    q_cond = ""
    q_params = []
    if cat_f:
        q_cond += " AND cr.category = ?"
        q_params.append(cat_f)
    if sev_f:
        q_cond += " AND cr.severity = ?"
        q_params.append(sev_f)

    reports = db.execute(
        f"SELECT cr.*,u.username FROM citizen_reports cr LEFT JOIN users u ON cr.reporter_id=u.id WHERE 1=1{q_cond} ORDER BY cr.submitted_at DESC",
        q_params).fetchall()

    users = db.execute("SELECT * FROM users ORDER BY id").fetchall()

    # Report analytics for admin
    report_by_cat = {}
    for row in db.execute("SELECT category, COUNT(*) n FROM citizen_reports WHERE category!='' GROUP BY category").fetchall():
        report_by_cat[row['category']] = row['n']
    report_by_sev = {}
    for row in db.execute("SELECT severity, COUNT(*) n FROM citizen_reports WHERE severity!='' GROUP BY severity").fetchall():
        report_by_sev[row['severity']] = row['n']
    high_districts = db.execute("""
        SELECT district, state, COUNT(*) n FROM citizen_reports
        WHERE severity='High' GROUP BY district, state ORDER BY n DESC LIMIT 5
    """).fetchall()

    stats = {
        'total_records': db.execute("SELECT COUNT(*) FROM risk_records").fetchone()[0],
        'total_users':   db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        'pending':       db.execute("SELECT COUNT(*) FROM citizen_reports WHERE status='pending'").fetchone()[0],
    }
    return render_template('admin.html', datasets=datasets, reports=reports, users=users,
                           stats=stats, report_by_cat=report_by_cat, report_by_sev=report_by_sev,
                           high_districts=high_districts, cat_filter=cat_f, sev_filter=sev_f)

@app.route('/admin/upload', methods=['POST'])
@admin_required
def upload_dataset():
    if 'file' not in request.files: flash('No file.','error'); return redirect(url_for('admin'))
    f = request.files['file']
    if not f or not f.filename.endswith('.csv'): flash('CSV only.','error'); return redirect(url_for('admin'))
    filename = secure_filename(f.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    f.save(filepath)
    try: df = pd.read_csv(filepath); cols = json.dumps(list(df.columns)); rc = len(df)
    except: cols='[]'; rc=0
    db = get_db()
    db.execute("INSERT INTO datasets (name,description,source,domain,filename,columns,row_count,is_official,uploaded_by) VALUES (?,?,?,?,?,?,?,?,?)",
        (request.form.get('name',f.filename),request.form.get('description',''),
         request.form.get('source',''),request.form.get('domain',''),
         filename,cols,rc,1 if request.form.get('is_official') else 0,session['user_id']))
    db.commit()
    flash(f'Dataset uploaded — {rc:,} rows.','success')
    return redirect(url_for('admin'))

@app.route('/admin/report/<int:rid>/status', methods=['POST'])
@admin_required
def update_report_status(rid):
    db = get_db()
    db.execute("UPDATE citizen_reports SET status=?,admin_note=? WHERE id=?",
        (request.form.get('status','pending'), request.form.get('admin_note',''), rid))
    db.commit()
    flash('Report updated.','success')
    return redirect(url_for('admin')+'#reports')

@app.route('/admin/dataset/<int:dataset_id>/delete', methods=['POST'])
@admin_required
def delete_dataset(dataset_id):
    db = get_db()
    ds = db.execute("SELECT * FROM datasets WHERE id=?", (dataset_id,)).fetchone()
    if not ds:
        flash('Dataset not found.', 'error')
        return redirect(url_for('admin'))
    # Remove associated risk records
    db.execute("DELETE FROM risk_records WHERE dataset_id=?", (dataset_id,))
    db.execute("DELETE FROM datasets WHERE id=?", (dataset_id,))
    db.commit()
    # Remove file if it exists
    fp = os.path.join(app.config['UPLOAD_FOLDER'], ds['filename'])
    if os.path.exists(fp):
        try: os.remove(fp)
        except: pass
    flash(f'Dataset "{ds["name"]}" and all associated records deleted.', 'success')
    return redirect(url_for('admin'))

@app.route('/api/district-map-data')
def api_district_map_data():
    """Return district-level welfare scores for map rendering."""
    db   = get_db()
    year = request.args.get('year', type=int, default=2023)
    rows = db.execute("""
        SELECT district, state,
               ROUND(AVG(risk_score),1)  score,
               ROUND(AVG(indicator_1),1) i1,
               ROUND(AVG(indicator_2),1) i2,
               ROUND(AVG(indicator_3),1) i3,
               ROUND(AVG(indicator_4),1) i4,
               risk_category
        FROM risk_records WHERE year=?
        GROUP BY district, state
    """, (year,)).fetchall()
    data = {}
    for r in rows:
        key = f"{r['state']}|{r['district']}"
        data[key] = {
            'district': r['district'], 'state': r['state'],
            'score': r['score'], 'i1': r['i1'], 'i2': r['i2'],
            'i3': r['i3'], 'i4': r['i4'],
            'category': r['risk_category'],
        }
    return jsonify(data)

@app.route('/api/state-rank')
def api_state_rank():
    """Return rank and score for a given state in the latest year."""
    state = request.args.get('state','').strip()
    db    = get_db()
    latest_year = db.execute("SELECT MAX(year) y FROM risk_records").fetchone()['y'] or 2026
    rows  = db.execute("""
        SELECT state, ROUND(AVG(risk_score),1) avg
        FROM risk_records WHERE year=?
        GROUP BY state ORDER BY avg DESC
    """, (latest_year,)).fetchall()
    total = len(rows)
    for idx, r in enumerate(rows, 1):
        if r['state'] == state:
            wl = welfare_label(r['avg'])
            return jsonify({'rank': idx, 'total': total, 'score': r['avg'],
                            'label': wl['label'], 'color': wl['color'],
                            'icon': wl['icon']})
    return jsonify({'error': 'State not found'}), 404

@app.route('/admin/analyze/<int:dataset_id>', methods=['POST'])
@admin_required
def analyze_dataset(dataset_id):
    db = get_db()
    ds = db.execute("SELECT * FROM datasets WHERE id=?", (dataset_id,)).fetchone()
    if not ds: flash('Not found.','error'); return redirect(url_for('admin'))
    col_map = {k:request.form.get(v) or '' for k,v in [
        ('state','col_state'),('district','col_district'),('year','col_year'),
        ('indicator_1','col_i1'),('indicator_2','col_i2'),
        ('indicator_3','col_i3'),('indicator_4','col_i4')]}
    ind_names = json.dumps({
        'indicator_1': request.form.get('name_i1') or INDICATOR_LABELS['indicator_1'],
        'indicator_2': request.form.get('name_i2') or INDICATOR_LABELS['indicator_2'],
        'indicator_3': request.form.get('name_i3') or INDICATOR_LABELS['indicator_3'],
        'indicator_4': request.form.get('name_i4') or INDICATOR_LABELS['indicator_4'],
    })
    try:
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], ds['filename']))
        results = analyze_dataframe(df, col_map)
        db.execute("DELETE FROM risk_records WHERE dataset_id=?", (dataset_id,))
        db.executemany("""INSERT INTO risk_records
            (state,district,year,indicator_1,indicator_2,indicator_3,indicator_4,
             risk_score,risk_category,dataset_id) VALUES (?,?,?,?,?,?,?,?,?,?)""",
            [(r['state'],r['district'],r['year'],r['indicator_1'],r['indicator_2'],
              r['indicator_3'],r['indicator_4'],r['risk_score'],r['risk_category'],dataset_id)
             for r in results])
        db.execute("UPDATE datasets SET indicator_names=? WHERE id=?", (ind_names, dataset_id))
        db.commit()
        flash(f'Analysis complete — {len(results):,} records.','success')
    except Exception as e: flash(f'Failed: {str(e)}','error')
    return redirect(url_for('admin'))


# Commentary: District
@app.route('/commentary/district/<district_name>')
def district_commentary(district_name):
    db  = get_db()
    row = db.execute("""
        SELECT district, state,
               ROUND(AVG(risk_score),1)   score,
               ROUND(AVG(indicator_1),1)  i1,
               ROUND(AVG(indicator_2),1)  i2,
               ROUND(AVG(indicator_3),1)  i3,
               ROUND(AVG(indicator_4),1)  i4
        FROM risk_records WHERE district=?
        GROUP BY district, state
    """, (district_name,)).fetchone()
    if not row:
        flash(f'No data found for {district_name}.', 'error')
        return redirect(url_for('search'))

    state_avg = db.execute(
        "SELECT ROUND(AVG(risk_score),1) avg FROM risk_records WHERE state=?",
        (row['state'],)).fetchone()['avg'] or 0
    nat_avg = db.execute(
        "SELECT ROUND(AVG(risk_score),1) avg FROM risk_records WHERE year=2023"
    ).fetchone()['avg'] or 52.4

    commentary = generate_commentary(
        score=row['score'], ind1=row['i1'], ind2=row['i2'],
        ind3=row['i3'],    ind4=row['i4'],
        nat_avg=nat_avg, state_avg=state_avg,
        name=district_name
    )
    # Trend for sparkline
    trend_rows = db.execute(
        "SELECT year, ROUND(AVG(risk_score),1) avg FROM risk_records WHERE district=? GROUP BY year ORDER BY year",
        (district_name,)).fetchall()
    trend = {'years': [r['year'] for r in trend_rows], 'scores': [r['avg'] for r in trend_rows]}

    return render_template('district_commentary.html',
        district=district_name, state=row['state'],
        commentary=commentary, trend=json.dumps(trend))


# Commentary: State
@app.route('/commentary/state/<state_name>')
def state_commentary(state_name):
    db  = get_db()
    row = db.execute("""
        SELECT ROUND(AVG(risk_score),1)  score,
               ROUND(AVG(indicator_1),1) i1,
               ROUND(AVG(indicator_2),1) i2,
               ROUND(AVG(indicator_3),1) i3,
               ROUND(AVG(indicator_4),1) i4
        FROM risk_records WHERE state=?
    """, (state_name,)).fetchone()
    if not row or not row['score']:
        flash(f'No data found for {state_name}.', 'error')
        return redirect(url_for('risk_map'))

    nat_avg = db.execute(
        "SELECT ROUND(AVG(risk_score),1) avg FROM risk_records WHERE year=2023"
    ).fetchone()['avg'] or 52.4
    commentary = generate_state_commentary(
        score=row['score'], ind1=row['i1'], ind2=row['i2'],
        ind3=row['i3'],    ind4=row['i4'],
        state_name=state_name, nat_avg=nat_avg
    )
    trend_rows = db.execute(
        "SELECT year, ROUND(AVG(risk_score),1) avg FROM risk_records WHERE state=? GROUP BY year ORDER BY year",
        (state_name,)).fetchall()
    trend = {'years': [r['year'] for r in trend_rows], 'scores': [r['avg'] for r in trend_rows]}

    # Top/bottom districts in state
    districts = db.execute("""
        SELECT district, ROUND(AVG(risk_score),1) avg
        FROM risk_records WHERE state=? AND year=2023
        GROUP BY district ORDER BY avg DESC
    """, (state_name,)).fetchall()

    return render_template('state_commentary.html',
        state_name=state_name, commentary=commentary,
        trend=json.dumps(trend), districts=districts)


# Indicator Correlation Analysis
@app.route('/analysis/correlation')
def correlation_analysis():
    # Frontend access disabled — backend logic preserved in correlation_engine.py
    # Redirect to dashboard; correlation insights are shown there instead.
    flash('Indicator correlation insights are now embedded in the Dashboard.', 'info')
    return redirect(url_for('dashboard'))

def auto_import_2024_2026():
    """Auto-import the 2024-2026 official dataset if not already loaded."""
    filename = 'welfarewatch_2024_2026_official.csv'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    existing = db.execute("SELECT id FROM datasets WHERE filename=?", (filename,)).fetchone()
    if existing:
        db.close(); return
    try:
        df = pd.read_csv(filepath)
        cols = json.dumps(list(df.columns))
        rc   = len(df)
        ind_names = json.dumps({
            'indicator_1': 'Education & Literacy',
            'indicator_2': 'Healthcare Access',
            'indicator_3': 'Food Security',
            'indicator_4': 'Employment & Income',
        })
        cur = db.execute(
            "INSERT INTO datasets (name,description,source,domain,filename,columns,row_count,is_official,uploaded_by,indicator_names) VALUES (?,?,?,?,?,?,?,?,?,?)",
            ('WelfareWatch 2024–2026 Official Dataset',
             'Realistic district-level welfare indicators for 2024, 2025 and 2026 across 15 major states.',
             'WelfareWatch Research Team',
             'Multi-Indicator Welfare',
             filename, cols, rc, 1, None, ind_names))
        ds_id = cur.lastrowid
        col_map = {
            'state': 'State', 'district': 'District', 'year': 'Year',
            'indicator_1': 'Education_Index', 'indicator_2': 'Healthcare_Index',
            'indicator_3': 'Food_Security_Index', 'indicator_4': 'Employment_Index',
        }
        results = analyze_dataframe(df, col_map)
        db.executemany(
            """INSERT INTO risk_records
               (state,district,year,indicator_1,indicator_2,indicator_3,indicator_4,
                risk_score,risk_category,dataset_id) VALUES (?,?,?,?,?,?,?,?,?,?)""",
            [(r['state'],r['district'],r['year'],r['indicator_1'],r['indicator_2'],
              r['indicator_3'],r['indicator_4'],r['risk_score'],r['risk_category'],ds_id)
             for r in results])
        db.commit()
        print(f"[WelfareWatch] ✅ Auto-imported 2024–2026 dataset — {len(results)} records")
    except Exception as e:
        print(f"[WelfareWatch] ⚠️  Auto-import failed: {e}")
    finally:
        db.close()


# PDF Report Generation
@app.route('/report/pdf/<district_name>')
def generate_pdf_report(district_name):
    """Render a print-ready HTML welfare report (no external PDF dependencies)."""
    db  = get_db()
    row = db.execute("""
        SELECT district, state,
               ROUND(AVG(risk_score),1) score,
               ROUND(AVG(indicator_1),1) i1, ROUND(AVG(indicator_2),1) i2,
               ROUND(AVG(indicator_3),1) i3, ROUND(AVG(indicator_4),1) i4
        FROM risk_records WHERE district=?
        GROUP BY district, state
    """, (district_name,)).fetchone()
    if not row:
        flash(f'No data for {district_name}.', 'error')
        return redirect(url_for('search'))

    trend_rows = db.execute(
        "SELECT year, ROUND(AVG(risk_score),1) avg FROM risk_records WHERE district=? GROUP BY year ORDER BY year",
        (district_name,)).fetchall()
    state_avg = db.execute(
        "SELECT ROUND(AVG(risk_score),1) avg FROM risk_records WHERE state=?", (row['state'],)
    ).fetchone()['avg'] or 0
    nat_avg = db.execute(
        "SELECT ROUND(AVG(risk_score),1) avg FROM risk_records WHERE year=(SELECT MAX(year) FROM risk_records)"
    ).fetchone()['avg'] or 0
    wl = welfare_label(row['score'])

    from commentary_engine import generate_commentary
    commentary = generate_commentary(
        score=row['score'], ind1=row['i1'], ind2=row['i2'],
        ind3=row['i3'], ind4=row['i4'], nat_avg=nat_avg,
        state_avg=state_avg, name=district_name)

    import datetime
    return render_template('report_print.html',
        district=district_name, row=row, wl=wl,
        state_avg=state_avg, nat_avg=nat_avg,
        trend_rows=trend_rows, commentary=commentary,
        generated=datetime.date.today().strftime('%d %b %Y'),
        INDICATOR_LABELS=INDICATOR_LABELS)

# ── API: Nation-wide stats (for homepage live ticker) ────────────────────────
@app.route('/api/latest-stats')
def api_latest_stats():
    db = get_db()
    latest_year = db.execute("SELECT MAX(year) y FROM risk_records").fetchone()['y'] or 2026
    nat = db.execute("SELECT ROUND(AVG(risk_score),1) avg FROM risk_records WHERE year=?",
                     (latest_year,)).fetchone()['avg'] or 0
    states = db.execute("SELECT COUNT(DISTINCT state) n FROM risk_records").fetchone()['n']
    districts = db.execute("SELECT COUNT(DISTINCT district) n FROM risk_records").fetchone()['n']
    reports   = db.execute("SELECT COUNT(*) n FROM citizen_reports").fetchone()['n']
    return jsonify({'nat_avg': nat, 'states': states, 'districts': districts,
                    'reports': reports, 'year': latest_year})


with app.app_context():
    init_db()
    auto_import_2024_2026()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
