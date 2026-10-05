def test_unauthenticated_landing(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"CoreClicks" in res.data
    assert b"Where high craft meets" in res.data


def test_unauthenticated_protected_redirect(client):
    res = client.get("/dashboard")
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "healthy"


def test_dashboard_authenticated(auth_client):
    res = auth_client.get("/dashboard")
    assert res.status_code == 200
    assert b"Welcome back" in res.data


def test_landing_explicit_route(auth_client):
    res = auth_client.get("/landing")
    assert res.status_code == 200
    assert b"CoreClicks" in res.data


def test_admin_panel(auth_client):
    res = auth_client.get("/admin")
    assert res.status_code == 200
    assert b"Administration Console" in res.data




def test_all_10_tools_views(auth_client):
    tools = [
        "/calculator",
        "/password-security",
        "/tasks",
        "/notes",
        "/api-tester",
        "/analytics",
        "/expenses",
        "/file-tools",
        "/color-tools",
        "/url-shortener",
    ]
    for route in tools:
        res = auth_client.get(route)
        assert res.status_code == 200, f"Failed on route {route}"


def test_404_handling(auth_client):
    res = auth_client.get("/non-existent-saas-route")
    assert res.status_code == 404
    assert b"404" in res.data
