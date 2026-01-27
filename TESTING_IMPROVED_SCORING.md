# 🧪 Testing the Improved Recommendation System

## Quick Start Testing

### Step 1: Register a User
```
URL: http://localhost:5174/register
1. Enter name, email, password
2. Create account
```

### Step 2: Set Preferences with Different Profiles
Test multiple user profiles to see different recommendations:

#### Profile A: Young & Healthy
```
Age: 25
Income: 600,000
Height: 175 cm
Weight: 70 kg
BMI: 22.9 (Normal)
Diseases: None
Risk Level: Low (Conservative)
Max Premium: 5,000
Preferred Types: health, travel
```
**Expected**: High scores on Health (87-95%) & Travel (75-85%)

#### Profile B: Middle-Aged with Conditions
```
Age: 45
Income: 1,000,000
Height: 172 cm
Weight: 85 kg
BMI: 28.7 (Overweight)
Diseases: Hypertension, Diabetes
Risk Level: High (Aggressive)
Max Premium: 8,000
Preferred Types: health, life
```
**Expected**: Very high scores on Health (94-99%) & Life (82-90%)

#### Profile C: Budget Conscious
```
Age: 35
Income: 300,000
Height: 170 cm
Weight: 65 kg
BMI: 22.5 (Normal)
Diseases: None
Risk Level: Low
Max Premium: 2,000
Preferred Types: health
```
**Expected**: High scores on budget-friendly policies only

---

## 🔍 Verification Tests

### Test 1: Score Differentiation ✅
**Goal**: Verify each policy gets a DIFFERENT score

**Steps**:
1. Register as "Profile B" (middle-aged with diseases)
2. Go to Recommendations page
3. Check 5 recommended policies

**Expected Results**:
```
Policy 1: ⭐⭐⭐⭐⭐ 96% (Health + Hospitalization)
Policy 2: ⭐⭐⭐⭐  84% (Life Insurance)
Policy 3: ⭐⭐⭐⭐  78% (Health Basic)
Policy 4: ⭐⭐⭐    65% (Travel)
Policy 5: ⭐⭐     42% (Auto)
```

**Verify**: Each score is different, NOT all 49%! ✅

---

### Test 2: Health Condition Boost ✅
**Goal**: Verify health policies are prioritized for users with diseases

**Steps**:
1. Create 2 users:
   - User A: No diseases (healthy)
   - User B: Hypertension + Diabetes

**Expected Results**:

User A (Healthy):
```
Health Insurance: 78% (decent)
Life Insurance: 72% (similar)
Travel Insurance: 80% (higher!)
```

User B (With Diseases):
```
Health Insurance: 96% (BOOSTED!)
Life Insurance: 88% (boosted)
Travel Insurance: 42% (lowered)
```

**Verify**: Health policies much higher for User B! ✅

---

### Test 3: Budget Awareness ✅
**Goal**: Verify premium affordability is calculated

**Steps**:
1. Create 2 users with different budgets:
   - User A: Max Premium ₹2,000/month
   - User B: Max Premium ₹8,000/month

2. Check same policy recommendations

**Expected Results**:

Policy: ₹3,000/month

User A (Budget ₹2,000):
```
Score: 35% (OVER BUDGET → LOW SCORE)
Reason: "Premium exceeds budget"
```

User B (Budget ₹8,000):
```
Score: 88% (WITHIN BUDGET → HIGH SCORE)
Reason: "Well within budget ($3000)"
```

**Verify**: Same policy scores differently based on budget! ✅

---

### Test 4: Risk Profile Impact ✅
**Goal**: Verify risk level affects recommendations

**Steps**:
1. Create 2 users (same age/income):
   - User A: Conservative risk
   - User B: Aggressive risk

**Expected Results**:

User A (Conservative):
```
Health: 89% (preferred)
Life: 85% (preferred)
Travel: 62% (less preferred)
```

User B (Aggressive):
```
Health: 95% (highly preferred)
Life: 90% (comprehensive)
Travel: 85% (broader options)
```

**Verify**: Conservative/Aggressive impact visible! ✅

---

### Test 5: Income-Based Calculations ✅
**Goal**: Verify premium-to-income ratio

**Steps**:
1. Create 2 users:
   - User A: Income ₹300,000 (low)
   - User B: Income ₹1,500,000 (high)

2. Check same ₹5,000/month policy

**Expected Results**:

User A (₹300,000/year):
```
₹5,000/month = 20% of annual income
Score: 45% (HIGH for them)
Reason: "Significant expense (20% of income)"
```

User B (₹1,500,000/year):
```
₹5,000/month = 4% of annual income
Score: 92% (EXCELLENT for them)
Reason: "Affordable (4% of annual income)"
```

**Verify**: Income ratio considered! ✅

---

### Test 6: Policy Type Preference ✅
**Goal**: Verify preferred policy types are boosted

**Steps**:
1. Create users with different preferred types:
   - User A: Prefers health, life
   - User B: Prefers travel, auto

