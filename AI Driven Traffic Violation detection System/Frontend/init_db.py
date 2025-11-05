"""
Use the engine and session factory from the main app to avoid creating a second engine
and to keep sessions consistent across the project.
"""
from app import Base, User, Challan, engine, SessionLocal

# Keep a local name `Session` for compatibility with the original script
Session = SessionLocal


def init():
    Base.metadata.create_all(bind=engine)
    db = Session()

    # Add sample user if not exists
    user = db.query(User).filter(User.username == 'john').first()
    if not user:
        # Create new user
        from werkzeug.security import generate_password_hash
        user = User(
            username='john', 
            password_hash=generate_password_hash('password'),
            name='sri amarnadh',
            phone='9030773966',
            vehicle_type='two-wheeler',
            vehicle_number='AP28BD5766'
        )
        db.add(user)
        db.commit()
        print('Created new user (username: john, password: password)')
    else:
        # Update existing user's info
        user.name = 'sri amarnadh'
        user.phone = '9030773966'
        db.commit()
        print('Updated existing user info')

    # Delete existing challans
    db.query(Challan).filter(Challan.user_id == user.id).delete()
    
    # Add the two specific challans
    challans = [
        Challan(
            user_id=user.id,
            amount=2000,
            violation='Over Speeding',
            date='30/10/2025',
            location='Ring Road, Sector 15',
            evidence_image='https://via.placeholder.com/600x400?text=Speed+Violation',
            plate_image='https://via.placeholder.com/400x120?text=Plate+Image',
            status='unpaid'
        ),
        Challan(
            user_id=user.id,
            amount=1000,
            violation='Red Light Jump',
            date='23/10/2025',
            location='Central Square Junction',
            evidence_image='https://via.placeholder.com/600x400?text=Red+Light+Violation',
            plate_image='https://via.placeholder.com/400x120?text=Plate+Image',
            status='unpaid'
        )
    ]
    
    for c in challans:
        db.add(c)
    db.commit()
    print('Added 2 specific challans')

    db.close()


if __name__ == '__main__':
    init()
