"""
WelfareWatch — Rule-Based Welfare Scoring Engine v3
=====================================================

SCORE MEANING (v3):
  Score = Weighted average of welfare indicators
  Range: 0 – 100
  HIGHER = BETTER welfare delivery

  80–100 → Excellent   (Welfare programmes reaching people effectively)
  60–79  → Good        (Strong delivery with minor gaps)
  40–59  → Moderate    (Average performance, improvement needed)
  20–39  → Weak        (Significant gaps, government action required)
  0–19   → Critical    (Severe welfare deficit, urgent intervention needed)

Formula:
  Welfare Score = 0.40 × Education & Literacy
                + 0.30 × Healthcare Access
                + 0.20 × Food Security
                + 0.10 × Employment & Income

All indicators normalized to 0–100 where 100 = best welfare delivery.
"""

import pandas as pd
import numpy as np


# Score bands — HIGHER IS BETTER
SCORE_BANDS = [
    (80, 100, 'Excellent',  '#10B981', 'excellent',
     'Welfare programmes are reaching people effectively. This area is a model for others.'),
    (60,  79, 'Good',       '#3B82F6', 'good',
     'Strong welfare delivery with minor gaps. Continued monitoring recommended.'),
    (40,  59, 'Moderate',   '#F59E0B', 'moderate',
     'Average performance. Targeted improvements can significantly help citizens.'),
    (20,  39, 'Weak',       '#F97316', 'weak',
     'Significant welfare gaps. Government action and resource allocation urgently needed.'),
    ( 0,  19, 'Critical',   '#EF4444', 'critical',
     'Severe welfare deficit. Immediate intervention and emergency support required.'),
]

INDICATOR_LABELS = {
    'indicator_1': 'Education & Literacy',
    'indicator_2': 'Healthcare Access',
    'indicator_3': 'Food Security',
    'indicator_4': 'Employment & Income',
}
INDICATOR_WEIGHTS = {
    'indicator_1': 40,
    'indicator_2': 30,
    'indicator_3': 20,
    'indicator_4': 10,
}
INDICATOR_ICONS = {
    'indicator_1': '📚',
    'indicator_2': '🏥',
    'indicator_3': '🌾',
    'indicator_4': '💼',
}
INDICATOR_DESCRIPTIONS = {
    'indicator_1': 'School enrollment, literacy rates, dropout rates, and education infrastructure access.',
    'indicator_2': 'Hospital availability, doctor-patient ratio, immunisation coverage, maternal health.',
    'indicator_3': 'PDS ration shop access, nutritional intake, food distribution effectiveness.',
    'indicator_4': 'MGNREGA coverage, employment rates, household income, poverty alleviation.',
}


def welfare_label(score):
    """Return display metadata for a welfare score (higher = better)."""
    if score is None:
        return {'label': 'No Data', 'icon': '❓', 'color': '#94A3B8', 'cls': 'nodata',
                'description': 'No data available for this area.'}
    s = float(score)
    for lo, hi, label, color, cls, desc in SCORE_BANDS:
        if lo <= s <= hi:
            icon = {'Excellent': '🌟', 'Good': '✅', 'Moderate': '⚠️',
                    'Weak': '🔶', 'Critical': '🚨'}[label]
            return {'label': label, 'icon': icon, 'color': color,
                    'cls': cls, 'description': desc}
    return {'label': 'No Data', 'icon': '❓', 'color': '#94A3B8', 'cls': 'nodata',
            'description': 'Score out of expected range.'}


def categorize_welfare(score):
    """Categorize score into DB-storable string (higher = better)."""
    s = float(score)
    if s >= 80: return 'Excellent'
    if s >= 60: return 'Good'
    if s >= 40: return 'Moderate'
    if s >= 20: return 'Weak'
    return 'Critical'


# Keep backward-compat alias
def categorize_risk(score):
    return categorize_welfare(score)


def compute_welfare_score(i1, i2, i3, i4):
    """
    Weighted welfare score. All inputs must be 0–100 (higher = better).
    Returns score 0–100 (higher = better welfare delivery).
    """
    score = (0.40 * float(i1) +
             0.30 * float(i2) +
             0.20 * float(i3) +
             0.10 * float(i4))
    return round(min(max(score, 0.0), 100.0), 2)


# Backward-compat alias
def compute_risk_score(i1, i2, i3, i4):
    return compute_welfare_score(i1, i2, i3, i4)