2. Check recommendations

**Expected Results**:

For Travel Insurance:
- User A score: 62% (not preferred)
- User B score: 85% (preferred!)

**Verify**: Preferred types score higher! ✅

---

## 📊 Detailed Scoring Verification

### Check Backend Logs
Look at terminal running backend to see detailed scoring logs:

```
=== Policy Rankings for risk_profile=high ===
1. Premium Health Coverage: 96.25/100 - Excellent coverage match • Within budget • Ideal for conditions
2. Life Insurance Plus: 84.50/100 - Good coverage • Appropriate for age • Matches high profile
3. Health Basics: 78.75/100 - Good coverage • Within budget • Suitable profile
4. Travel Insurance: 42.10/100 - Partial coverage • Over budget • Not suited
5. Auto Insurance: 35.80/100 - Limited coverage • Budget mismatch • Low relevance
```

Each policy gets unique score breakdown! ✅

---

## 🔧 Manual API Testing

### Test with cURL

#### 1. Set Preferences (This triggers auto-recommendation generation)
```bash
curl -X POST "http://localhost:8000/user/preferences?token=YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 45,
    "income": 1000000,
    "height": 172,
    "weight": 85,
    "bmi": 28.7,
    "diseases": ["Hypertension", "Diabetes"],
    "has_kids": true,
    "marital_status": "married",
    "max_premium": 8000,
    "preferred_policy_types": ["health", "life"],
    "preferences": {
      "required_coverages": ["hospitalization", "preventive"]
    },
    "risk_profile": "high"
  }'
```

#### 2. Get Recommendations
```bash
curl -X GET "http://localhost:8000/recommendations?token=YOUR_TOKEN" \
  -H "Accept: application/json"
```

**Expected Response**:
```json
[
  {
    "id": 1,
    "policy_id": 5,
    "score": 96.25,
    "reason": "Excellent coverage match • Within budget • Ideal for your health conditions • Matches high profile",
    "policy": {
      "id": 5,
      "title": "Premium Health Coverage",
      "premium": 7500,
      "policy_type": "health"
    }
  },
  {
    "id": 2,
    "policy_id": 8,
    "score": 84.50,
    "reason": "Good coverage • Within budget • Matches high profile",
    "policy": {
      "id": 8,
      "title": "Life Insurance Plus",
      "premium": 6000,
      "policy_type": "life"
    }
  }
]
```

**Verify**: Scores are differentiated (96.25, 84.50, etc.), NOT all 49%! ✅

---

## 🎯 Success Criteria Checklist

### ✅ Scoring System Working If:
- [ ] Different users get different score distributions
- [ ] Same policy scores differently for different users
- [ ] Health policies score higher for users with diseases (90%+ boost)
- [ ] Budget-aware scoring works (under-budget: 80%+, over-budget: <40%)
- [ ] Age affects recommendations (young: travel boost, old: health boost)
- [ ] Risk profile impact visible (conservative vs aggressive)
- [ ] Policy type preferences are respected
- [ ] Scores span 15-100 range (not 40-60)
- [ ] Clear reasons shown for each recommendation
- [ ] Console logs show differentiated scores

### ❌ Issues to Check If Scoring Still Wrong:
- [ ] Backend restarted after code changes?
- [ ] Database cleared (old recommendations)?
- [ ] Preferences saved (triggers auto-generation)?
- [ ] Token valid (not expired)?
- [ ] All fields filled in preferences?

---

## 🚨 Debugging

### If Scores Still Same (49%):
1. Check backend logs: Look for score printout
2. Verify scoring.py updated: Check functions exist
3. Clear database recommendations: Start fresh
4. Restart backend server: Apply changes
5. Set preferences again: Trigger generation

### If Recommendations Missing:
1. Verify user created and logged in
2. Check preferences saved: POST /user/preferences
3. Look at backend logs for errors
4. Verify database has policies (seed_data)

### If Scores Incorrect:
1. Check user_full_data passed to rank_policies()
2. Verify all health data captured
3. Check income/budget calculations
4. Look at score component breakdown in logs

---

## 📈 Expected Improvements Over Old System

| Aspect | Old | New | Test |
|--------|-----|-----|------|
| Score Range | 45-55% | 15-100% | Try multiple users |
| Health Boost | 0% | +10-15% | Create user with diseases |
| Budget Fit | Basic | Income % | High vs low income |
| Differentiation | None | Yes | Check 5 policies |
| Risk Impact | Low | High | Compare conservative/aggressive |
| Policy Type Fit | Basic | Dedicated | Check preferred types |

---

## 🎉 When It Works

You'll see something like:
```
User A (Young, Healthy):
1. Health: 82%
2. Travel: 88%
3. Life: 71%
4. Home: 65%
5. Auto: 74%

User B (Older, Chronic Disease):
1. Health: 98%
2. Life: 89%
3. Travel: 38%
4. Home: 62%
5. Auto: 45%
```

**COMPLETELY DIFFERENT!** ✅ System working perfectly!
