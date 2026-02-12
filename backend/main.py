from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import engine
import models, schemas
from auth import hash_password, verify_password, create_access_token
from deps import get_db, get_current_user
from scoring_refactored import rank_policies
from fraud_rules import check_claim_for_fraud, get_claim_fraud_risk_level
from email_service import EmailService
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

@app.get("/policies")
def list_policies(
    policy_type: str = Query(None, description="Filter by policy type (health, life, auto, home, travel)"),
    provider_id: int = Query(None, description="Filter by provider ID"),
    search: str = Query(None, description="Search in policy title and description"),
    min_premium: Decimal = Query(None, description="Minimum premium"),
    max_premium: Decimal = Query(None, description="Maximum premium"),
    skip: int = Query(0, ge=0, description="Number of policies to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of policies to return (max 100)"),
    db: Session = Depends(get_db)
):
    """
    List all available policies with pagination and filtering.
    
    Features:
    - Filter by policy type, provider, premium range
    - Search by title and description
    - Pagination support (skip/limit)
    - Returns up to 100 policies per request
    
    Example:
    GET /policies?policy_type=health&limit=20&skip=0
    GET /policies?search=HDFC&policy_type=life&max_premium=5000
    """
    query = db.query(models.Policy)
    
    # Apply filters
    if policy_type:
        query = query.filter(models.Policy.policy_type == policy_type)
    
    if provider_id:
        query = query.filter(models.Policy.provider_id == provider_id)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (models.Policy.title.ilike(search_pattern)) |
            (models.Policy.description.ilike(search_pattern))
        )
    
    if min_premium is not None:
        query = query.filter(models.Policy.premium >= min_premium)
    
    if max_premium is not None:
        query = query.filter(models.Policy.premium <= max_premium)
    
    # Get total count for pagination
    total_count = query.count()
    
    # Apply pagination
    policies = query.order_by(models.Policy.title).offset(skip).limit(limit).all()
    
    # Format response with pagination metadata
    return {
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "count": len(policies),
        "policies": [
            {
                **schemas.PolicyOut.from_orm(p).dict(),
                "provider": schemas.ProviderOut.from_orm(p.provider).dict() if p.provider else None
            } 
            for p in policies
        ]
    }

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
def save_preferences(data: dict, token: str = Query(...), db: Session = Depends(get_db)):
    """Save user preferences and auto-generate recommendations"""
    try:
        user = get_current_user(token, db)

        diseases = data.get("diseases", [])
        bmi = float(data.get("bmi") or 0)
        age = int(data.get("age") or 0)
        income = int(data.get("income") or 0)

        # RISK LOGIC (simplified: low/medium/high)
        if len(diseases) >= 4 or bmi >= 30:
            risk = "high"
        elif len(diseases) >= 2 or bmi >= 25:
            risk = "medium"
        else:
            risk = "low"

        user.risk_profile = {
            **data,
            "bmi": bmi,
            "risk_level": risk,
            "risk_profile": risk  # Both names for compatibility
        }

        db.commit()

        # 🎯 AUTO-GENERATE RECOMMENDATIONS with full user data
        try:
            risk_profile = risk  # Use calculated risk_profile
            # Get preferences from the stored risk_profile dict
            preferred_types = user.risk_profile.get('preferred_policy_types', [])
            max_premium = user.risk_profile.get('max_premium')
            
            print(f"\n[DEBUG] Preferences received:")
            print(f"  - preferred_policy_types from data: {data.get('preferred_policy_types', [])}")
            print(f"  - preferred_policy_types from risk_profile: {preferred_types}")
            print(f"  - max_premium: {max_premium}")
            
            preferences = {
                'preferred_policy_types': preferred_types,
                'max_premium': max_premium
            }
            
            # Build full user data for comprehensive scoring
            user_full_data = {
                'age': age,
                'income': income,
                'bmi': bmi,
                'diseases': diseases,
                'has_kids': data.get('has_kids', False),
                'marital_status': data.get('marital_status', ''),
                'height': float(data.get('height') or 0),
                'weight': float(data.get('weight') or 0)
            }
            
            # Get all available policies
            all_policies = db.query(models.Policy).all()
            
            if all_policies:
                # Convert policies to dict for scoring
                policies_dict = []
                for p in all_policies:
                    policies_dict.append({
                        'id': p.id,
                        'title': p.title,
                        'premium': float(p.premium),
                        'coverage': p.coverage or {},
                        'policy_type': p.policy_type,
                        'provider_id': p.provider_id
                    })
                
                # Score and rank policies with full user data
                ranked = rank_policies(policies_dict, preferences, risk_profile, user_full_data, top_n=5)
                
                # Clear existing recommendations
                db.query(models.Recommendation).filter(models.Recommendation.user_id == user.id).delete()
                
                # Save new recommendations
                for policy_dict, score, reason in ranked:
                    rec = models.Recommendation(
                        user_id=user.id,
                        policy_id=policy_dict['id'],
                        score=score,
                        reason=reason
                    )
                    db.add(rec)
                
                db.commit()
        except Exception as e:
            print(f"Recommendation generation failed: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            # Don't fail preferences save if recommendations fail

        return {"message": "Preferences saved", "recommendations_generated": True}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))






