"""
WelfareWatch — Rule-Based Commentary Engine
=============================================
Generates human-readable explanations for welfare scores.
Pure rule-based logic — no AI or machine learning.
"""

from risk_engine import INDICATOR_LABELS, SCORE_BANDS, welfare_label


# Score thresholds for each indicator
def _indicator_grade(score):
    """Categorize a single indicator score."""
    if score >= 80: return 'excellent'
    if score >= 65: return 'good'
    if score >= 50: return 'moderate'
    if score >= 35: return 'weak'
    return 'critical'


# Templates for each indicator × grade combo
IND_COMMENTS = {
    'indicator_1': {  # Education & Literacy
        'excellent': {
            'why':    "Education & Literacy is a standout strength — school enrollment rates are high, dropout rates are low, and literacy levels are above the national average.",
            'action': "Maintain current education infrastructure and expand vocational training programs for youth above secondary level."
        },
        'good': {
            'why':    "Education delivery is performing well, though some districts still see girls' enrollment gaps and secondary school dropouts.",
            'action': "Focus on reducing gender disparity in upper-primary enrollment and improve teacher-to-student ratios in rural blocks."
        },
        'moderate': {
            'why':    "Education coverage is average — a mix of well-functioning schools and under-resourced areas creates uneven outcomes.",
            'action': "Prioritise opening new primary schools in remote villages, enforce attendance through mid-day meal schemes, and recruit trained teachers."
        },
        'weak': {
            'why':    "Education access is significantly below average. High dropout rates, poor infrastructure, and teacher absenteeism are key contributing factors.",
            'action': "Urgent action needed: conduct school mapping surveys, launch cash-transfer incentives for attendance, and partner with NGOs for adult literacy camps."
        },
        'critical': {
            'why':    "Education is in a critical state — a large share of children are out of school, literacy rates are far below national average, and school infrastructure is inadequate.",
            'action': "Emergency intervention required. Apply for SMSA (Samagra Shiksha) special grants, launch community mobilisation for dropout recovery, and build at least one model school per block."
        },
    },
    'indicator_2': {  # Healthcare Access
        'excellent': {
            'why':    "Healthcare access is excellent — government hospitals, primary health centres (PHCs), and community health workers are well-distributed and functional.",
            'action': "Scale up specialised care services (dialysis, cancer screening) and expand digital health records across all facilities."
        },
        'good': {
            'why':    "Healthcare delivery is strong, with good PHC coverage, though some gaps remain in specialist availability and health worker deployment in remote areas.",
            'action': "Increase the number of ASHA workers in underserved blocks and ensure timely supply of essential medicines to all sub-centres."
        },
        'moderate': {
            'why':    "Healthcare access is average — while primary centres exist, they often lack doctors, medicines, and diagnostic equipment, especially in tribal and rural areas.",
            'action': "Utilise National Health Mission (NHM) funds to upgrade PHCs to 24×7 facilities, hire contractual specialists, and strengthen ambulance coverage."
        },
        'weak': {
            'why':    "Healthcare access is significantly below par. Many residents travel over 20km for basic care, maternal mortality is above average, and immunisation coverage is incomplete.",
            'action': "Fast-track setting up new sub-health centres, launch mobile medical units for remote areas, and run immunisation mop-up drives through Ayushman Bharat."
        },
        'critical': {
            'why':    "Healthcare is at a critical level. PHC infrastructure is absent or non-functional in large parts of the area, leading to preventable deaths and untreated chronic illness.",
            'action': "Declare a health emergency priority zone. Apply for Central assistance under PM-AB Health Infrastructure Mission (PMABHIM). Deploy Army/DRDO medical camps as immediate relief."
        },
    },
    'indicator_3': {  # Food Security
        'excellent': {
            'why':    "Food security is strong — ration shops (PDS) are functional, Aadhaar-linked cards are widely distributed, and nutritional indicators among children are positive.",
            'action': "Expand fortified food distribution under ICDS and target remaining pockets of anaemia among women and adolescent girls."
        },
        'good': {
            'why':    "Food security delivery is good overall, though some leakages in PDS and irregular supply chains create minor gaps for vulnerable households.",
            'action': "Digitalise POS machines in all ration shops, eliminate ghost beneficiaries, and ensure monthly minimum entitlement reaches all AAY card holders."
        },
        'moderate': {
            'why':    "Food security is at an average level. Several ration shops operate irregularly, and a share of eligible households is still excluded from NFSA benefits.",
            'action': "Conduct door-to-door NFSA survey to identify excluded families, activate grievance redressal under 'Annavad' portal, and improve PDS supply chain monitoring."
        },
        'weak': {
            'why':    "Food insecurity is a significant concern. Malnutrition rates among under-5 children are elevated, ration shop coverage is thin, and many eligible families lack valid ration cards.",
            'action': "Launch emergency nutritional supplementation under POSHAN Abhiyan, increase Anganwadi worker density, and conduct special NFSA enrolment camps."
        },
        'critical': {
            'why':    "Food security is in a critical condition. Severe malnutrition, hunger indicators above national emergency thresholds, and almost non-functional PDS infrastructure demand immediate intervention.",
            'action': "Activate National Food Security crisis protocol. Seek PM Relief Fund allocation. Deploy mobile ration distribution vans and expand community kitchens (Indira Rasoi / Amma Canteen model)."
        },
    },
    'indicator_4': {  # Employment & Income
        'excellent': {
            'why':    "Employment and income indicators are excellent. MGNREGA job demand is fully met, non-farm employment is growing, and household income levels exceed the state average.",
            'action': "Expand skill development under PMKVY (Pradhan Mantri Kaushal Vikas Yojana) to create a pipeline into urban formal employment."
        },
        'good': {
            'why':    "Employment delivery is solid, with most MGNREGA job-seekers receiving work and diversification into self-help group (SHG) livelihoods showing results.",
            'action': "Deepen PM SVANidhi (street vendor loans) and PM Mudra Yojana reach to boost micro-enterprise and reduce dependency on seasonal agriculture."
        },
        'moderate': {
            'why':    "Employment situation is average — MGNREGA work is partially available but 100-day completion rates are below target, and non-farm income sources remain limited.",
            'action': "Increase MGNREGA work shelf by adding permissible activities (pond desilting, plantation). Link SHG products to e-commerce through Government e-Marketplace (GeM)."
        },
        'weak': {
            'why':    "Employment and income are significantly below average. Seasonal migration is high, MGNREGA demand exceeds supply, and poverty rates are above the district average.",
            'action': "Fast-track MGNREGA fund release to cover pending wage payments. Establish one vocational training centre per block under Deen Dayal Upadhyaya Grameen Kaushalya Yojana."
        },
        'critical': {
            'why':    "Employment is in a critical state. Widespread unemployment, very high seasonal out-migration, and extremely low household income are driving a downward welfare spiral.",
            'action': "Declare MGNREGA drought relief. Apply for Special Central Assistance to Aspirational Districts Programme. Launch PM Garib Kalyan Rozgar Abhiyan-style intensive employment drive."
        },
    },
}

