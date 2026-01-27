# 🔒 STRICT RECOMMENDATION FILTERING - Implementation Guide

## Overview
The recommendation system now applies **AGGRESSIVE FILTERING BEFORE SCORING** to strictly respect user preferences.

## Filtering Stages (Applied in Order)

### Stage 1: Age-Based Filtering
```python
age < 15 → ONLY: health
15 ≤ age ≤ 45 → ONLY: health, auto, home, travel  
age > 45 → ONLY: health, life
```

**Examples:**
- 12-year-old: Only health policies (schools require this)
- 35-year-old: Health, auto, home, travel available
- 55-year-old: Only health, life (most relevant)

### Stage 2: Risk-Based Filtering
```python
If risk_profile == 'high':
  → ONLY health policies allowed
  → All other types are EXCLUDED
```

**Examples:**
- Conservative risk: All age-appropriate types available
- Moderate risk: All age-appropriate types available
- **High risk: ONLY health policies** (strict!)

### Stage 3: Preferred Policy Types Filtering
```python
If preferred_policy_types is specified:
  → ONLY include policies matching preferred types
  → EXCLUDE all other types (even age-appropriate ones)
```

**Examples:**
```
User selects: ["health", "life"]
Available: health, auto, home, travel
Result: ONLY health, life policies shown

User selects: ["home"]
Available: health, auto, home, travel
Result: ONLY home policies shown
```

### Stage 4: Max Premium Filtering
```python
If max_premium is specified:
  → EXCLUDE policies with premium > max_premium
  → Only policies within budget remain
```

**Examples:**
```
Max Premium: ₹15,000
Policies:
  - Health (₹2,000) → INCLUDED ✅
  - Health (₹8,000) → INCLUDED ✅
  - Home (₹16,000) → EXCLUDED ❌ (over budget)
  - Life (₹5,000) → EXCLUDED ❌ (not preferred type)
```

## Filter Combination Examples

### Example 1: Home + ₹15,000 Budget
```
User Profile:
- Age: 35
- Preferred Types: ["home"]
- Max Premium: ₹15,000
- Risk: moderate

Filtering Process:
1. Age filter: 35 → home allowed ✅
2. Risk filter: moderate → all types allowed ✅
3. Type filter: only home → STRICT
4. Budget filter: max ₹15,000

Result: ONLY home policies ≤ ₹15,000
  ✅ Home Basic (₹8,000)
  ✅ Home Plus (₹12,000)
  ❌ Home Premium (₹18,000) - over budget
  ❌ Health (₹5,000) - wrong type
```

### Example 2: High-Risk User
```
User Profile:
- Age: 40
- Preferred Types: ["health", "life"]
- Risk: HIGH
- Max Premium: ₹50,000

Filtering Process:
1. Age filter: 40 → health, auto, home, travel allowed
2. Risk filter: HIGH → ONLY health ✅
3. Type filter: preferred [health, life] → ONLY health
4. Budget filter: max ₹50,000

Result: ONLY health policies ≤ ₹50,000
  ✅ Premium Health (₹7,500)
  ✅ Family Health (₹12,000)
  ❌ Life Insurance (₹8,000) - high risk can't buy life
  ❌ Auto Insurance (₹5,000) - high risk can't buy auto
```

### Example 3: Young + Limited Budget
```
User Profile:
- Age: 28
- Preferred Types: []  (none specified, all allowed)
- Max Premium: ₹5,000
- Risk: low

Filtering Process:
1. Age filter: 28 → health, auto, home, travel allowed
2. Risk filter: low → all allowed ✅
3. Type filter: none specified → all allowed ✅
4. Budget filter: max ₹5,000

Result: All age-appropriate types ≤ ₹5,000
  ✅ Health Basic (₹2,500)
  ✅ Travel (₹1,500)
  ✅ Auto (₹4,500)
  ❌ Health Premium (₹8,000) - over budget
  ❌ Home (₹7,000) - over budget
```

## Implementation Details

### In scoring.py

```python
def filter_policies(
    policies: List[Dict[str, Any]],
    user_data: Dict[str, Any],
    risk_profile: str
) -> Tuple[List[Dict[str, Any]], Dict[str, List[str]]]:
    """
    Apply STRICT filtering BEFORE scoring.
    """
```

