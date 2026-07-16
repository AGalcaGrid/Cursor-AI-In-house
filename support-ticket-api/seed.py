"""
Seed script to create initial admin and agent accounts.
Run with: python seed.py
"""
from app import create_app, db
from app.models.user import User

def seed_users():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                name='Admin User',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
            print('✓ Created admin user: admin@example.com / Admin123!')
        else:
            print('→ Admin user already exists: admin@example.com')
        
        # Check if agent already exists
        agent = User.query.filter_by(email='agent@example.com').first()
        if not agent:
            agent = User(
                name='Support Agent',
                email='agent@example.com',
                role='agent'
            )
            agent.set_password('Agent123!')
            db.session.add(agent)
            print('✓ Created agent user: agent@example.com / Agent123!')
        else:
            print('→ Agent user already exists: agent@example.com')
        
        db.session.commit()
        print('\nSeed completed!')
        print('\nYou can now log in with:')
        print('  Admin: admin@example.com / Admin123!')
        print('  Agent: agent@example.com / Agent123!')

if __name__ == '__main__':
    seed_users()
