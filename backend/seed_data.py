"""
Seed script to populate database with sample providers and policies
Run this once to initialize the database with test data
"""
from database import SessionLocal, engine
import models
from decimal import Decimal

def seed_database():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(models.Provider).first():
            print("Database already seeded. Skipping...")
            return
        
        # Create Providers
        providers_data = [
            {"name": "SafeGuard Insurance", "country": "USA"},
            {"name": "Guardian Life", "country": "USA"},
            {"name": "AXA Global", "country": "France"},
            {"name": "Allianz", "country": "Germany"},
            {"name": "State Farm", "country": "USA"},
        ]
        
        providers = []
        for p_data in providers_data:
            provider = models.Provider(**p_data)
            db.add(provider)
            db.flush()
            providers.append(provider)
        
        db.commit()
        
        # Create Policies
        policies_data = [
            # Auto Insurance
            {
                "provider_id": providers[0].id,
                "policy_type": "auto",
                "title": "Basic Auto Coverage",
                "coverage": {
                    "liability": "$100,000",
                    "collision": "Yes",
                    "comprehensive": "Yes",
                    "medical": "$5,000"
                },
                "premium": Decimal("85.00"),
                "term_months": 12,
                "deductible": Decimal("500.00"),
                "tnc_url": "https://example.com/auto-tnc"
            },
            {
                "provider_id": providers[1].id,
                "policy_type": "auto",
                "title": "Premium Auto Plus",
                "coverage": {
                    "liability": "$250,000",
                    "collision": "Yes",
                    "comprehensive": "Yes",
                    "medical": "$10,000",
                    "roadside_assist": "Yes"
                },
                "premium": Decimal("125.00"),
                "term_months": 12,
                "deductible": Decimal("250.00"),
                "tnc_url": "https://example.com/auto-premium-tnc"
            },
            
            # Health Insurance
            {
                "provider_id": providers[2].id,
                "policy_type": "health",
                "title": "Basic Health Plan",
                "coverage": {
                    "hospitalization": "Yes",
                    "outpatient": "Yes",
                    "dental": "Limited",
                    "vision": "Limited",
                    "maternity": "Yes"
                },
                "premium": Decimal("300.00"),
                "term_months": 12,
                "deductible": Decimal("1000.00"),
                "tnc_url": "https://example.com/health-basic-tnc"
            },
            {
                "provider_id": providers[3].id,
                "policy_type": "health",
                "title": "Family Health Coverage",
                "coverage": {
                    "hospitalization": "Yes",
                    "outpatient": "Yes",
                    "dental": "Full",
                    "vision": "Full",
                    "maternity": "Yes",
                    "preventive": "Yes"
                },
                "premium": Decimal("650.00"),
                "term_months": 12,
                "deductible": Decimal("500.00"),
                "tnc_url": "https://example.com/health-family-tnc"
            },
            
            # Life Insurance
            {
                "provider_id": providers[0].id,
                "policy_type": "life",
                "title": "Term Life 20-Year",
                "coverage": {
                    "death_benefit": "$500,000",
                    "accidental_death": "$500,000",
                    "disability_waiver": "Yes"
                },
                "premium": Decimal("45.00"),
                "term_months": 240,
                "deductible": Decimal("0.00"),
                "tnc_url": "https://example.com/life-term-tnc"
            },
            {
                "provider_id": providers[4].id,
                "policy_type": "life",
                "title": "Whole Life Forever",
                "coverage": {
                    "death_benefit": "$250,000",
                    "cash_value": "Yes",
                    "accidental_death": "$250,000"
                },
                "premium": Decimal("150.00"),
                "term_months": 600,
                "deductible": Decimal("0.00"),
                "tnc_url": "https://example.com/life-whole-tnc"
            },
            
            # Home Insurance
            {
                "provider_id": providers[1].id,
                "policy_type": "home",
                "title": "Basic Home Coverage",
                "coverage": {
                    "dwelling": "$300,000",
                    "personal_property": "$100,000",
                    "liability": "$100,000",
                    "medical_payments": "$1,000"
                },
                "premium": Decimal("95.00"),
                "term_months": 12,
                "deductible": Decimal("1000.00"),
                "tnc_url": "https://example.com/home-basic-tnc"
            },
            {
                "provider_id": providers[2].id,
                "policy_type": "home",
                "title": "Complete Home Protection",
                "coverage": {
                    "dwelling": "$500,000",
                    "personal_property": "$250,000",
                    "liability": "$300,000",
                    "medical_payments": "$5,000",
                    "replacement_cost": "Yes"
                },
                "premium": Decimal("180.00"),
                "term_months": 12,
                "deductible": Decimal("500.00"),
                "tnc_url": "https://example.com/home-complete-tnc"
            },
            
            # Travel Insurance
            {
                "provider_id": providers[3].id,
                "policy_type": "travel",
                "title": "Budget Travel Plan",
                "coverage": {
                    "trip_cancellation": "$2,500",
                    "medical_emergency": "$50,000",
                    "baggage_delay": "$200",
                    "flight_delay": "$300"
                },
                "premium": Decimal("25.00"),
                "term_months": 1,
                "deductible": Decimal("250.00"),
                "tnc_url": "https://example.com/travel-budget-tnc"
            },
            {
                "provider_id": providers[4].id,
                "policy_type": "travel",
                "title": "Premium International Travel",
                "coverage": {
                    "trip_cancellation": "$10,000",
                    "medical_emergency": "$250,000",
                    "baggage_loss": "$5,000",
                    "flight_delay": "$500",
                    "emergency_evacuation": "Yes"
                },
                "premium": Decimal("85.00"),
                "term_months": 1,
                "deductible": Decimal("100.00"),
                "tnc_url": "https://example.com/travel-premium-tnc"
            },
            # ADD BELOW EXISTING policies_data list

# Family Health – High Income
            {
                "provider_id": providers[3].id,
                "policy_type": "health",
                "title": "Elite Family Health Shield",
                "coverage": {
                    "hospitalization": "Yes",
                    "maternity": "Yes",
                    "kids_coverage": "Yes",
                    "icu": "Unlimited"
                },
                "premium": Decimal("1200.00"),
                "term_months": 12,
                "deductible": Decimal("200.00"),
                "tnc_url": "https://example.com/family-health-elite"
           },

# Low Income Health
          {
            "provider_id": providers[1].id,
            "policy_type": "health",
            "title": "Basic Health Saver",
            "coverage": {
                "hospitalization": "Yes",
                "kids_coverage": "No",
                "maternity": "No"
            },
            "premium": Decimal("180.00"),
            "term_months": 12,
            "deductible": Decimal("3000.00"),
            "tnc_url": "https://example.com/basic-health"
      },

        ]
        
        for p_data in policies_data:
            policy = models.Policy(**p_data)
            db.add(policy)
        
        db.commit()
        print(f"✅ Seeded {len(providers)} providers and {len(policies_data)} policies")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