# Overall score commentary
def _overall_why(score, ind_scores):
    """Generate an overall explanation based on the composite score."""
    wl = welfare_label(score)
    ind1, ind2, ind3, ind4 = ind_scores
    
    strongest = max(
        ('Education & Literacy', ind1),
        ('Healthcare Access', ind2),
        ('Food Security', ind3),
        ('Employment & Income', ind4),
        key=lambda x: x[1]
    )
    weakest = min(
        ('Education & Literacy', ind1),
        ('Healthcare Access', ind2),
        ('Food Security', ind3),
        ('Employment & Income', ind4),
        key=lambda x: x[1]
    )
    gap = round(strongest[1] - weakest[1], 1)

    if score >= 80:
        return (f"This area is performing at an excellent level ({score}/100). "
                f"The strongest pillar is <strong>{strongest[0]}</strong> ({strongest[1]}/100), "
                f"reflecting effective programme delivery. Even the weakest area, "
                f"<strong>{weakest[0]}</strong> ({weakest[1]}/100), is above the danger zone.")
    if score >= 60:
        return (f"This area scores {score}/100 — Good welfare delivery overall. "
                f"<strong>{strongest[0]}</strong> ({strongest[1]}/100) is the key strength. "
                f"The gap between the strongest and weakest indicator is {gap} points, suggesting "
                f"targeted improvement in <strong>{weakest[0]}</strong> can push this into Excellent territory.")
    if score >= 40:
        return (f"The overall welfare score of {score}/100 (Moderate) reflects uneven programme delivery. "
                f"While <strong>{strongest[0]}</strong> ({strongest[1]}/100) shows promise, "
                f"<strong>{weakest[0]}</strong> ({weakest[1]}/100) is dragging the composite score down. "
                f"Closing this {gap}-point gap is the single highest-leverage action.")
    if score >= 20:
        return (f"A welfare score of {score}/100 (Weak) signals multiple system failures. "
                f"Only <strong>{strongest[0]}</strong> ({strongest[1]}/100) shows some functioning delivery. "
                f"<strong>{weakest[0]}</strong> ({weakest[1]}/100) is in a critical state and requires immediate government action.")
    return (f"The score of {score}/100 is Critical — indicating severe welfare deficits across all four pillars. "
            f"<strong>{weakest[0]}</strong> ({weakest[1]}/100) is the most urgent priority. "
            f"Multi-ministry emergency intervention is required immediately.")


