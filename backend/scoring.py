"""Policy Scoring Engine - Week 4 (IMPROVED with STRICT FILTERING)
Scores policies based on user preferences, risk profile, and personal health data
Applies AGGRESSIVE filtering BEFORE scoring to respect user preferences
"""

from decimal import Decimal
from typing import List, Dict, Any, Tuple

def filter_policies(
    policies: List[Dict[str, Any]],
    user_data: Dict[str, Any],
    risk_profile: str
) -> Tuple[List[Dict[str, Any]], Dict[str, List[str]]]:
    """
    STRICTLY filter policies based on user preferences BEFORE scoring.
    
    Filters:
    1. Age-based filtering (what types are appropriate)
    2. Risk-based filtering (high risk → health only)
    3. Preferred policy types (if specified)
    4. Max premium (if specified)
    
    Returns:
        - Filtered list of policies
        - Dict with filter details for logging
    """
    filter_details = {
        'initial_count': len(policies),
        'age_filtered': [],
        'risk_filtered': [],
        'preferred_type_filtered': [],
        'budget_filtered': [],
        'final_count': 0
    }
    
    demographics = user_data.get('demographics', {})
    preferences = user_data.get('preferences', {})
    
    age = demographics.get('age', 30)
    max_premium = preferences.get('max_premium')
    preferred_types = preferences.get('preferred_policy_types', [])
    
    # STEP 1: Age-based filtering
    # ============================
    allowed_by_age = []
    
    if age < 15:
        allowed_by_age = ['health']
    elif 15 <= age <= 45:
        allowed_by_age = ['health', 'auto', 'home', 'travel']
    else:  # age > 45
        allowed_by_age = ['health', 'life']
    
    filtered = []
    for policy in policies:
        if policy.get('policy_type') in allowed_by_age:
            filtered.append(policy)
            filter_details['age_filtered'].append(policy.get('title', 'Unknown'))
    
    # STEP 2: Risk-based filtering
    # =============================
    if risk_profile == 'high':
        # High risk users can ONLY get health policies
        filtered = [p for p in filtered if p.get('policy_type') == 'health']
        filter_details['risk_filtered'] = [p.get('title', 'Unknown') for p in filtered]
    
    # STEP 3: Preferred policy types filtering
    # ==========================================
    if preferred_types:
        # If user specified preferences, STRICTLY enforce them
        # Only include policies matching preferred types
        filtered = [p for p in filtered if p.get('policy_type') in preferred_types]
        filter_details['preferred_type_filtered'] = [p.get('title', 'Unknown') for p in filtered]
    
    # STEP 4: Max premium filtering
    # ==============================
    if max_premium:
        # STRICTLY exclude policies exceeding max premium
        filtered = [p for p in filtered if Decimal(str(p.get('premium', 0))) <= Decimal(str(max_premium))]
        filter_details['budget_filtered'] = [p.get('title', 'Unknown') for p in filtered]
    
    filter_details['final_count'] = len(filtered)
    
    # Log filtering results
    print(f"\n=== POLICY FILTERING (STRICT MODE) ===")
    print(f"Initial policies: {filter_details['initial_count']}")
    print(f"Age filter (age={age}): {len(filter_details['age_filtered'])} policies remain")
    if risk_profile == 'high':
        print(f"Risk filter (high risk): Health only")
    print(f"Preferred types: {preferred_types if preferred_types else 'None (all allowed)'}")
    print(f"Max premium: {f'₹{max_premium}' if max_premium else 'No limit'}")
    print(f"Final policies after ALL filters: {filter_details['final_count']}")
    print(f"Filtered policies: {[p.get('title') for p in filtered]}")
    print("=" * 40)
    
    return filtered, filter_details

def calculate_policy_score(policy: Dict[str, Any], user_data: Dict[str, Any], risk_profile: str) -> Decimal:
    """
    Calculate a score (0-100) for a policy based on user preferences and risk profile.
    
    Scoring Factors:
    - Coverage matching (35 points)
    - Premium affordability (25 points)
    - Risk & health alignment (25 points)
    - Policy type fit (10 points)
    - Provider rating (5 points)
    """
    score = Decimal(0)
    
    # Extract preferences from user_data
    preferences = user_data.get('preferences', {})
    health_data = user_data.get('health_data', {})
    demographics = user_data.get('demographics', {})
    
    # Factor 1: Coverage Matching (35 points max)
    coverage_match = calculate_coverage_match(policy, preferences)
    score += Decimal(35) * coverage_match
    
    # Factor 2: Premium Affordability (25 points max)
    premium_score = calculate_premium_score(policy, preferences, demographics)
    score += Decimal(25) * premium_score
    
    # Factor 3: Health & Risk Alignment (25 points max)
    health_score = calculate_health_risk_alignment(policy, health_data, risk_profile, demographics)
    score += Decimal(25) * health_score
    
    # Factor 4: Policy Type Fit (10 points max)
    type_score = calculate_policy_type_fit(policy, preferences, health_data)
    score += Decimal(10) * type_score
    
    # Factor 5: Provider Rating (5 points max)
    provider_score = calculate_provider_score(policy)
    score += Decimal(5) * provider_score
    
    return min(score.quantize(Decimal('0.01')), Decimal(100))


