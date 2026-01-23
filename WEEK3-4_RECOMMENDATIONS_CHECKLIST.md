# 📋 WEEK 3-4 TASK CHECKLIST: RECOMMENDATIONS ENGINE (Module C)

## Overview
Implement personalized policy recommendations based on user preferences and scoring algorithm.

---

## 🎯 WEEK 3: Collect User Preferences

### Task 1: Create Preference Collection Form
**File**: `c:\newproject\frontend-react\src\pages\Preferences.jsx` (NEW)

**Components needed**:
- Policy type preferences (checkboxes): auto, health, life, home, travel
- Budget preference (radio buttons): Budget ($25-100), Mid-range ($100-300), Premium ($300+)
- Coverage priorities (drag-to-rank or importance rating)
- Deductible preference (low/medium/high)
- Term preference (short/medium/long)

**Styling**: 
- Match existing pages (400px max-width preferred, but can be form layout)
- Save button, Cancel button
- Success message after save

### Task 2: Create Backend Endpoint
**File**: `c:\newproject\backend\main.py` (ADD ENDPOINT)

```python
@app.post("/user/preferences", response_model=schemas.UserOut)
def save_preferences(
    preferences: schemas.PreferencesUpdate,  # NEW SCHEMA
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Save user preferences for recommendations"""
    user = get_current_user(token, db)
    user.risk_profile = preferences.dict()  # Save as JSON
    db.commit()
    db.refresh(user)
    return schemas.UserOut.from_orm(user)
```

### Task 3: Create Schema
**File**: `c:\newproject\backend\schemas.py` (ADD SCHEMA)

```python
class PreferencesUpdate(BaseModel):
    preferred_policy_types: List[str]  # ["auto", "health", ...]
    budget_level: str  # "budget", "mid-range", "premium"
    coverage_priorities: Dict[str, int]  # {"liability": 1, "medical": 2, ...}
    deductible_preference: str  # "low", "medium", "high"
    term_preference: str  # "short", "medium", "long"
```

### Task 4: Add Preferences Link to Header
**File**: `c:\newproject\frontend-react\src\components\Header.jsx` (MODIFY)

Add menu item: "⚙️ Preferences" → Navigate to `/preferences`

### Task 5: Update Router
**File**: `c:\newproject\frontend-react\src\App.jsx` (MODIFY)

Add route:
```javascript
<Route path="/preferences" element={<Preferences />} />
```

**Expected Output by End of Week 3**:
- Users can navigate to preferences form
- Form saves preferences to user.risk_profile (JSON)
- API returns saved preferences
- Preferences displayed on profile page

---

## 🎯 WEEK 4: Score & Recommend Policies

### Task 6: Create Scoring Algorithm
**File**: `c:\newproject\backend\recommendation_engine.py` (NEW)

```python
from decimal import Decimal

def score_policy_for_user(user, policy, db_session):
    """
    Score a policy for a user based on preferences.
    Returns score from 0-100
    """
    score = 0
    preferences = user.risk_profile or {}
    
    # 1. Policy type match (30 points max)
    preferred_types = preferences.get('preferred_policy_types', [])
    if policy.policy_type in preferred_types:
        score += 30
    
    # 2. Premium fit (25 points max)
    budget = preferences.get('budget_level', 'mid-range')
    budget_ranges = {
        'budget': (0, 100),
        'mid-range': (100, 300),
        'premium': (300, 1000)
    }
    min_budget, max_budget = budget_ranges[budget]
    if min_budget <= float(policy.premium) <= max_budget:
        score += 25
    else:
        # Partial credit if close
        score += max(0, 25 - (abs(float(policy.premium) - (min_budget + max_budget) / 2) / 50))
    
    # 3. Term preference (20 points max)
    term_pref = preferences.get('term_preference', 'medium')
    term_ranges = {
        'short': (0, 12),
        'medium': (12, 36),
        'long': (36, 600)
    }
    min_term, max_term = term_ranges[term_pref]
    if min_term <= policy.term_months <= max_term:
        score += 20
    
    # 4. Coverage match (25 points max)
    coverage_prefs = preferences.get('coverage_priorities', {})
    if policy.coverage:
        matches = sum(1 for key in coverage_prefs.keys() if key in policy.coverage)
        if matches > 0:
            score += min(25, matches * 5)
    
    return min(100, round(score, 2))  # Cap at 100
```

