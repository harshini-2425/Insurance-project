from sqlalchemy import Column, Integer, String, Date, JSON, TIMESTAMP, ForeignKey, Numeric, Boolean, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    dob = Column(Date)
    risk_profile = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    user_policies = relationship("UserPolicy", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")
    fraud_flags = relationship("FraudFlag", back_populates="flagged_by_user")
    admin_logs = relationship("AdminLog", back_populates="admin")

class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    policies = relationship("Policy", back_populates="provider")

class PolicyTypeEnum(str, enum.Enum):
    auto = "auto"
    health = "health"
    life = "life"
    home = "home"
    travel = "travel"

class Policy(Base):
    __tablename__ = "policies"
    
    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    policy_type = Column(SQLEnum(PolicyTypeEnum), nullable=False)
    title = Column(String, nullable=False)
    coverage = Column(JSON, nullable=True)
    premium = Column(Numeric(10, 2), nullable=False)
    term_months = Column(Integer, nullable=False)
    deductible = Column(Numeric(10, 2), nullable=False)
    tnc_url = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    provider = relationship("Provider", back_populates="policies")
    user_policies = relationship("UserPolicy", back_populates="policy")
    recommendations = relationship("Recommendation", back_populates="policy")

class UserPolicyStatusEnum(str, enum.Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"

class UserPolicy(Base):
    __tablename__ = "user_policies"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)
    policy_number = Column(String, unique=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    premium = Column(Numeric(10, 2), nullable=False)
    status = Column(SQLEnum(UserPolicyStatusEnum), default=UserPolicyStatusEnum.active)
    auto_renew = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="user_policies")
    policy = relationship("Policy", back_populates="user_policies")
    claims = relationship("Claim", back_populates="user_policy")

class ClaimStatusEnum(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"
    paid = "paid"

class Claim(Base):
    __tablename__ = "claims"
    
    id = Column(Integer, primary_key=True)
    user_policy_id = Column(Integer, ForeignKey("user_policies.id"), nullable=False)
    claim_number = Column(String, unique=True, nullable=False)
    claim_type = Column(String, nullable=False)
    incident_date = Column(Date, nullable=False)
    amount_claimed = Column(Numeric(10, 2), nullable=False)
    status = Column(SQLEnum(ClaimStatusEnum), default=ClaimStatusEnum.draft)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    user_policy = relationship("UserPolicy", back_populates="claims")
    documents = relationship("ClaimDocument", back_populates="claim")
    fraud_flags = relationship("FraudFlag", back_populates="claim")

class ClaimDocument(Base):
    __tablename__ = "claim_documents"
    
    id = Column(Integer, primary_key=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    file_url = Column(String, nullable=False)
    doc_type = Column(String, nullable=False)
    uploaded_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    claim = relationship("Claim", back_populates="documents")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)
    score = Column(Numeric(5, 2), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="recommendations")
    policy = relationship("Policy", back_populates="recommendations")

class FraudSeverityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class FraudFlag(Base):
    __tablename__ = "fraud_flags"
    
    id = Column(Integer, primary_key=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    rule_code = Column(String, nullable=False)
    severity = Column(SQLEnum(FraudSeverityEnum), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    flagged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    claim = relationship("Claim", back_populates="fraud_flags")
    flagged_by_user = relationship("User", back_populates="fraud_flags")

class AdminLog(Base):
    __tablename__ = "admin_logs"
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    target_type = Column(String, nullable=False)
    target_id = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    admin = relationship("User", back_populates="admin_logs")
