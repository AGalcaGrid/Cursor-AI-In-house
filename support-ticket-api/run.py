from app import create_app, db
from app.models import User, Ticket, Comment, Assignment, Attachment

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Ticket': Ticket,
        'Comment': Comment,
        'Assignment': Assignment,
        'Attachment': Attachment
    }


def seed_data():
    """Seed initial data for development."""
    with app.app_context():
        # Create admin user
        if not User.query.filter_by(email='admin@support.com').first():
            admin = User(
                name='Admin User',
                email='admin@support.com',
                role='admin'
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
        
        # Create agent user
        if not User.query.filter_by(email='agent@support.com').first():
            agent = User(
                name='Support Agent',
                email='agent@support.com',
                role='agent',
                expertise_areas=['technical', 'billing']
            )
            agent.set_password('Agent123!')
            db.session.add(agent)
        
        # Create customer user
        if not User.query.filter_by(email='customer@example.com').first():
            customer = User(
                name='Test Customer',
                email='customer@example.com',
                role='customer'
            )
            customer.set_password('Customer123!')
            db.session.add(customer)
        
        db.session.commit()
        print('Seed data created successfully!')


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'seed':
        seed_data()
    else:
        app.run(host='0.0.0.0', port=5002, debug=True)
