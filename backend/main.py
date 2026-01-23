from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import engine
import models, schemas
from auth import hash_password, verify_password, create_access_token
from deps import get_db, get_current_user
import uuid
from datetime import datetime
from decimal import Decimal

models.Base.metadata.create_all(bind=engine)

# Create app
app = FastAPI(title="Insurance Comparison & Claims Assistant")

# CORS Configuration - MUST be before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ HEALTH CHECK ============

@app.get("/health")
def health():
    return {"status": "ok"}

# ============ MODULE A: AUTH & PROFILE ============

@app.post("/auth/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Validate required fields
        if not user.name or not user.email or not user.password or not user.dob:
            raise HTTPException(status_code=400, detail="All fields are required")
        
        # Check if email already exists
        existing_user = db.query(models.User).filter(models.User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")

        # Create new user
        new_user = models.User(
            name=user.name,
            email=user.email,
            password=hash_password(user.password),
            dob=user.dob
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate token
        token = create_access_token({"user_id": new_user.id})
        return {"access_token": token, "user_id": new_user.id, "user": schemas.UserOut.from_orm(new_user)}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/login")
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        user = db.query(models.User).filter(models.User.email == data.email).first()
        if not user or not verify_password(data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token({"user_id": user.id})
        return {"access_token": token, "user_id": user.id, "user": schemas.UserOut.from_orm(user)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/me", response_model=schemas.UserOut)
def get_profile(token: str = Query(...), db: Session = Depends(get_db)):
    """Get current user profile"""
    user = get_current_user(token, db)
    return schemas.UserOut.from_orm(user)

@app.put("/user/profile", response_model=schemas.UserOut)
def update_profile(data: schemas.UserUpdate, token: str = Query(...), db: Session = Depends(get_db)):
    """Update user profile"""
    user = get_current_user(token, db)
    
    if data.name:
        user.name = data.name
    if data.risk_profile:
        user.risk_profile = data.risk_profile
    
    db.commit()
    db.refresh(user)
    return schemas.UserOut.from_orm(user)

# ============ MODULE B: POLICY CATALOG ============

@app.get("/providers", response_model=list[schemas.ProviderOut])
def list_providers(db: Session = Depends(get_db)):
    """List all insurance providers"""
    providers = db.query(models.Provider).all()
    return [schemas.ProviderOut.from_orm(p) for p in providers]

@app.post("/providers", response_model=schemas.ProviderOut)
def create_provider(data: schemas.ProviderCreate, db: Session = Depends(get_db)):
    """Create new provider (admin only)"""
    provider = models.Provider(name=data.name, country=data.country)
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return schemas.ProviderOut.from_orm(provider)

@app.get("/policies", response_model=list[schemas.PolicyWithProvider])
def list_policies(
    policy_type: str = Query(None),
    provider_id: int = Query(None),
    min_premium: Decimal = Query(None),
    max_premium: Decimal = Query(None),
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db)
):
    """List all policies with optional filters"""
    query = db.query(models.Policy)
    
    if policy_type:
        query = query.filter(models.Policy.policy_type == policy_type)
    if provider_id:
        query = query.filter(models.Policy.provider_id == provider_id)
    if min_premium:
        query = query.filter(models.Policy.premium >= min_premium)
    if max_premium:
        query = query.filter(models.Policy.premium <= max_premium)
    
    policies = query.offset(skip).limit(limit).all()
    return [schemas.PolicyWithProvider(
        **schemas.PolicyOut.from_orm(p).dict(),
        provider=schemas.ProviderOut.from_orm(p.provider)
    ) for p in policies]

@app.get("/policies/compare")
def compare_policies(
    policy_ids: str = Query(...),
    db: Session = Depends(get_db)
):
    """Compare multiple policies"""
    try:
        ids = [int(id) for id in policy_ids.split(",")]
        policies = db.query(models.Policy).filter(models.Policy.id.in_(ids)).all()
        
        if not policies:
            raise HTTPException(status_code=404, detail="No policies found")
        
        result = []
        for p in policies:
            policy_dict = schemas.PolicyOut.from_orm(p).dict()
            policy_dict["provider"] = schemas.ProviderOut.from_orm(p.provider).dict()
            result.append(policy_dict)
        
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid policy IDs format")

@app.get("/policies/{policy_id}", response_model=schemas.PolicyWithProvider)
def get_policy(policy_id: int, db: Session = Depends(get_db)):
    """Get policy details"""
    policy = db.query(models.Policy).filter(models.Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return schemas.PolicyWithProvider(
        **schemas.PolicyOut.from_orm(policy).dict(),
        provider=schemas.ProviderOut.from_orm(policy.provider)
    )

@app.post("/policies", response_model=schemas.PolicyOut)
def create_policy(data: schemas.PolicyCreate, db: Session = Depends(get_db)):
    """Create new policy (admin only)"""
    # Verify provider exists
    provider = db.query(models.Provider).filter(models.Provider.id == data.provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    policy = models.Policy(
        provider_id=data.provider_id,
        policy_type=data.policy_type,
        title=data.title,
        coverage=data.coverage,
        premium=data.premium,
        term_months=data.term_months,
        deductible=data.deductible,
        tnc_url=data.tnc_url
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return schemas.PolicyOut.from_orm(policy)

# ============ USER POLICIES (Purchased Policies) ============

@app.post("/user-policies", response_model=schemas.UserPolicyOut)
def purchase_policy(
    data: schemas.UserPolicyCreate,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Purchase/assign a policy to user"""
    user = get_current_user(token, db)
    
    # Verify policy exists
    policy = db.query(models.Policy).filter(models.Policy.id == data.policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    # Generate unique policy number
    policy_number = f"POL-{user.id}-{uuid.uuid4().hex[:8].upper()}"
    
    user_policy = models.UserPolicy(
        user_id=user.id,
        policy_id=data.policy_id,
        policy_number=policy_number,
        start_date=data.start_date,
        end_date=data.end_date,
        premium=data.premium,
        auto_renew=data.auto_renew
    )
    db.add(user_policy)
    db.commit()
    db.refresh(user_policy)
    return schemas.UserPolicyOut.from_orm(user_policy)

@app.get("/user-policies", response_model=list[schemas.UserPolicyWithPolicy])
def get_user_policies(
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get all policies owned by user"""
    user = get_current_user(token, db)
    user_policies = db.query(models.UserPolicy).filter(models.UserPolicy.user_id == user.id).all()
    
    return [schemas.UserPolicyWithPolicy(
        **schemas.UserPolicyOut.from_orm(up).dict(),
        policy=schemas.PolicyWithProvider(
            **schemas.PolicyOut.from_orm(up.policy).dict(),
            provider=schemas.ProviderOut.from_orm(up.policy.provider)
        )
    ) for up in user_policies]

@app.get("/user-policies/{user_policy_id}", response_model=schemas.UserPolicyWithPolicy)
def get_user_policy(
    user_policy_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get specific user policy"""
    user = get_current_user(token, db)
    user_policy = db.query(models.UserPolicy).filter(
        models.UserPolicy.id == user_policy_id,
        models.UserPolicy.user_id == user.id
    ).first()
    
    if not user_policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    return schemas.UserPolicyWithPolicy(
        **schemas.UserPolicyOut.from_orm(user_policy).dict(),
        policy=schemas.PolicyWithProvider(
            **schemas.PolicyOut.from_orm(user_policy.policy).dict(),
            provider=schemas.ProviderOut.from_orm(user_policy.policy.provider)
        )
    )

@app.post("/user/preferences")
def save_preferences(
    data: schemas.UserPreferences,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    user = get_current_user(token, db)

    diseases = data.diseases
    bmi = data.bmi

    # -------------------
    # RISK CALCULATION
    # -------------------
    if len(diseases) >= 4 or bmi >= 30:
        risk = "high"
    elif len(diseases) >= 2 or bmi >= 25:
        risk = "medium"
    else:
        risk = "low"

    user.risk_profile = {
        "age": data.age,
        "income": data.income,
        "marital_status": data.marital_status,
        "has_kids": data.has_kids,
        "bmi": data.bmi,
        "diseases": data.diseases,
        "preferred_policy_types": data.preferred_policy_types,
        "max_premium": data.max_premium,
        "risk_level": risk
    }

    db.commit()
    return {"message": "Preferences saved successfully"}



@app.get("/recommendations")
def get_recommendations(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    prefs = user.risk_profile

    age = int(prefs.get("age", 0))
    diseases = prefs.get("diseases", [])
    bmi = float(prefs.get("bmi", 0))
    income = int(prefs.get("income", 0))

    # -------------------
    # RISK LEVEL LOGIC
    # -------------------
    risk_level = "low"

    if len(diseases) >= 5 or bmi >= 30:
        risk_level = "high"
    elif len(diseases) >= 2 or bmi >= 25:
        risk_level = "medium"

    # -------------------
    # POLICY FILTER BY AGE
    # -------------------
    allowed_types = []

    if age < 15:
        allowed_types = ["health"]
    elif age <= 45:
        allowed_types = ["health", "auto", "travel", "home"]
    else:
        allowed_types = ["health", "life"]

    policies = db.query(models.Policy).filter(
    models.Policy.policy_type.in_(allowed_types)
    )

    if prefs.get("preferred_policy_types"):
        policies = policies.filter(
            models.Policy.policy_type.in_(prefs["preferred_policy_types"])
        )

    if prefs.get("max_premium"):
        policies = policies.filter(
            models.Policy.premium <= prefs["max_premium"]
      )

    policies = policies.all()


    recommendations = []

    for p in policies:
        score = 0

        if p.policy_type == "health":
            score += 3
        if income > 500000:
            score += 2
        if risk_level == "high" and p.policy_type != "health":
            continue  # ❌ reject risky policies

        recommendations.append({
            "title": p.title,
            "policy_type": p.policy_type,
            "premium": p.premium,
            "reason": f"Recommended for {risk_level} risk profile & age {age}"
        })

    return recommendations



