from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import engine
import models, schemas
from auth import hash_password, verify_password, create_access_token
from deps import get_db, get_current_user
from scoring import rank_policies
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
    limit: int = Query(100),
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
    """Generate and save personalized policy recommendations for user"""
    try:
        user = get_current_user(token, db)
        
        # Get user preferences and health data
        if not user.risk_profile:
            raise HTTPException(status_code=400, detail="Please set your preferences first")
        
        risk_profile = user.risk_profile.get('risk_profile', 'moderate')
        preferences = user.risk_profile.get('preferences', {})
        
        # Build full user data for comprehensive scoring
        user_full_data = {
            'age': user.risk_profile.get('age'),
            'income': user.risk_profile.get('income'),
            'bmi': user.risk_profile.get('bmi'),
            'diseases': user.risk_profile.get('diseases', []),
            'has_kids': user.risk_profile.get('has_kids'),
            'marital_status': user.risk_profile.get('marital_status'),
            'height': user.risk_profile.get('height'),
            'weight': user.risk_profile.get('weight')
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
                'coverage': p.coverage or {},
                'policy_type': p.policy_type,
                'provider_id': p.provider_id
            })
        
        # Score and rank policies with full user data
        # Score and rank policies with STRICT FILTERING applied
        # (rank_policies applies all filters BEFORE scoring)
        ranked = rank_policies(policies_dict, preferences, risk_profile, user_full_data, top_n=5)
        
        # Check if any policies passed filtering
        if not ranked:
            return {
                "message": "No policies match your filters",
                "details": f"Your preferences (type: {preferences.get('preferred_policy_types')}, max: ₹{preferences.get('max_premium')}) "
                          f"and risk profile ({risk_profile}) didn't match any available policies.",
                "recommendations": []
            }
        
        # Clear existing recommendations
        db.query(models.Recommendation).filter(models.Recommendation.user_id == user.id).delete()
        
        # Save new recommendations (only those that passed ALL filters)
        saved_recommendations = []
        for policy_dict, score, reason in ranked:
            # Additional validation: Ensure policy matches user filters
            policy_type = policy_dict.get('policy_type')
            premium = Decimal(str(policy_dict.get('premium', 0)))
            
            # Verify policy type is allowed
            if preferences.get('preferred_policy_types') and policy_type not in preferences.get('preferred_policy_types'):
                print(f"⚠️ Skipping {policy_dict['title']} - not in preferred types")
                continue
            
            # Verify premium is within budget
            max_prem = preferences.get('max_premium')
            if max_prem and premium > Decimal(str(max_prem)):
                print(f"⚠️ Skipping {policy_dict['title']} - exceeds budget")
                continue
            
            # All filters passed - save recommendation
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

# ============ MODULE E: CLAIMS (Week 5) ============

@app.post("/claims")
def create_claim(
    token: str = Query(...),
    user_policy_id: int = None,
    claim_type: str = None,
    incident_date: str = None,
    amount_claimed: Decimal = None,
    description: str = None,
    db: Session = Depends(get_db)
):
    """Create a new insurance claim"""
    try:
        user = get_current_user(token, db)
        
        # Verify user owns the policy
        user_policy = db.query(models.UserPolicy).filter(
            models.UserPolicy.id == user_policy_id,
            models.UserPolicy.user_id == user.id
        ).first()
        
        if not user_policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Generate unique claim number
        claim_number = f"CLM-{uuid.uuid4().hex[:8].upper()}"
        
        claim = models.Claim(
            user_policy_id=user_policy_id,
            claim_number=claim_number,
            claim_type=claim_type,
            incident_date=incident_date,
            amount_claimed=amount_claimed,
            status="draft",
            description=description
        )
        
        db.add(claim)
        db.commit()
        db.refresh(claim)
        
        return {
            "id": claim.id,
            "claim_number": claim.claim_number,
            "status": claim.status,
            "created_at": claim.created_at
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/claims")
def get_user_claims(
    token: str = Query(...),
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get all claims for the logged-in user"""
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
        
        result.append({
            "id": claim.id,
            "claim_number": claim.claim_number,
            "claim_type": claim.claim_type,
            "amount_claimed": float(claim.amount_claimed),
            "status": claim.status,
            "incident_date": str(claim.incident_date),
            "created_at": claim.created_at,
            "policy": {
                "id": policy.id,
                "title": policy.title,
                "premium": float(policy.premium)
            },
            "documents_count": len(claim.documents)
        })
    
    return result

@app.get("/claims/{claim_id}")
def get_claim_detail(
    claim_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get detailed claim information"""
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
    
    return {
        "id": claim.id,
        "claim_number": claim.claim_number,
        "claim_type": claim.claim_type,
        "amount_claimed": float(claim.amount_claimed),
        "status": claim.status,
        "incident_date": str(claim.incident_date),
        "description": claim.description,
        "created_at": claim.created_at,
        "policy": {
            "id": policy.id,
            "title": policy.title,
            "premium": float(policy.premium),
            "policy_number": user_policy.policy_number
        },
        "documents": [
            {
                "id": doc.id,
                "doc_type": doc.doc_type,
                "file_url": doc.file_url,
                "uploaded_at": doc.uploaded_at
            }
            for doc in claim.documents
        ]
    }

@app.post("/claims/{claim_id}/documents")
def upload_claim_document(
    claim_id: int,
    token: str = Query(...),
    doc_type: str = None,
    file_content: str = None,
    file_name: str = None,
    db: Session = Depends(get_db)
):
    """Upload a document for a claim (base64 encoded or file reference)"""
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
        
        # For now, store as reference (in production would be S3/cloud storage)
        # Generate a file reference
        file_url = f"claims/{claim.claim_number}/{file_name}"
        
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
            "uploaded_at": doc.uploaded_at
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/claims/{claim_id}/submit")
def submit_claim(
    claim_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Submit a claim (change from draft to submitted)"""
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
    
    if claim.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft claims can be submitted")
    
    claim.status = "submitted"
    db.commit()
    
    return {
        "message": "Claim submitted successfully",
        "claim_number": claim.claim_number,
        "status": claim.status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)






