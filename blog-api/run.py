from app import create_app, db
from app.models import User, Post, Comment, Category

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Post': Post,
        'Comment': Comment,
        'Category': Category
    }


def seed_categories():
    """Seed default categories."""
    categories = [
        {'name': 'Technology', 'slug': 'technology', 'description': 'Tech news and tutorials'},
        {'name': 'Lifestyle', 'slug': 'lifestyle', 'description': 'Life tips and experiences'},
        {'name': 'Travel', 'slug': 'travel', 'description': 'Travel stories and guides'},
        {'name': 'Food', 'slug': 'food', 'description': 'Recipes and food reviews'},
        {'name': 'Health', 'slug': 'health', 'description': 'Health and wellness tips'},
    ]
    
    with app.app_context():
        for cat_data in categories:
            if not Category.query.filter_by(slug=cat_data['slug']).first():
                category = Category(**cat_data)
                db.session.add(category)
        db.session.commit()
        print('Categories seeded successfully!')


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'seed':
        seed_categories()
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
