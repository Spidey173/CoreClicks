import pytest
from app import create_app
from app.extensions import db
from app.models.user import User, UserSettings


@pytest.fixture(scope="session")
def app():
    """Create application instance for testing."""
    test_app = create_app("testing")
    with test_app.app_context():
        db.create_all()
        yield test_app


@pytest.fixture(autouse=True)
def clean_db(app):
    """Keep test data clean between runs."""
    with app.app_context():
        User.query.filter(User.email.in_(["newuser@coreclicks.dev", "regtest@coreclicks.dev"])).delete()
        db.session.commit()
    yield
    with app.app_context():
        User.query.filter(User.email.in_(["newuser@coreclicks.dev", "regtest@coreclicks.dev"])).delete()
        db.session.commit()


@pytest.fixture
def client(app):
    """Fresh unauthenticated test client."""
    c = app.test_client()
    with c.session_transaction() as sess:
        sess.clear()
    return c


@pytest.fixture
def runner(app):
    """Test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def auth_client(app):
    """Client logged in as an admin user."""
    with app.app_context():
        user = User.query.filter_by(email="admin@coreclicks.dev").first()
        if not user:
            user = User(email="admin@coreclicks.dev", username="admin", role="admin")
            user.set_password("Admin@12345")
            db.session.add(user)
            db.session.commit()

    logged_client = app.test_client()
    logged_client.post("/login", data={"identifier": "admin@coreclicks.dev", "password": "Admin@12345"}, follow_redirects=True)
    return logged_client