def calculate_coverage_match(policy: Dict[str, Any], preferences: Dict[str, Any]) -> Decimal:
    """
    Calculate how well the policy coverage matches user preferences.
    Returns value between 0 and 1 (to be multiplied by 35).
    """
    if not preferences or not policy.get('coverage'):
        return Decimal('0.5')  # Default medium match
    
    policy_type = policy.get('policy_type', '')
    preferred_types = preferences.get('preferred_policy_types', [])
    
    # Check if policy type is preferred
    type_match = Decimal(0.3)  # Base score
    if preferred_types and policy_type in preferred_types:
        type_match = Decimal(1.0)  # Full match
    elif preferred_types:
        type_match = Decimal(0.4)  # Partial match
    
    # Check specific coverages
    required_coverages = preferences.get('required_coverages', [])
    policy_coverage = policy.get('coverage', {})
    
    if not required_coverages:
        return type_match * Decimal('0.8')
    
    matches = 0
    for coverage in required_coverages:
        if coverage in policy_coverage and policy_coverage[coverage]:
            matches += 1
    
    coverage_ratio = Decimal(matches) / Decimal(len(required_coverages)) if required_coverages else Decimal(0.5)
    
    # Combine type match (30%) and coverage match (70%)
    combined = (type_match * Decimal('0.3')) + (coverage_ratio * Decimal('0.7'))
    return min(combined, Decimal(1))


def calculate_premium_score(policy: Dict[str, Any], preferences: Dict[str, Any], demographics: Dict[str, Any]) -> Decimal:
    """
    Calculate score based on premium affordability and income ratio.
    Higher score if premium is reasonable relative to income.
    Returns value between 0 and 1.
    """
    max_premium = preferences.get('max_premium')
    income = demographics.get('income', 0)
    policy_premium = Decimal(str(policy.get('premium', 0)))
    
    # If no max_premium set, use income-based calculation (5% of annual income)
    if not max_premium and income:
        max_prem = Decimal(str(income)) * Decimal('0.05')
    elif max_premium:
        max_prem = Decimal(str(max_premium))
    else:
        return Decimal('0.5')  # Default
    
    if policy_premium <= max_prem:
        # Bonus for being under budget - scales from 0.6 to 1.0
        ratio = policy_premium / max_prem if max_prem > 0 else Decimal(0)
        score = Decimal('0.6') + ((Decimal(1) - ratio) * Decimal('0.4'))
        return min(score, Decimal(1))
    else:
        # Penalty for exceeding budget
        overage_ratio = (policy_premium - max_prem) / max_prem
        # Scale from 0.4 down to near 0
        score = Decimal('0.4') - (overage_ratio * Decimal('0.35'))
        return max(score, Decimal(0.05))


def calculate_health_risk_alignment(
    policy: Dict[str, Any], 
    health_data: Dict[str, Any], 
    risk_profile: str,
    demographics: Dict[str, Any]
) -> Decimal:
    """
    Calculate how well policy aligns with user's health conditions and risk profile.
    Considers age, health conditions, BMI, and risk tolerance.
    Returns value between 0 and 1.
    """
    score = Decimal('0.5')  # Base score
    
    policy_type = policy.get('policy_type', '')
    
    # Health-specific scoring
    bmi = health_data.get('bmi')
    diseases = health_data.get('diseases', [])
    age = demographics.get('age', 30)
    
    # Health policy recommendations
    if policy_type == 'health':
        # Health policies are always good for anyone
        base_health_score = Decimal('0.9')
        
        # Boost for overweight/obese BMI
        if bmi and bmi > 25:
            base_health_score = Decimal('0.95')
        
        # Boost for existing diseases
        if diseases and len(diseases) > 0:
            base_health_score = Decimal('0.98')
        
        score = base_health_score
    
    # Life insurance recommendations
    elif policy_type == 'life':
        # Good for young adults and families
        if age < 50:
            score = Decimal('0.85')
        else:
            score = Decimal('0.75')
    
    # Auto insurance recommendations
    elif policy_type == 'auto':
        # Good for general risk management
        score = Decimal('0.7')
    
    # Home insurance recommendations
    elif policy_type == 'home':
        # Good for homeowners (neutral for renters)
        score = Decimal('0.75')
    
    # Travel insurance recommendations
    elif policy_type == 'travel':
        # Good for younger demographics
        if age < 40:
            score = Decimal('0.8')
        else:
            score = Decimal('0.6')
    
    # Risk profile adjustment (conservative/moderate/aggressive)
    if risk_profile == 'conservative':
        # Conservative users prefer essential, proven policies
        if policy_type in ['health', 'life']:
            score *= Decimal('1.1')
        else:
            score *= Decimal('0.95')
    elif risk_profile == 'aggressive':
        # Aggressive users willing to try comprehensive options
        score *= Decimal('1.15')
    
    return min(score, Decimal(1))