# Column direction detection
# high value = GOOD for welfare → keep as-is (already high = better)
_HIGH_IS_GOOD = [
    'index', 'score', 'coverage', 'enrolled', 'enrollment', 'linked', 'verified',
    'registered', 'beneficiar', 'active', 'completed', 'got_work', 'allotted',
    'issued', 'wage', 'girls', 'female', 'empanelled', 'hospital', 'literacy',
    'attendance', 'access', 'rate', 'percent', 'pct', 'ratio',
]
# high value = BAD → invert (100 - normalized)
_HIGH_IS_BAD = [
    'dropout', 'absent', 'pending', 'delay', 'miss', 'shortage',
    'poverty', 'malnutrition', 'stunting', 'wasting', 'deficit',
]


def _infer_direction(col_name: str) -> str:
    """'keep' = high raw value is good, 'invert' = high raw value is bad."""
    col = col_name.lower()
    if '[inv]' in col:
        return 'invert'
    for kw in _HIGH_IS_BAD:
        if kw in col:
            return 'invert'
    for kw in _HIGH_IS_GOOD:
        if kw in col:
            return 'keep'
    return 'keep'


def normalize_series(series: pd.Series, direction: str = 'keep') -> pd.Series:
    """
    Normalize to 0–100 where 100 = best welfare delivery.
    'keep'   → high raw value → high normalized (high = good)
    'invert' → high raw value → low normalized (high = bad, so flip)
    """
    s = pd.to_numeric(series, errors='coerce').fillna(0)
    n = len(s)
    if n <= 1 or s.max() == s.min():
        return pd.Series([50.0] * n, index=s.index)
    normalized = (s - s.min()) / (s.max() - s.min()) * 100.0
    if direction == 'invert':
        normalized = 100.0 - normalized
    return normalized.round(2)


def analyze_dataframe(df: pd.DataFrame, col_map: dict) -> list:
    """
    Full pipeline: extract → normalize → score → categorize.
    Returns list of dicts. Higher score = better welfare.
    """
    df = df.copy()
    for key in ['indicator_1', 'indicator_2', 'indicator_3', 'indicator_4']:
        col = col_map.get(key, '')
        if col and col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    norm = {}
    for key in ['indicator_1', 'indicator_2', 'indicator_3', 'indicator_4']:
        col = col_map.get(key, '')
        if col and col in df.columns:
            norm[key] = normalize_series(df[col], _infer_direction(col))
        else:
            norm[key] = pd.Series([50.0] * len(df), index=df.index)

    results = []
    for idx, row in df.iterrows():
        state = str(row.get(col_map.get('state', ''), 'Unknown') or 'Unknown')
        district = str(row.get(col_map.get('district', ''), 'Unknown') or 'Unknown')
        year_col = col_map.get('year', '')
        try:
            year = int(float(row[year_col])) if year_col and year_col in df.columns else 2023
        except (ValueError, TypeError):
            year = 2023

        i1 = float(norm['indicator_1'].loc[idx])
        i2 = float(norm['indicator_2'].loc[idx])
        i3 = float(norm['indicator_3'].loc[idx])
        i4 = float(norm['indicator_4'].loc[idx])
        score = compute_welfare_score(i1, i2, i3, i4)

        results.append({
            'state': state, 'district': district, 'year': year,
            'indicator_1': round(i1, 1), 'indicator_2': round(i2, 1),
            'indicator_3': round(i3, 1), 'indicator_4': round(i4, 1),
            'risk_score': score, 'risk_category': categorize_welfare(score),
        })
    return results


def compute_insights(year_scores: dict) -> dict:
    """Compute trend insights. Higher score = better."""
    if not year_scores:
        return {}
    years  = sorted(year_scores.keys())
    scores = [year_scores[y] for y in years]
    best_yr  = years[scores.index(max(scores))]   # max = best (higher is better)
    worst_yr = years[scores.index(min(scores))]   # min = worst
    first, last = scores[0], scores[-1]
    change = round(last - first, 1)
    pct_change = round(abs(change / first) * 100, 1) if first else 0
    trend = 'improving' if change > 0 else 'declining' if change < 0 else 'stable'
    return {
        'best_year':   best_yr,
        'best_score':  round(max(scores), 1),
        'worst_year':  worst_yr,
        'worst_score': round(min(scores), 1),
        'change':      change,
        'pct_change':  pct_change,
        'trend':       trend,
    }
