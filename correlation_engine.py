"""
WelfareWatch — Indicator Correlation & Impact Analysis Engine
=============================================================
Pure rule-based statistical analysis. No ML or AI.

Answers: Which welfare indicator has the strongest relationship
with overall welfare score?

Methods used:
1. Pearson correlation coefficient (r) per indicator
2. Contribution analysis (weighted deviation)
3. Marginal impact simulation (change one indicator, see score change)
4. Rank correlation (Spearman) for robustness
"""

import math
from risk_engine import INDICATOR_LABELS, INDICATOR_WEIGHTS, compute_welfare_score


def _mean(values):
    return sum(values) / len(values) if values else 0


def _std(values):
    if len(values) < 2: return 0
    m = _mean(values)
    variance = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def pearson_correlation(x_vals, y_vals):
    """Compute Pearson r between two lists of numbers."""
    n = len(x_vals)
    if n < 3: return 0.0
    mx, my = _mean(x_vals), _mean(y_vals)
    sx, sy = _std(x_vals), _std(y_vals)
    if sx == 0 or sy == 0: return 0.0
    cov = sum((x - mx) * (y - my) for x, y in zip(x_vals, y_vals)) / (n - 1)
    return round(cov / (sx * sy), 4)


def spearman_correlation(x_vals, y_vals):
    """Rank-based Spearman correlation — robust to outliers."""
    n = len(x_vals)
    if n < 3: return 0.0
    
    def rank(vals):
        sorted_vals = sorted(enumerate(vals), key=lambda x: x[1])
        ranks = [0] * n
        for rank_i, (orig_i, _) in enumerate(sorted_vals):
            ranks[orig_i] = rank_i + 1
        return ranks

    rx, ry = rank(x_vals), rank(y_vals)
    d2 = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    return round(1 - (6 * d2) / (n * (n * n - 1)), 4)


def marginal_impact(base_scores, weights, indicator_idx, delta=10):
    """
    Simulate: if indicator[indicator_idx] improves by `delta` points,
    how much does overall welfare score change?
    """
    improved = list(base_scores)
    improved[indicator_idx] = min(100, improved[indicator_idx] + delta)
    before = compute_welfare_score(*base_scores)
    after  = compute_welfare_score(*improved)
    return round(after - before, 2)


def interpret_correlation(r):
    """Human-readable interpretation of Pearson r."""
    ar = abs(r)
    if ar >= 0.8: strength = "Very Strong"
    elif ar >= 0.6: strength = "Strong"
    elif ar >= 0.4: strength = "Moderate"
    elif ar >= 0.2: strength = "Weak"
    else: strength = "Very Weak"
    direction = "positive" if r >= 0 else "negative"
    return f"{strength} {direction} relationship"


def compute_correlation_analysis(records):
    """
    Main entry point. Takes list of dicts with keys:
    indicator_1, indicator_2, indicator_3, indicator_4, risk_score
    
    Returns a rich analysis dict.
    """
    if len(records) < 10:
        return {'error': 'Insufficient data for correlation analysis (need at least 10 records)'}

    scores   = [r['risk_score']  for r in records]
    ind_data = {
        'indicator_1': [r['indicator_1'] for r in records],
        'indicator_2': [r['indicator_2'] for r in records],
        'indicator_3': [r['indicator_3'] for r in records],
        'indicator_4': [r['indicator_4'] for r in records],
    }

    results = {}
    for key, values in ind_data.items():
        pr = pearson_correlation(values, scores)
        sr = spearman_correlation(values, scores)
        weight = INDICATOR_WEIGHTS[key]
        label  = INDICATOR_LABELS[key]

        # Marginal impact: +10 points → score change
        avg_scores = [
            _mean(ind_data['indicator_1']),
            _mean(ind_data['indicator_2']),
            _mean(ind_data['indicator_3']),
            _mean(ind_data['indicator_4']),
        ]
        idx = int(key[-1]) - 1
        impact_10 = marginal_impact(avg_scores, INDICATOR_WEIGHTS, idx, 10)
        impact_20 = marginal_impact(avg_scores, INDICATOR_WEIGHTS, idx, 20)

        results[key] = {
            'label':          label,
            'pearson_r':      pr,
            'spearman_r':     sr,
            'weight_pct':     weight,
            'interpretation': interpret_correlation(pr),
            'avg_value':      round(_mean(values), 1),
            'std_value':      round(_std(values), 1),
            'impact_10pts':   impact_10,  # score gain if this indicator improves by 10
            'impact_20pts':   impact_20,
            # Combined impact score: how much does this indicator really move welfare?
            'impact_score':   round(abs(pr) * weight + abs(sr) * 5, 2),
        }

    # Rank by impact score (highest = most influential)
    ranked = sorted(results.items(), key=lambda x: x[1]['impact_score'], reverse=True)

    # Key findings
    top    = ranked[0]
    bottom = ranked[-1]
    
    # Biggest gap from ideal (100)
    gaps = {k: round(100 - _mean(v), 1) for k, v in ind_data.items()}
    biggest_gap_key = max(gaps, key=gaps.get)
    biggest_gap     = gaps[biggest_gap_key]

    # Variance analysis: which indicator has the most spread (opportunity for targeted intervention)?
    variances = {k: round(_std(v), 1) for k, v in ind_data.items()}
    most_variable_key = max(variances, key=variances.get)

    # R² values (explained variance)
    r_squared = {k: round(v['pearson_r'] ** 2 * 100, 1) for k, v in results.items()}

    # Cross-indicator correlation matrix
    corr_matrix = {}
    keys_list = list(ind_data.keys())
    for ki in keys_list:
        corr_matrix[ki] = {}
        for kj in keys_list:
            if ki == kj:
                corr_matrix[ki][kj] = 1.0
            else:
                corr_matrix[ki][kj] = pearson_correlation(ind_data[ki], ind_data[kj])

    return {
        'indicators':         results,
        'ranked':             ranked,
        'top_indicator':      {'key': top[0], **top[1]},
        'bottom_indicator':   {'key': bottom[0], **bottom[1]},
        'biggest_gap':        {'key': biggest_gap_key, 'label': INDICATOR_LABELS[biggest_gap_key], 'gap': biggest_gap},
        'most_variable':      {'key': most_variable_key, 'label': INDICATOR_LABELS[most_variable_key], 'std': variances[most_variable_key]},
        'r_squared':          r_squared,
        'corr_matrix':        corr_matrix,
        'n_records':          len(records),
        'national_avg':       round(_mean(scores), 1),
        'key_insight':        _generate_key_insight(ranked, biggest_gap_key, r_squared),
    }


def _generate_key_insight(ranked, biggest_gap_key, r_squared):
    """Generate the single most important finding."""
    top_key, top_data = ranked[0]
    top_r2 = r_squared[top_key]
    gap_label = INDICATOR_LABELS[biggest_gap_key]
    top_label = top_data['label']
    
    if top_key == biggest_gap_key:
        return (f"<strong>{top_label}</strong> is both the most correlated indicator with welfare "
                f"(r={top_data['pearson_r']}, explains {top_r2}% of score variation) "
                f"AND has the largest room for improvement. Investing here gives maximum returns.")
    else:
        return (f"<strong>{top_label}</strong> most strongly predicts welfare outcomes "
                f"(r={top_data['pearson_r']}, explains {top_r2}% of score variation). "
                f"However, <strong>{gap_label}</strong> has the most room to improve — "
                f"a combined strategy targeting both would have the greatest impact.")
