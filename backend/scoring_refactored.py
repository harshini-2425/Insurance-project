"""
REFACTORED Policy Scoring & Recommendation Engine
Implements STRICT POLICY-TYPE filtering FIRST, then soft constraints via scoring
"""

from decimal import Decimal
from typing import List, Dict, Any, Tuple

# =====================================================================
# STAGE 1: STRICT POLICY-TYPE FILTERING
# =====================================================================

def filter_by_policy_type(
    policies: List[Dict[str, Any]],
    user_policy_preferences: List[str]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    STAGE 1: STRICT filter by user-selected policy types.
    
    This is the PRIMARY and MOST RESTRICTIVE filter.
    If user selects policy types, ONLY those types are returned.
    
    Args:
        policies: All available policies
        user_policy_preferences: User's selected policy types (e.g., ['health', 'life'])
    
    Returns:
        - Filtered policies matching user's policy type selection
        - Filter metadata for logging
    """
    
    filter_result = {
        'stage': 'policy_type_filtering',
        'initial_count': len(policies),
        'selected_types': user_policy_preferences if user_policy_preferences else 'ANY',
        'policies_by_type': {},
        'eliminated_count': 0,
        'final_count': 0
    }
    
    # If user has NO preferences, return all policies (no filtering)
    if not user_policy_preferences:
        filter_result['final_count'] = len(policies)
        return policies, filter_result
    
    # STRICT: Only keep policies matching user's selected types
    filtered = []
    for policy in policies:
        policy_type = policy.get('policy_type', '')
        
        if policy_type not in filter_result['policies_by_type']:
            filter_result['policies_by_type'][policy_type] = 0
        filter_result['policies_by_type'][policy_type] += 1
        
        if policy_type in user_policy_preferences:
            filtered.append(policy)
    
    filter_result['eliminated_count'] = len(policies) - len(filtered)
    filter_result['final_count'] = len(filtered)
    
    return filtered, filter_result


# =====================================================================
# STAGE 2: SECONDARY SOFT CONSTRAINTS (Via Scoring, Not Hard Removal)
# =====================================================================

def calculate_policy_score(
    policy: Dict[str, Any],
    user_data: Dict[str, Any],
    risk_profile: str
) -> Decimal:
    """
    Calculate composite score (0-100) for a policy.
    
    Scoring Factors (Soft Constraints - not hard removal):
    1. Coverage Matching: 35 points (does policy cover user's needs?)
    2. Premium Affordability: 25 points (within budget?)
    3. Health & Risk Alignment: 25 points (suits user's profile?)
    4. Policy Type Fit: 10 points (how suitable for user's situation?)
    5. Provider Rating: 5 points (provider reputation)
    
    All factors are SCORING-BASED, not filtering-based.
    Even if a policy has low affordability score, it's not removed.
    """
    
    demographics = user_data.get('demographics', {})
    preferences = user_data.get('preferences', {})
    health = user_data.get('health', {})
    
    # Calculate each scoring component (0-1 scale)
    coverage_score = calculate_coverage_match(policy, preferences) * 35
    premium_score = calculate_premium_score(policy, preferences, demographics) * 25
    health_score = calculate_health_risk_alignment(policy, risk_profile, health) * 25
    type_fit_score = calculate_policy_type_fit(policy, preferences, demographics) * 10
    provider_score = calculate_provider_score(policy) * 5
    
    # Composite score (0-100)
    total_score = coverage_score + premium_score + health_score + type_fit_score + provider_score
    
    return Decimal(str(total_score)).quantize(Decimal('0.01'))


def calculate_coverage_match(
    policy: Dict[str, Any],
    preferences: Dict[str, Any]
) -> Decimal:
    """
    Coverage Matching Score (0-1, multiplied by 35)
    
    How well does this policy cover the user's needs?
    
    Components:
    - Type match: Is this policy type in user's preferences? (30% weight)
    - Coverage detail: Does it cover specific needs? (70% weight)
    """
    
    policy_type = policy.get('policy_type', '')
    coverage = policy.get('coverage', {})
    preferred_types = preferences.get('preferred_policy_types', [])
    
    # Type match (30% weight)
    if policy_type in preferred_types:
        type_match_score = Decimal('1.0')  # Perfect match
    elif not preferred_types:
        type_match_score = Decimal('0.3')  # No preferences set
    else:
        type_match_score = Decimal('0.4')  # Not in preferences
    
    # Coverage detail match (70% weight)
    coverage_detail_score = Decimal('0.8')  # Default: most policies have good coverage
    
    # Specific policy type coverage bonuses
    if policy_type == 'health':
        coverage_detail_score = Decimal('0.9')  # Health plans typically comprehensive
    elif policy_type == 'life':
        coverage_detail_score = Decimal('0.85')
    elif policy_type == 'auto':
        coverage_detail_score = Decimal('0.75')
    elif policy_type == 'home':
        coverage_detail_score = Decimal('0.8')
    elif policy_type == 'travel':
        coverage_detail_score = Decimal('0.8')
    
    # Combine: Type match (30%) + Coverage detail (70%)
    combined_score = (type_match_score * Decimal('0.30')) + (coverage_detail_score * Decimal('0.70'))
    
    return combined_score


def calculate_premium_score(
    policy: Dict[str, Any],
    preferences: Dict[str, Any],
    demographics: Dict[str, Any]
) -> Decimal:
    """
    Premium Affordability Score (0-1, multiplied by 25)
    
    How affordable is this policy relative to user's budget?
    
    Scoring:
    - If within budget: 0.6 to 1.0 (higher if significantly under budget)
    - If exceeds budget: 0.05 to 0.4 (penalty based on overage)
    - If no budget set: Use income-based threshold or default 0.5
    """
    
    premium = Decimal(str(policy.get('premium', 0)))
    max_premium = preferences.get('max_premium')
    income = demographics.get('income')
    
    # Determine affordability threshold
    if max_premium:
        threshold = Decimal(str(max_premium))
    elif income:
        # 5% of annual income per month as threshold
        threshold = Decimal(str(income)) * Decimal('0.05') / Decimal('12')
    else:
        # No limit: score based on relative affordability
        return Decimal('0.5')
    
    # Score based on premium vs threshold
    if premium <= threshold:
        # Within budget: bonus score (0.6 to 1.0)
        ratio = premium / threshold
        score = Decimal('0.60') + ((Decimal('1') - ratio) * Decimal('0.40'))
    else:
        # Exceeds budget: penalty score (0.05 to 0.4)
        overage_ratio = (premium - threshold) / threshold
        score = Decimal('0.40') - (overage_ratio * Decimal('0.35'))
        score = max(score, Decimal('0.05'))  # Floor at 0.05
    
    return score


def calculate_health_risk_alignment(
    policy: Dict[str, Any],
    risk_profile: str,
    health_data: Dict[str, Any]
) -> Decimal:
    """
    Health & Risk Alignment Score (0-1, multiplied by 25)
    
    How well does this policy align with user's health and risk profile?
    
    Scoring varies by policy type:
    - Health policies: 0.90-0.98 base, +bonuses for user health conditions
    - Life policies: 0.75-0.85 depending on age
    - Auto/Home/Travel: Standard 0.70-0.80
    
    Risk profile adjustments:
    - Conservative: Health/Life × 1.1, Others × 0.95
    - Moderate: No adjustment
    - Aggressive: All policies × 1.15
    """
    
    policy_type = policy.get('policy_type', '')
    bmi = health_data.get('bmi')
    diseases = health_data.get('diseases', [])
    age = health_data.get('age', 30)
    
    # Base score by policy type
    if policy_type == 'health':
        base_score = Decimal('0.90')
        
        # Bonuses for health conditions
        if bmi and bmi > 25:
            base_score += Decimal('0.05')  # Overweight benefits from health coverage
        
        if diseases:
            base_score += Decimal('0.03') * Decimal(str(len(diseases)))  # Bonus per disease
        
        base_score = min(base_score, Decimal('1.0'))  # Cap at 1.0
    
    elif policy_type == 'life':
        base_score = Decimal('0.85') if age < 50 else Decimal('0.75')
    
    elif policy_type == 'auto':
        base_score = Decimal('0.70')
    
    elif policy_type == 'home':
        base_score = Decimal('0.75')
    
    elif policy_type == 'travel':
        base_score = Decimal('0.80') if age < 40 else Decimal('0.60')
    
    else:
        base_score = Decimal('0.70')
    
    # Apply risk profile adjustment
    if risk_profile == 'conservative':
        if policy_type in ['health', 'life']:
            adjustment = Decimal('1.10')  # +10% boost
        else:
            adjustment = Decimal('0.95')  # -5% penalty
    
    elif risk_profile == 'aggressive':
        adjustment = Decimal('1.15')  # +15% boost for risk-takers
    
    else:  # moderate
        adjustment = Decimal('1.00')  # No adjustment
    
    final_score = base_score * adjustment
    return min(final_score, Decimal('1.0'))


def calculate_policy_type_fit(
    policy: Dict[str, Any],
    preferences: Dict[str, Any],
    demographics: Dict[str, Any]
) -> Decimal:
    """
    Policy Type Fit Score (0-1, multiplied by 10)
    
    How well suited is this specific policy type for the user's situation?
    
    Scoring:
    - In preferred types: 1.00 (perfect fit)
    - Health policy + user has diseases: 0.95 (well-suited)
    - Not in preferred types: 0.40
    - Generic fit: 0.60
    """
    
    policy_type = policy.get('policy_type', '')
    preferred_types = preferences.get('preferred_policy_types', [])
    diseases = demographics.get('diseases', [])
    
    if policy_type in preferred_types:
        return Decimal('1.00')  # Perfect fit
    
    if policy_type == 'health' and diseases:
        return Decimal('0.95')  # Health policy is well-suited for sick users
    
    if not preferred_types:
        return Decimal('0.60')  # No preferences: generic fit
    
    return Decimal('0.40')  # Not in preferences: low fit


def calculate_provider_score(policy: Dict[str, Any]) -> Decimal:
    """
    Provider Rating Score (0-1, multiplied by 5)
    
    Provider reputation and rating.
    Current implementation: Default 0.85
    Future enhancement: Load real provider ratings from database
    """
    
    # Placeholder: In production, load from ProviderRating table
    return Decimal('0.85')


def generate_recommendation_reason(
    policy: Dict[str, Any],
    score: Decimal,
    user_data: Dict[str, Any]
) -> str:
    """
    Generate human-readable explanation for why this policy is recommended.
    
    Creates 2-3 sentence explanation highlighting key reasons.
    """
    
    policy_title = policy.get('title', '')
    policy_type = policy.get('policy_type', '')
    premium = Decimal(str(policy.get('premium', 0)))
    coverage_amount = policy.get('coverage_amount', 0)
    
    demographics = user_data.get('demographics', {})
    preferences = user_data.get('preferences', {})
    
    max_premium = preferences.get('max_premium')
    preferred_types = preferences.get('preferred_policy_types', [])
    diseases = demographics.get('diseases', [])
    
    reasons = []
    
    # Reason 1: Coverage match
    if policy_type in preferred_types:
        reasons.append("Matches your preferred policy type")
    elif policy_type == 'health' and diseases:
        reasons.append(f"Ideal for managing your health conditions")
    else:
        reasons.append("Good coverage match")
    
    # Reason 2: Budget fit
    if max_premium and premium <= Decimal(str(max_premium)):
        reasons.append(f"Within your budget (₹{premium:,.0f})")
    else:
        reasons.append(f"Good value coverage (₹{premium:,.0f})")
    
    # Reason 3: Coverage amount
    if coverage_amount >= 1000000:
        reasons.append(f"Strong coverage (₹{coverage_amount:,.0f})")
    else:
        reasons.append("Solid protection")
    
    # Combine reasons (select 2-3)
    selected_reasons = reasons[:3]
    return " • ".join(selected_reasons)


# =====================================================================
# MAIN ENTRY POINT: RANK POLICIES
# =====================================================================

def rank_policies(
    policies: List[Dict[str, Any]],
    preferences: Dict[str, Any],
    risk_profile: str,
    user_data: Dict[str, Any],
    top_n: int = 10
) -> List[Tuple[Dict[str, Any], Decimal, str]]:
    """
    MAIN ENTRY POINT for recommendation engine.
    
    Two-stage process:
    STAGE 1 (STRICT): Filter policies by user-selected policy types
    STAGE 2 (SOFT): Score remaining policies and rank them
    
    Args:
        policies: All available policies
        preferences: User preferences (preferred_policy_types, max_premium, etc.)
        risk_profile: User's risk profile (conservative/moderate/aggressive)
        user_data: Comprehensive user data (age, health, income, etc.)
        top_n: Number of recommendations to return (default 10)
    
    Returns:
        List of (policy, score, reason) tuples, ranked by score descending
    """
    
    print("\n" + "="*70)
    print("RECOMMENDATION ENGINE - TWO STAGE PROCESS")
    print("="*70)
    
    # Extract policy type preferences
    preferred_types = preferences.get('preferred_policy_types', [])
    
    # ===== STAGE 1: STRICT POLICY-TYPE FILTERING =====
    print("\n[STAGE 1] STRICT POLICY-TYPE FILTERING")
    print("-" * 70)
    
    filtered_policies, filter_metadata = filter_by_policy_type(policies, preferred_types)
    
    print(f"  Initial policies: {filter_metadata['initial_count']}")
    print(f"  Selected policy types: {filter_metadata['selected_types']}")
    print(f"  Policies by type: {filter_metadata['policies_by_type']}")
    print(f"  Policies eliminated: {filter_metadata['eliminated_count']}")
    print(f"  Policies remaining: {filter_metadata['final_count']}")
    
    if not filtered_policies:
        print("\n  ⚠️ No policies match user's selected policy types!")
        return []
    
    # ===== STAGE 2: SCORING & RANKING =====
    print("\n[STAGE 2] SCORING & RANKING")
    print("-" * 70)
    
    scored_policies = []
    for policy in filtered_policies:
        score = calculate_policy_score(policy, user_data, risk_profile)
        reason = generate_recommendation_reason(policy, score, user_data)
        scored_policies.append((policy, score, reason))
    
    # Sort by score descending
    scored_policies.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N
    top_recommendations = scored_policies[:top_n]
    
    print(f"  Policies scored: {len(scored_policies)}")
    print(f"  Top {top_n} recommendations returned:")
    
    for i, (policy, score, reason) in enumerate(top_recommendations, 1):
        print(f"    {i}. {policy['title']:40} | Score: {score}/100")
    
    print("\n" + "="*70 + "\n")
    
    return top_recommendations
