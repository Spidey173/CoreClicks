import pytest
from app import create_app
from app.extensions import db
from app.models.user import User, UserSettings


@pytest.fixture
def app():
    """Create application instance for testing."""
    test_app = create_app("testing")
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def auth_client(client, app):
    """Client logged in as a standard user."""
    with app.app_context():
        user = User.query.filter_by(email="admin@coreclicks.dev").first()
        if not user:
            user = User(email="admin@coreclicks.dev", username="admin", role="admin")
            user.set_password("Admin@12345")
            db.session.add(user)
            db.session.commit()

    # Log in via form
    client.post("/login", data={"identifier": "admin@coreclicks.dev", "password": "Admin@12345"}, follow_redirects=True)
    return client
