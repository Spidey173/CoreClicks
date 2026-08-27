import pytest
from app.models.user import User, APIKey
from app.services.auth_service import authenticate_user, create_api_key, register_user


def test_user_registration(app):
    with app.app_context():
        user, err = register_user("newuser@coreclicks.dev", "newuser", "SecurePass123!")
        assert err is None
        assert user is not None
        assert user.check_password("SecurePass123!") is True
        assert user.check_password("WrongPassword") is False


def test_user_registration_validation(app):
    with app.app_context():
        # Duplicate email
        user, err = register_user("admin@coreclicks.dev", "admin_dup", "Pass12345!")
        assert user is None
        assert "already exists" in err

        # Short password
        user, err = register_user("valid@domain.com", "validuser", "123")
        assert user is None
        assert "at least 6 characters" in err


def test_user_authentication(app):
    with app.app_context():
        user = authenticate_user("admin@coreclicks.dev", "Admin@12345")
        assert user is not None
        assert user.username == "admin"

        wrong_user = authenticate_user("admin@coreclicks.dev", "WrongPass")
        assert wrong_user is None


def test_api_key_generation(app):
    with app.app_context():
        user = User.query.filter_by(email="admin@coreclicks.dev").first()
        raw_key, key_obj = create_api_key(user.id, "CI Runner")
        assert raw_key.startswith("cck_")
        assert key_obj.key_prefix == raw_key[:10]
        assert key_obj.is_active is True


def test_auth_routes(client):
    # Login page
    res = client.get("/login")
    assert res.status_code == 200
    assert b"Sign In" in res.data

    # Register page
    res_reg = client.get("/register")
    assert res_reg.status_code == 200
    assert b"Create Account" in res_reg.data

    # Successful login
    login_res = client.post("/login", data={"identifier": "admin@coreclicks.dev", "password": "Admin@12345"}, follow_redirects=True)
    assert login_res.status_code == 200
    assert b"Welcome back" in login_res.data