### Task 7: Create Recommendation Generation Endpoint
**File**: `c:\newproject\backend\main.py` (ADD ENDPOINT)

```python
@app.post("/recommendations/generate", response_model=list[schemas.RecommendationWithPolicy])
def generate_recommendations(
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Generate recommendations for user based on preferences"""
    user = get_current_user(token, db)
    
    # Clear old recommendations
    db.query(models.Recommendation).filter(
        models.Recommendation.user_id == user.id
    ).delete()
    
    # Score all policies
    from recommendation_engine import score_policy_for_user
    policies = db.query(models.Policy).all()
    
    recommendations = []
    for policy in policies:
        score = score_policy_for_user(user, policy, db)
        if score > 30:  # Only recommend if score > 30
            reason = f"Matches your preference for {policy.policy_type} insurance in the ${policy.premium}/mo range"
            rec = models.Recommendation(
                user_id=user.id,
                policy_id=policy.id,
                score=Decimal(str(score)),
                reason=reason
            )
            db.add(rec)
            recommendations.append(rec)
    
    db.commit()
    
    # Sort by score descending
    recommendations.sort(key=lambda r: r.score, reverse=True)
    
    return [schemas.RecommendationWithPolicy(
        **schemas.RecommendationOut.from_orm(r).dict(),
        policy=schemas.PolicyWithProvider(
            **schemas.PolicyOut.from_orm(r.policy).dict(),
            provider=schemas.ProviderOut.from_orm(r.policy.provider)
        )
    ) for r in recommendations[:10]]  # Top 10 recommendations
```

### Task 8: Create Recommendations Retrieval Endpoint
**File**: `c:\newproject\backend\main.py` (ADD ENDPOINT)

```python
@app.get("/recommendations", response_model=list[schemas.RecommendationWithPolicy])
def get_recommendations(
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get user's recommendations"""
    user = get_current_user(token, db)
    recommendations = db.query(models.Recommendation).filter(
        models.Recommendation.user_id == user.id
    ).order_by(models.Recommendation.score.desc()).limit(10).all()
    
    return [schemas.RecommendationWithPolicy(
        **schemas.RecommendationOut.from_orm(r).dict(),
        policy=schemas.PolicyWithProvider(
            **schemas.PolicyOut.from_orm(r.policy).dict(),
            provider=schemas.ProviderOut.from_orm(r.policy.provider)
        )
    ) for r in recommendations]
```

### Task 9: Create Recommendations Page
**File**: `c:\newproject\frontend-react\src\pages\Recommendations.jsx` (NEW)

**Features**:
- Display "Get Recommendations" button
- Show top 10 recommendations ranked by score
- Display score as progress bar (0-100)
- Show reason for each recommendation
- Link to policy details or purchase page
- Show "No recommendations" message if none match

**Layout**:
```
[Get Recommendations Button]

Recommendation 1: Policy A
Score: ████████░░ 85%
Reason: Matches your preference...
[View Policy] [Purchase]

Recommendation 2: Policy B
Score: ███████░░░ 78%
...
```

### Task 10: Add Recommendations to BrowsePolicies
**File**: `c:\newproject\frontend-react\src\pages\BrowsePolicies.jsx` (MODIFY)

Add:
- "Get Recommendations" button at top
- Recommended badge on policies that have recommendations
- Filter to show "Recommended for you" first

### Task 11: Update Router
**File**: `c:\newproject\frontend-react\src\App.jsx` (MODIFY)

Add route:
```javascript
<Route path="/recommendations" element={<Recommendations />} />
```

### Task 12: Update Header Navigation
**File**: `c:\newproject\frontend-react\src/components/Header.jsx` (MODIFY)

Add "Recommendations" link to menu

**Expected Output by End of Week 4**:
- Users can set preferences (budget, policy types, etc.)
- Click "Generate Recommendations" to see personalized list
- Top 10 policies recommended ranked by match score (0-100)
- Each recommendation shows reason for ranking
- Recommendations persist in database
- Can view recommended policies and purchase them

