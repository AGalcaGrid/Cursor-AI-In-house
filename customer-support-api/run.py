import os
from app import create_app, db

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """Make database available in flask shell."""
    return {'db': db}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