# ============ MODULE D: RECOMMENDATIONS (Week 4) ============

@app.post("/recommendations/generate")
def generate_recommendations(
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Generate and save personalized policy recommendations for user.
    
    Two-stage process:
    1. STRICT: Filter by user-selected policy types (policy_type)
    2. SOFT: Score remaining policies and rank (5-10 recommendations)
    
    Returns top recommendations or more browsable options if available.
    """
    try:
        user = get_current_user(token, db)
        
        # Get user preferences and health data
        if not user.risk_profile:
            raise HTTPException(status_code=400, detail="Please set your preferences first")
        
        risk_profile = user.risk_profile.get('risk_profile', 'moderate')
        preferences = user.risk_profile.get('preferences', {})
        
        # Build full user data for comprehensive scoring (restructured)
        user_full_data = {
            'demographics': {
                'age': user.risk_profile.get('age'),
                'income': user.risk_profile.get('income'),
                'bmi': user.risk_profile.get('bmi'),
                'diseases': user.risk_profile.get('diseases', []),
                'has_kids': user.risk_profile.get('has_kids'),
                'marital_status': user.risk_profile.get('marital_status'),
                'height': user.risk_profile.get('height'),
                'weight': user.risk_profile.get('weight')
            },
            'health': {
                'age': user.risk_profile.get('age'),
                'bmi': user.risk_profile.get('bmi'),
                'diseases': user.risk_profile.get('diseases', [])
            },
            'preferences': preferences
        }
        
        # Get all available policies
        all_policies = db.query(models.Policy).all()
        if not all_policies:
            raise HTTPException(status_code=404, detail="No policies available")
        
        # Convert policies to dict for scoring
        policies_dict = []
        for p in all_policies:
            policies_dict.append({
                'id': p.id,
                'title': p.title,
                'premium': float(p.premium),
                'coverage_amount': p.coverage_amount,
                'coverage': p.coverage or {},
                'policy_type': p.policy_type,
                'provider_id': p.provider_id,
                'description': p.description
            })
        
        # RANK POLICIES using refactored scoring engine
        # STAGE 1: Strict policy-type filtering
        # STAGE 2: Soft constraints via scoring and ranking
        ranked = rank_policies(
            policies_dict,
            preferences,
            risk_profile,
            user_full_data,
            top_n=10  # Return up to 10 recommendations instead of 5
        )
        
        # Check if any policies passed filtering
        if not ranked:
            return {
                "message": "No policies match your selected policy types",
                "details": f"No policies of type {preferences.get('preferred_policy_types')} are available. "
                          f"Please adjust your preferences.",
                "recommendations": []
            }
        
        # Clear existing recommendations
        db.query(models.Recommendation).filter(models.Recommendation.user_id == user.id).delete()
        
        # Save all ranked recommendations (no additional validation needed)
        saved_recommendations = []
        for policy_dict, score, reason in ranked:
            rec = models.Recommendation(
                user_id=user.id,
                policy_id=policy_dict['id'],
                score=score,
                reason=reason
            )
            db.add(rec)
            saved_recommendations.append(rec)
        
        db.commit()
        
        # Return with policy details
        result = []
        for rec in saved_recommendations:
            db.refresh(rec)
            policy = db.query(models.Policy).filter(models.Policy.id == rec.policy_id).first()
            if policy:
                result.append({
                'id': rec.id,
                'policy_id': rec.policy_id,
                'score': float(rec.score),
                'reason': rec.reason,
                'created_at': rec.created_at,
                'policy': {
                    'id': policy.id,
                    'title': policy.title,
                    'premium': float(policy.premium),
                    'coverage': policy.coverage,
                    'provider': {
                        'id': policy.provider.id,
                        'name': policy.provider.name
                    }
                }
            })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommendations")
def get_recommendations(
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get user's saved recommendations"""
    user = get_current_user(token, db)
    
    recommendations = db.query(models.Recommendation).filter(
        models.Recommendation.user_id == user.id
    ).order_by(models.Recommendation.score.desc()).all()
    
    if not recommendations:
        return []
    
    result = []
    for rec in recommendations:
        policy = db.query(models.Policy).filter(models.Policy.id == rec.policy_id).first()
        
        # Skip if policy doesn't exist
        if not policy:
            continue
            
        result.append({
            'id': rec.id,
            'user_id': rec.user_id,
            'policy_id': rec.policy_id,
            'score': float(rec.score),
            'reason': rec.reason,
            'created_at': rec.created_at,
            'policy': {
                'id': policy.id,
                'title': policy.title,
                'premium': float(policy.premium),
                'term_months': policy.term_months,
                'deductible': float(policy.deductible),
                'coverage': policy.coverage,
                'policy_type': policy.policy_type,
                'created_at': policy.created_at,
                'provider': {
                    'id': policy.provider.id,
                    'name': policy.provider.name,
                    'country': policy.provider.country,
                    'created_at': policy.provider.created_at
                }
            }
        })
    
    return result

@app.delete("/recommendations/{recommendation_id}")
def delete_recommendation(
    recommendation_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Delete a specific recommendation"""
    user = get_current_user(token, db)
    
    rec = db.query(models.Recommendation).filter(
        models.Recommendation.id == recommendation_id,
        models.Recommendation.user_id == user.id
    ).first()
    
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    db.delete(rec)
    db.commit()
    
    return {"message": "Recommendation deleted"}

# ============ MODULE E: CLAIMS (Week 5-6) ============

@app.post("/claims")
def create_claim(
    claim_data: schemas.ClaimCreate,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Create a new insurance claim in draft status.
    User can upload documents and submit later.
    
    Request body:
    {
        "user_policy_id": 1,
        "claim_type": "death|illness|accident|theft",
        "incident_date": "2026-01-15",
        "amount_claimed": 500000,
        "documents": [optional - loaded separately]
    }
    """
    try:
        user = get_current_user(token, db)
        
        # Verify user owns the policy
        user_policy = db.query(models.UserPolicy).filter(
            models.UserPolicy.id == claim_data.user_policy_id,
            models.UserPolicy.user_id == user.id
        ).first()
        
        if not user_policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Generate unique claim number
        claim_number = f"CLM-{uuid.uuid4().hex[:8].upper()}"
        
        claim = models.Claim(
            user_policy_id=claim_data.user_policy_id,
            claim_number=claim_number,
            claim_type=claim_data.claim_type,
            incident_date=claim_data.incident_date,
            amount_claimed=claim_data.amount_claimed,
            status=models.ClaimStatusEnum.draft,
            description=None
        )
        
        db.add(claim)
        db.commit()
        db.refresh(claim)
        
        return {
            "id": claim.id,
            "claim_number": claim.claim_number,
            "status": "draft",
            "created_at": str(claim.created_at),
            "message": "Claim created. Upload documents and submit when ready."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/claims")
def get_user_claims(
    token: str = Query(...),
    status: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get all claims for the logged-in user.
    Optional status filter: draft|submitted|under_review|approved|rejected|paid
    """
    try:
        user = get_current_user(token, db)
        
        query = db.query(models.Claim).join(
            models.UserPolicy,
            models.Claim.user_policy_id == models.UserPolicy.id
        ).filter(models.UserPolicy.user_id == user.id)
        
        if status:
            query = query.filter(models.Claim.status == status)
        
        claims = query.order_by(models.Claim.created_at.desc()).all()
        
        result = []
        for claim in claims:
            user_policy = claim.user_policy
            policy = user_policy.policy
            provider = policy.provider
            
            result.append({
                "id": claim.id,
                "claim_number": claim.claim_number,
                "claim_type": claim.claim_type,
                "amount_claimed": float(claim.amount_claimed),
                "status": claim.status,
                "incident_date": str(claim.incident_date),
                "created_at": str(claim.created_at),
                "policy": {
                    "id": policy.id,
                    "title": policy.title,
                    "premium": float(policy.premium),
                    "provider_name": provider.name
                },
                "documents_count": len(claim.documents)
            })
        
        return {
            "count": len(result),
            "claims": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/claims/{claim_id}")
def get_claim_detail(
    claim_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Get detailed claim information including all documents and timeline.
    """
    try:
        user = get_current_user(token, db)
        
        claim = db.query(models.Claim).join(
            models.UserPolicy,
            models.Claim.user_policy_id == models.UserPolicy.id
        ).filter(
            models.Claim.id == claim_id,
            models.UserPolicy.user_id == user.id
        ).first()
        
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        user_policy = claim.user_policy
        policy = user_policy.policy
        provider = policy.provider
        
        return {
            "id": claim.id,
            "claim_number": claim.claim_number,
            "claim_type": claim.claim_type,
            "amount_claimed": float(claim.amount_claimed),
            "status": claim.status,
            "incident_date": str(claim.incident_date),
            "description": claim.description,
            "created_at": str(claim.created_at),
            "policy": {
                "id": policy.id,
                "title": policy.title,
                "premium": float(policy.premium),
                "policy_type": policy.policy_type,
                "policy_number": user_policy.policy_number,
                "provider": provider.name
            },
            "documents": [
                {
                    "id": doc.id,
                    "doc_type": doc.doc_type,
                    "file_url": doc.file_url,
                    "uploaded_at": str(doc.uploaded_at)
                }
                for doc in claim.documents
            ],
            "documents_count": len(claim.documents)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/claims/{claim_id}/documents")
def upload_claim_document(
    claim_id: int,
    file: UploadFile = File(...),
    doc_type: str = Query(...),
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document to a claim.
    Documents can be uploaded in draft stage.
    Accepts file uploads via FormData.
    """
    try:
        user = get_current_user(token, db)
        
        # Verify claim belongs to user
        claim = db.query(models.Claim).join(
            models.UserPolicy,
            models.Claim.user_policy_id == models.UserPolicy.id
        ).filter(
            models.Claim.id == claim_id,
            models.UserPolicy.user_id == user.id
        ).first()
        
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        # Create file reference (in production, save to cloud storage like S3)
        # For now, just store the metadata with a unique identifier
        file_url = f"documents/{claim_id}/{doc_type}_{uuid.uuid4().hex[:8]}_{file.filename}"
        
        # Create document record
        doc = models.ClaimDocument(
            claim_id=claim_id,
            file_url=file_url,
            doc_type=doc_type
        )
        
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        return {
            "id": doc.id,
            "doc_type": doc.doc_type,
            "file_url": doc.file_url,
            "uploaded_at": str(doc.uploaded_at),
            "message": "Document uploaded successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/claims/{claim_id}/submit")
def submit_claim(
    claim_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Submit a claim for review.
    Changes status from draft to submitted.
    Runs fraud detection rules automatically.
    """
    try:
        user = get_current_user(token, db)
        
        claim = db.query(models.Claim).join(
            models.UserPolicy,
            models.Claim.user_policy_id == models.UserPolicy.id
        ).filter(
            models.Claim.id == claim_id,
            models.UserPolicy.user_id == user.id
        ).first()
        
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        if claim.status != models.ClaimStatusEnum.draft:
            raise HTTPException(
                status_code=400, 
                detail=f"Only draft claims can be submitted. Current status: {claim.status}"
            )
        
        if len(claim.documents) == 0:
            raise HTTPException(
                status_code=400, 
                detail="At least one document is required before submitting"
            )
        
        # ===== WEEK 7: RUN FRAUD DETECTION =====
        fraud_flags = check_claim_for_fraud(db, claim)
        fraud_risk = get_claim_fraud_risk_level(fraud_flags)
        
        # Set initial status based on fraud risk
        if fraud_risk == "CRITICAL":
            claim.status = models.ClaimStatusEnum.under_review
        else:
            claim.status = models.ClaimStatusEnum.submitted
        
        db.commit()
        
        response = {
            "message": "Claim submitted successfully",
            "claim_number": claim.claim_number,
            "status": claim.status,
            "submitted_at": str(datetime.utcnow()),
            "next_steps": "Our team will review your claim within 5-7 business days",
            "fraud_check": {
                "risk_level": fraud_risk,
                "flags_count": len(fraud_flags),
                "flags": [
                    {
                        "code": f.rule_code,
                        "severity": f.severity,
                        "details": f.details
                    }
                    for f in fraud_flags
                ]
            }
        }
        
        # Send confirmation email to user
        policy = claim.user_policy.policy
        EmailService.send_claim_submitted_notification(
            user_email=user.email,
            user_name=user.name,
            claim_number=claim.claim_number,
            policy_name=policy.title
        )
        
        # If critical risk, send fraud alert email
        if fraud_risk == "CRITICAL":
            response["warning"] = "Your claim has been flagged for detailed review due to potential fraud indicators."
            EmailService.send_fraud_alert_notification(
                user_email=user.email,
                user_name=user.name,
                claim_number=claim.claim_number,
                risk_level=fraud_risk
            )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ============ WEEK 7: FRAUD DETECTION & RULES ============

@app.get("/claims/{claim_id}/fraud-flags")
def get_claim_fraud_flags(
    claim_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Get fraud flags for a specific claim.
    User can only view their own claims' fraud flags.
    """
    try:
        user = get_current_user(token, db)
        
        claim = db.query(models.Claim).join(
            models.UserPolicy,
            models.Claim.user_policy_id == models.UserPolicy.id
        ).filter(
            models.Claim.id == claim_id,
            models.UserPolicy.user_id == user.id
        ).first()
        
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        fraud_flags = db.query(models.FraudFlag).filter(
            models.FraudFlag.claim_id == claim_id
        ).all()
        
        return {
            "claim_number": claim.claim_number,
            "flags_count": len(fraud_flags),
            "risk_level": get_claim_fraud_risk_level(fraud_flags),
            "flags": [
                {
                    "id": f.id,
                    "code": f.rule_code,
                    "name": f.rule_code.replace("_", " ").title(),
                    "severity": f.severity,
                    "details": f.details,
                    "created_at": str(f.created_at)
                }
                for f in fraud_flags
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/claims/{claim_id}/recheck-fraud")
def recheck_claim_fraud(
    claim_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Recheck a claim for fraud patterns.
    Creates new fraud flags and removes old ones.
    Admin endpoint (currently open for testing).
    """
    try:
        user = get_current_user(token, db)
        
        claim = db.query(models.Claim).filter(
            models.Claim.id == claim_id
        ).first()
        
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        # Delete old fraud flags
        db.query(models.FraudFlag).filter(
            models.FraudFlag.claim_id == claim_id
        ).delete()
        
        # Run new fraud check
        fraud_flags = check_claim_for_fraud(db, claim)
        fraud_risk = get_claim_fraud_risk_level(fraud_flags)
        
        return {
            "claim_number": claim.claim_number,
            "risk_level": fraud_risk,
            "flags_count": len(fraud_flags),
            "flags": [
                {
                    "code": f.rule_code,
                    "severity": f.severity,
                    "details": f.details
                }
                for f in fraud_flags
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/fraud/summary")
def get_fraud_summary(
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Get fraud summary statistics (Admin endpoint).
    Shows overall fraud flags and risk distribution.
    """
    try:
        user = get_current_user(token, db)
        # In production, check if user is admin
        
        total_flags = db.query(models.FraudFlag).count()
        
        high_severity = db.query(models.FraudFlag).filter(
            models.FraudFlag.severity == models.FraudSeverityEnum.high
        ).count()
        
        medium_severity = db.query(models.FraudFlag).filter(
            models.FraudFlag.severity == models.FraudSeverityEnum.medium
        ).count()
        
        low_severity = db.query(models.FraudFlag).filter(
            models.FraudFlag.severity == models.FraudSeverityEnum.low
        ).count()
        
        # Count by rule
        rule_counts = db.query(
            models.FraudFlag.rule_code,
            func.count(models.FraudFlag.id).label("count")
        ).group_by(models.FraudFlag.rule_code).all()
        
        claims_with_flags = db.query(models.Claim).join(
            models.FraudFlag
        ).distinct().count()
        
        return {
            "total_flags": total_flags,
            "severity_distribution": {
                "high": high_severity,
                "medium": medium_severity,
                "low": low_severity
            },
            "claims_flagged": claims_with_flags,
            "top_fraud_rules": [
                {"rule": code, "count": count}
                for code, count in sorted(rule_counts, key=lambda x: x[1], reverse=True)[:5]
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/fraud/high-risk-claims")
def get_high_risk_claims(
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Get list of high-risk claims requiring review (Admin endpoint).
    """
    try:
        user = get_current_user(token, db)
        # In production, check if user is admin
        
        # Get claims with high severity fraud flags
        high_risk_claims = db.query(models.Claim).join(
            models.FraudFlag
        ).filter(
            models.FraudFlag.severity == models.FraudSeverityEnum.high
        ).distinct().all()
        
        claims_data = []
        for claim in high_risk_claims:
            flags = db.query(models.FraudFlag).filter(
                models.FraudFlag.claim_id == claim.id
            ).all()
            
            claims_data.append({
                "id": claim.id,
                "claim_number": claim.claim_number,
                "claim_type": claim.claim_type,
                "amount_claimed": float(claim.amount_claimed),
                "status": claim.status,
                "created_at": str(claim.created_at),
                "user_name": claim.user_policy.user.name,
                "policy_type": claim.user_policy.policy.policy_type,
                "risk_level": get_claim_fraud_risk_level(flags),
                "flags_count": len(flags),
                "high_severity_flags": sum(1 for f in flags if f.severity == models.FraudSeverityEnum.high)
            })
        
        return sorted(claims_data, key=lambda x: x["high_severity_flags"], reverse=True)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/claims/{claim_id}")
def delete_claim(
    claim_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Delete a claim. Only draft claims can be deleted.
    """
    try:
        user = get_current_user(token, db)
        
        claim = db.query(models.Claim).join(
            models.UserPolicy,
            models.Claim.user_policy_id == models.UserPolicy.id
        ).filter(
            models.Claim.id == claim_id,
            models.UserPolicy.user_id == user.id
        ).first()
        
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        if claim.status != models.ClaimStatusEnum.draft:
            raise HTTPException(
                status_code=400, 
                detail="Only draft claims can be deleted"
            )
        
        # Delete associated documents first
        db.query(models.ClaimDocument).filter(
            models.ClaimDocument.claim_id == claim_id
        ).delete()
        
        # Delete the claim
        db.delete(claim)
        db.commit()
        
        return {
            "message": "Claim deleted successfully",
            "claim_number": claim.claim_number
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/claims/{claim_id}/documents/{doc_id}")
def delete_document(
    claim_id: int,
    doc_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Delete a document from a claim. Only possible if claim is in draft status.
    """
    try:
        user = get_current_user(token, db)
        
        claim = db.query(models.Claim).join(
            models.UserPolicy,
            models.Claim.user_policy_id == models.UserPolicy.id
        ).filter(
            models.Claim.id == claim_id,
            models.UserPolicy.user_id == user.id
        ).first()
        
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        if claim.status != models.ClaimStatusEnum.draft:
            raise HTTPException(
                status_code=400, 
                detail="Can only delete documents from draft claims"
            )
        
        doc = db.query(models.ClaimDocument).filter(
            models.ClaimDocument.id == doc_id,
            models.ClaimDocument.claim_id == claim_id
        ).first()
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        db.delete(doc)
        db.commit()
        
        return {
            "message": "Document deleted successfully",
            "doc_id": doc_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ============ USER APPLICATIONS (NEW POLICY PURCHASES) ============

@app.post("/user-applications")
def apply_for_insurance(
    policy_id: int = Query(...),
    full_name: str = Query(...),
    email: str = Query(...),
    phone_number: str = Query(...),
    date_of_birth: str = Query(...),
    gender: str = Query(...),
    address: str = Query(...),
    nominee_name: str = Query(...),
    nominee_relation: str = Query(...),
    nominee_phone: str = Query(...),
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Submit an application to purchase a new insurance policy
    """
    try:
        # Verify user is authenticated
        user = get_current_user(token, db)
        
        # Verify policy exists
        policy = db.query(models.Policy).filter(models.Policy.id == policy_id).first()
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Check if user already has this policy
        existing = db.query(models.UserPolicy).filter(
            models.UserPolicy.user_id == user.id,
            models.UserPolicy.policy_id == policy_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="You already have this policy")
        
        # Generate unique policy number
        policy_number = f"POL-{uuid.uuid4().hex[:8].upper()}"
        
        # Create new user policy (application approved automatically for demo)
        from datetime import timedelta
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=365 * (policy.term_months // 12))
        
        new_user_policy = models.UserPolicy(
            user_id=user.id,
            policy_id=policy_id,
            policy_number=policy_number,
            start_date=start_date,
            end_date=end_date,
            premium=policy.premium,
            status=models.UserPolicyStatusEnum.active,
            auto_renew=False
        )
        
        db.add(new_user_policy)
        db.commit()
        db.refresh(new_user_policy)
        
        # Send confirmation email to user
        EmailService.send_application_confirmation(
            user_email=user.email,
            user_name=user.name,
            policy_name=policy.title,
            policy_number=policy_number,
            premium=str(policy.premium)
        )
        
        return {
            "message": "Application submitted successfully!",
            "policy_number": policy_number,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "status": "active",
            "premium": str(policy.premium),
            "email_sent": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing application: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)