---

## ✅ CHECKLIST

### Week 3
- [ ] Create Preferences.jsx page
- [ ] Create PreferencesUpdate schema
- [ ] Add POST /user/preferences endpoint
- [ ] Add Preferences menu item to Header
- [ ] Test preferences saving
- [ ] Verify risk_profile JSON storage

### Week 4
- [ ] Create recommendation_engine.py with scoring algorithm
- [ ] Add POST /recommendations/generate endpoint
- [ ] Add GET /recommendations endpoint
- [ ] Create Recommendations.jsx page
- [ ] Add recommendation display with scores
- [ ] Add "Get Recommendations" button to BrowsePolicies
- [ ] Update router with /recommendations route
- [ ] Test full recommendation flow
- [ ] Verify scores are calculated correctly
- [ ] Test that recommendations persist in DB

---

## 🧪 TESTING SCENARIOS

### Test 1: Save Preferences
1. Go to `/preferences`
2. Select: Auto + Health insurance
3. Budget: Mid-range ($100-300)
4. Click Save
5. ✅ Should see "Preferences saved" message
6. ✅ Profile should show saved preferences

### Test 2: Generate Recommendations
1. After saving preferences (Test 1)
2. Go to `/recommendations`
3. Click "Get Recommendations"
4. ✅ Should see 5-10 policies ranked by score
5. ✅ Auto and Health policies should have higher scores
6. ✅ Policies in $100-300 range should rank higher

### Test 3: Recommendation Persistence
1. Generate recommendations (Test 2)
2. Close and reopen browser
3. Go to `/recommendations`
4. ✅ Same recommendations should still be there
5. ✅ Scores should be the same

### Test 4: Preference Update
1. Go to `/preferences`
2. Change budget to "Premium" ($300+)
3. Click "Regenerate Recommendations"
4. ✅ Higher-priced policies should now have better scores
5. ✅ Previous recommendations should be cleared

---

## 📊 SCORING ALGORITHM DETAILS

### Scoring Factors (Total 100 points)
1. **Policy Type Match** (30 points)
   - Full points if user prefers that type
   - 0 points if different type
   
2. **Premium Fit** (25 points)
   - Full points if within user's budget range
   - Decreases linearly if outside range
   
3. **Term Preference** (20 points)
   - Full points if within preferred term range
   - 0 points if significantly different
   
4. **Coverage Match** (25 points)
   - 5 points per coverage area preference that matches
   - Max 25 points

### Example Scoring
**User Preferences**:
- Preferred types: [auto, health]
- Budget: mid-range ($100-300)
- Term preference: medium (12-36 months)
- Coverage priorities: {liability: 1, medical: 2}

**Policy: Guardian Health Basic ($300, 12 months, health)**
- Type match: +30 (health is preferred) ✓
- Premium fit: +25 (exactly at max of $300) ✓
- Term: +20 (12 months is in range) ✓
- Coverage: +10 (medical matches) ✓
- **Total: 85/100** ✅

---

## 🔗 API ENDPOINTS TO IMPLEMENT

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/user/preferences` | Save user preferences |
| POST | `/recommendations/generate` | Generate recommendations |
| GET | `/recommendations` | Get user's recommendations |

---

## 💾 DATABASE CHANGES
- ✅ Recommendation table already exists
- ✅ risk_profile JSON column already in Users table
- No schema migration needed!

---

## 📝 NOTES FOR DEVELOPER

1. **Scoring Algorithm**: Feel free to adjust weights (30/25/20/25) based on real-world testing
2. **Recommendation Count**: Currently returns top 10, can be made configurable
3. **Score Threshold**: Currently 30+ gets recommended, adjust if needed
4. **Reason Text**: Make it more personalized/detailed based on actual match factors
5. **Performance**: Current algorithm is O(n*m), fine for now but consider caching for 1000+ policies

---

**Next Review**: January 22, 2026 (End of Week 4)  
**Estimated Time**: 14-16 hours (8-10 for W3, 6-8 for W4)
