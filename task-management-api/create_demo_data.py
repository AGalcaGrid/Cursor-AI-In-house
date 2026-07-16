"""
Create demo admin user with sample tasks for demonstration
"""
from app import create_app, db
from app.models.user import User
from app.models.task import Task
from app.models.project import Project
from datetime import datetime, timedelta

def create_demo_data():
    app = create_app('development')
    
    with app.app_context():
        # Check if demo user already exists
        existing_user = User.query.filter_by(email='admin@demo.com').first()
        if existing_user:
            print('❌ Demo admin user already exists!')
            print('   Email: admin@demo.com')
            print('   Password: admin123')
            return
        
        # Create demo admin user
        print('Creating demo admin user...')
        admin = User(
            username='admin',
            email='admin@demo.com'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('✅ Demo admin user created!')
        
        # Create demo project
        print('Creating demo project...')
        project = Project(
            name='Website Redesign',
            description='Complete redesign of company website with modern UI/UX',
            status='active',
            owner_id=admin.id
        )
        db.session.add(project)
        db.session.commit()
        print('✅ Demo project created!')
        
        # Create sample tasks
        print('Creating sample tasks...')
        
        tasks_data = [
            {
                'title': 'Design new landing page',
                'description': 'Create wireframes and mockups for the new marketing landing page with modern design principles',
                'status': 'in_progress',
                'priority': 'high',
                'due_date': datetime.utcnow() + timedelta(days=2)
            },
            {
                'title': 'Implement user authentication',
                'description': 'Set up JWT authentication with login, register, and password reset functionality',
                'status': 'in_progress',
                'priority': 'high',
                'due_date': datetime.utcnow() + timedelta(days=5)
            },
            {
                'title': 'Write API documentation',
                'description': 'Document all REST API endpoints with Swagger/OpenAPI specifications',
                'status': 'pending',
                'priority': 'medium',
                'due_date': datetime.utcnow() + timedelta(days=7)
            },
            {
                'title': 'Fix mobile navigation bug',
                'description': 'Navigation menu not closing properly on mobile devices after clicking a link',
                'status': 'in_progress',
                'priority': 'high',
                'due_date': datetime.utcnow() + timedelta(days=1)
            },
            {
                'title': 'Set up CI/CD pipeline',
                'description': 'Configure GitHub Actions for automated testing and deployment to production',
                'status': 'completed',
                'priority': 'high',
                'due_date': datetime.utcnow() - timedelta(days=1)
            },
            {
                'title': 'Review pull requests',
                'description': 'Review and merge pending pull requests from team members',
                'status': 'completed',
                'priority': 'low',
                'due_date': datetime.utcnow() - timedelta(days=2)
            },
            {
                'title': 'Update dependencies',
                'description': 'Update all npm packages to their latest stable versions',
                'status': 'pending',
                'priority': 'low',
                'due_date': datetime.utcnow() + timedelta(days=10)
            },
            {
                'title': 'Performance optimization',
                'description': 'Analyze and optimize bundle size and loading performance',
                'status': 'pending',
                'priority': 'medium',
                'due_date': datetime.utcnow() + timedelta(days=14)
            },
            {
                'title': 'Database migration',
                'description': 'Migrate from SQLite to PostgreSQL for production deployment',
                'status': 'pending',
                'priority': 'high',
                'due_date': datetime.utcnow() + timedelta(days=3)
            },
            {
                'title': 'Add dark mode support',
                'description': 'Implement dark mode theme with user preference persistence',
                'status': 'completed',
                'priority': 'medium',
                'due_date': datetime.utcnow() - timedelta(days=5)
            },
            {
                'title': 'Create user onboarding flow',
                'description': 'Design and implement interactive onboarding tutorial for new users',
                'status': 'pending',
                'priority': 'medium',
                'due_date': datetime.utcnow() + timedelta(days=12)
            },
            {
                'title': 'Security audit',
                'description': 'Conduct comprehensive security audit and fix vulnerabilities',
                'status': 'in_progress',
                'priority': 'high',
                'due_date': datetime.utcnow() + timedelta(days=4)
            },
        ]
        
        for task_data in tasks_data:
            task = Task(
                user_id=admin.id,
                project_id=project.id,
                **task_data
            )
            db.session.add(task)
        
        db.session.commit()
        print(f'✅ Created {len(tasks_data)} sample tasks!')
        
        print('\n' + '='*50)
        print('🎉 Demo data created successfully!')
        print('='*50)
        print('\n📧 Demo Admin Credentials:')
        print('   Email: admin@demo.com')
        print('   Password: admin123')
        print('\n🎯 Login at: http://localhost:5174')
        print('   Click "Open Dashboard" → Login with above credentials')
        print('\n✅ You will see:')
        print(f'   - {len(tasks_data)} tasks in the dashboard')
        print('   - 1 project (Website Redesign)')
        print('   - Tasks with different statuses and priorities')
        print('='*50)

if __name__ == '__main__':
    create_demo_data()