def calculate_policy_type_fit(
    policy: Dict[str, Any], 
    preferences: Dict[str, Any],
    health_data: Dict[str, Any]
) -> Decimal:
    """
    Calculate how well the policy type fits user's specific needs.
    Returns value between 0 and 1.
    """
    policy_type = policy.get('policy_type', '')
    preferred_types = preferences.get('preferred_policy_types', [])
    
    # Perfect match
    if preferred_types and policy_type in preferred_types:
        return Decimal('1.0')
    
    # Strong fit for health policies if user has health conditions
    diseases = health_data.get('diseases', [])
    if policy_type == 'health' and diseases:
        return Decimal('0.95')
    
    # Default match
    if preferred_types:
        return Decimal('0.4')
    
    return Decimal('0.6')


def calculate_provider_score(policy: Dict[str, Any]) -> Decimal:
    """
    Calculate provider rating score.
    Returns value between 0 and 1.
    """
    # In a real system, this would check provider ratings database
    # For now, use a default good rating
    return Decimal('0.85')


def rank_policies(
    policies: List[Dict[str, Any]], 
    user_preferences: Dict[str, Any],
    risk_profile: str,
    user_full_data: Dict[str, Any] = None,
    top_n: int = 5
) -> List[tuple]:
    """
    Score and rank policies for a user.
    
    CRITICAL: First applies STRICT FILTERING, then scores remaining policies.
    Only policies that pass ALL filters are included in recommendations.
    
    Returns list of tuples: (policy, score, reason)
    """
    # Prepare comprehensive user data for scoring
    user_data = {
        'preferences': user_preferences,
        'health_data': {},
        'demographics': {}
    }
    
    if user_full_data:
        user_data['health_data'] = {
            'bmi': user_full_data.get('bmi'),
            'diseases': user_full_data.get('diseases', []),
            'age': user_full_data.get('age'),
            'height': user_full_data.get('height'),
            'weight': user_full_data.get('weight')
        }
        user_data['demographics'] = {
            'age': user_full_data.get('age'),
            'income': user_full_data.get('income'),
            'has_kids': user_full_data.get('has_kids'),
            'marital_status': user_full_data.get('marital_status')
        }
    
    # STEP 1: STRICTLY FILTER policies before scoring
    filtered_policies, filter_details = filter_policies(policies, user_data, risk_profile)
    
    # If no policies remain after filtering, return empty
    if not filtered_policies:
        print(f"\n⚠️  WARNING: No policies match user filters!")
        print(f"  - User preferences: {user_preferences}")
        print(f"  - Risk profile: {risk_profile}")
        return []
    
    # STEP 2: Score remaining policies
    scored_policies = []
    
    for policy in filtered_policies:
        score = calculate_policy_score(policy, user_data, risk_profile)
        reason = generate_recommendation_reason(policy, user_data, risk_profile, score)
        scored_policies.append((policy, score, reason))
    
    # Sort by score descending
    scored_policies.sort(key=lambda x: x[1], reverse=True)
    
    # Log scores for debugging
    print(f"\n=== Policy Rankings for risk_profile={risk_profile} ===")
    print(f"Policies to score: {len(filtered_policies)} (after filtering from {filter_details['initial_count']})")
    for i, (policy, score, reason) in enumerate(scored_policies[:top_n], 1):
        print(f"{i}. {policy['title']}: {score}/100 - {reason}")
    print("=" * 50)
    
    return scored_policies[:top_n]


def generate_recommendation_reason(
    policy: Dict[str, Any],
    user_data: Dict[str, Any],
    risk_profile: str,
    score: Decimal
) -> str:
    """Generate human-readable reason for the recommendation."""
    reasons = []
    
    preferences = user_data.get('preferences', {})
    health_data = user_data.get('health_data', {})
    
    # Coverage match
    coverage_match = calculate_coverage_match(policy, preferences)
    if coverage_match >= Decimal('0.8'):
        reasons.append("Excellent coverage match")
    elif coverage_match >= Decimal('0.6'):
        reasons.append("Good coverage alignment")
    
    # Premium affordability
    max_prem = preferences.get('max_premium', 0)
    income = user_data.get('demographics', {}).get('income', 0)
    policy_prem = Decimal(str(policy.get('premium', 0)))
    
    if max_prem and policy_prem <= Decimal(str(max_prem)):
        reasons.append(f"Within budget (${policy_prem})")
    elif income:
        income_pct = (policy_prem / Decimal(str(income)) * Decimal(100)).quantize(Decimal('0.1'))
        reasons.append(f"Affordable ({income_pct}% of annual income)")
    
    # Health alignment
    diseases = health_data.get('diseases', [])
    if policy.get('policy_type') == 'health' and diseases:
        reasons.append(f"Ideal for your health conditions")
    
    # Risk fit
    if risk_profile:
        reasons.append(f"Matches {risk_profile} profile")
    
    if not reasons:
        reasons.append(f"Score: {score}/100")
    
    return " • ".join(reasons[:3])  # Limit to 3 reasons