**Filtering Logic:**
1. Extract user preferences: age, max_premium, preferred_types
2. Calculate age-allowed types
3. Apply risk filter (high → health only)
4. Apply preferred type filter (if specified)
5. Apply budget filter (if specified)
6. Return filtered list

**Return Value:**
- List of policies that passed ALL filters
- Dictionary with filtering details for logging

### In main.py

**POST /recommendations/generate:**
```python
# Step 1: rank_policies() is called
# Step 2: rank_policies() calls filter_policies()
# Step 3: Only filtered policies are scored
# Step 4: Only scored policies are saved to DB

# Additional validation before saving:
if not in preferred_types:
    continue  # Skip
if premium > max_premium:
    continue  # Skip
# Save only policies that passed ALL filters
```

## API Response Examples

### Success Response (Filters Applied)
```json
[
  {
    "id": 1,
    "policy_id": 5,
    "score": 92.5,
    "reason": "Perfect match for your home insurance needs",
    "policy": {
      "id": 5,
      "title": "Home Insurance Standard",
      "premium": 12000,
      "policy_type": "home"
    }
  }
]
```

### No Matches Response
```json
{
  "message": "No policies match your filters",
  "details": "Your preferences (type: ['home'], max: 15000) and risk profile (moderate) didn't match any available policies.",
  "recommendations": []
}
```

## Testing Strict Filtering

### Test Case 1: Single Policy Type
```
Setup:
- User selects: ["home"]
- Max premium: ₹15,000
- Available policies: 50 total

Expected:
- Only home policies shown
- Only those ≤ ₹15,000
- All other policies EXCLUDED

Verify:
- Check response contains ONLY home policies
- Check all policies < 15000
- Check count matches filtered set
```

### Test Case 2: High-Risk User
```
Setup:
- Risk profile: high
- Preferred types: ["health", "auto", "home"]
- Max premium: ₹20,000

Expected:
- ONLY health policies shown
- Auto and home EXCLUDED despite being preferred
- Premium filter also applied

Verify:
- All policies type == "health"
- All policies premium ≤ 20000
- Auto/home not included even though preferred
```

### Test Case 3: Age + Budget Combination
```
Setup:
- Age: 25
- Max premium: ₹3,000
- Preferred types: []

Expected:
- Age-appropriate: health, auto, home, travel
- But only those ≤ ₹3,000
- May have 0-2 matches depending on available policies

Verify:
- Policy type in [health, auto, home, travel]
- Premium ≤ 3000
- Result may be empty (valid outcome)
```

## Logging Output

When preferences are saved or recommendations generated, check backend logs:

```
=== POLICY FILTERING (STRICT MODE) ===
Initial policies: 50
Age filter (age=35): 45 policies remain
Preferred types: ['home']
Max premium: ₹15,000
Final policies after ALL filters: 3
Filtered policies: ['Home Standard', 'Home Plus', 'Home Deluxe']
========================================

=== Policy Rankings for risk_profile=moderate ===
Policies to score: 3 (after filtering from 50)
1. Home Deluxe: 89.5/100 - Excellent coverage match • Perfect for budget
2. Home Plus: 87.2/100 - Good coverage • Within budget
3. Home Standard: 82.1/100 - Basic coverage • Best budget fit
==================================================
```

## FAQ

### Q: What if a user selects multiple policy types?
**A:** All selected types are included in recommendations (after passing age/risk filters)

### Q: What if no policies match?
**A:** Returns empty recommendations with explanation message

### Q: Can high-risk users get non-health policies?
**A:** NO - high risk → health only, regardless of preferences

### Q: Can user exceed their stated budget?
**A:** NO - all policies must be ≤ max_premium

### Q: Are age filters strict?
**A:** YES - strictly enforced, no exceptions

### Q: Can I override filters?
**A:** NO - filters are hard requirements, not preferences

## Edge Cases Handled

✅ No preferred types specified → Age-appropriate types allowed  
✅ High risk overrides preferred types → Health only  
✅ Zero policies match filters → Returns empty array  
✅ Max premium not specified → No budget filter applied  
✅ Age boundary cases (15, 45) → Properly categorized  
✅ Very restrictive filters → Returns "no matches" message  

## Future Enhancements

- [ ] Allow users to adjust filters and see updated recommendations
- [ ] Show why a policy was filtered out
- [ ] Suggest relaxing filters when no matches found
- [ ] Save filter history for analytics
- [ ] Recommend policies if user relaxes constraints