def _comparison_text(score, nat_avg=52.4, state_avg=None):
    """Contextualise the score against benchmarks."""
    lines = []
    diff_nat = round(score - nat_avg, 1)
    if diff_nat > 5:
        lines.append(f"<strong>+{diff_nat} points above</strong> the national average of {nat_avg}/100 — performing well relative to India overall.")
    elif diff_nat < -5:
        lines.append(f"<strong>{diff_nat} points below</strong> the national average of {nat_avg}/100 — needs to close this gap urgently.")
    else:
        lines.append(f"Score is close to the national average of {nat_avg}/100 — room to push into the 'Good' category exists.")
    if state_avg:
        diff_state = round(score - state_avg, 1)
        if diff_state > 3:
            lines.append(f"Also <strong>+{diff_state} pts above</strong> the state average ({state_avg}/100).")
        elif diff_state < -3:
            lines.append(f"<strong>{diff_state} pts below</strong> the state average ({state_avg}/100) — underperforming within its own state.")
    return " ".join(lines)


def generate_commentary(score, ind1, ind2, ind3, ind4, nat_avg=52.4, state_avg=None, name="This area"):
    """
    Generate full commentary for a district or state.
    Returns dict with keys: overall_why, comparison, indicators, top_priority, quick_wins
    """
    scores = [ind1, ind2, ind3, ind4]
    keys   = ['indicator_1', 'indicator_2', 'indicator_3', 'indicator_4']
    labels = list(INDICATOR_LABELS.values())

    # Per-indicator commentary
    indicators = []
    for i, (key, label, s) in enumerate(zip(keys, labels, scores)):
        grade = _indicator_grade(s)
        wl    = welfare_label(s)
        cmt   = IND_COMMENTS[key][grade]
        indicators.append({
            'label':   label,
            'score':   s,
            'grade':   grade,
            'wl':      wl,
            'why':     cmt['why'],
            'action':  cmt['action'],
        })

    # Sort to find top priority (lowest score) and quick win (second lowest but not critical)
    sorted_inds = sorted(indicators, key=lambda x: x['score'])
    top_priority = sorted_inds[0]

    # Quick win = highest score that is still below 70 (room to improve)
    improvable = [ind for ind in sorted_inds if ind['score'] < 70]
    quick_win  = improvable[-1] if len(improvable) > 1 else sorted_inds[-1]

    return {
        'overall_why':   _overall_why(score, scores),
        'comparison':    _comparison_text(score, nat_avg, state_avg),
        'indicators':    indicators,
        'top_priority':  top_priority,
        'quick_win':     quick_win,
        'name':          name,
        'score':         score,
        'wl':            welfare_label(score),
    }


def generate_state_commentary(score, ind1, ind2, ind3, ind4, state_name, nat_avg=52.4):
    """State-level commentary with broader context."""
    base = generate_commentary(score, ind1, ind2, ind3, ind4, nat_avg, name=state_name)
    return base
