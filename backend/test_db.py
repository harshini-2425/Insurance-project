import sys
from datetime import date
from database import engine, SessionLocal
from models import User
import schemas

# Test database connection
try:
    print("Testing database connection...")
    db = SessionLocal()
    print("✓ Database connection successful")
    
    # Test creating a user
    print("\nTesting user creation...")
    test_user = User(
        name="Test User",
        email="test@test.com",
        password="hashedpassword",
        dob=date(1990, 1, 1)
    )
    db.add(test_user)
    db.commit()
    print("✓ User creation successful")
    
    # Verify user was created
    user = db.query(User).filter(User.email == "test@test.com").first()
    if user:
        print(f"✓ User found: {user.name} ({user.email})")
    
    db.close()
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
