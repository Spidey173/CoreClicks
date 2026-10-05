import io
import json


class TestCalculatorApi:
    def test_calculate_and_history(self, auth_client):
        res = auth_client.post(
            "/api/v1/calculator/calculate",
            json={"expression": "100 * 2.5", "angle_mode": "rad"},
        )
        assert res.status_code == 201
        data = res.get_json()
        assert data["result"] == "250"

        # Read history
        hist = auth_client.get("/api/v1/calculator/history")
        assert hist.status_code == 200
        assert len(hist.get_json()) >= 1


class TestPasswordApi:
    def test_analyze_and_generate(self, auth_client):
        res = auth_client.post(
            "/api/v1/password-security/analyze",
            json={"password": "MyCustomStrongPassword!987"},
        )
        assert res.status_code == 201
        assert res.get_json()["analysis"]["score"] >= 80

        gen_res = auth_client.post(
            "/api/v1/password-security/generate",
            json={"type": "random", "length": 24},
        )
        assert gen_res.status_code == 200
        assert len(gen_res.get_json()["password"]) == 24


class TestTasksApi:
    def test_crud_and_kanban(self, auth_client):
        # Create
        create_res = auth_client.post(
            "/api/v1/tasks",
            json={"title": "Integration Test Task", "priority": "high", "category": "QA"},
        )
        assert create_res.status_code == 201
        task_id = create_res.get_json()["task"]["id"]

        # Read Kanban columns
        kanban_res = auth_client.get("/api/v1/tasks/kanban")
        assert kanban_res.status_code == 200
        assert "todo" in kanban_res.get_json()

        # Update position
        pos_res = auth_client.put(
            f"/api/v1/tasks/{task_id}/position",
            json={"status": "in_progress", "position": 0},
        )
        assert pos_res.status_code == 200
        assert pos_res.get_json()["task"]["status"] == "in_progress"

        # Delete
        del_res = auth_client.delete(f"/api/v1/tasks/{task_id}")
        assert del_res.status_code == 200


class TestNotesApi:
    def test_crud_and_versions(self, auth_client):
        create_res = auth_client.post(
            "/api/v1/notes",
            json={"title": "Test Note", "content": "# Heading\n\nContent here", "folder": "Testing"},
        )
        assert create_res.status_code == 201
        note_id = create_res.get_json()["note"]["id"]

        # Get
        get_res = auth_client.get(f"/api/v1/notes/{note_id}")
        assert get_res.status_code == 200
        assert get_res.get_json()["reading_stats"]["words"] >= 3

        # Update content (creates version)
        update_res = auth_client.put(
            f"/api/v1/notes/{note_id}",
            json={"content": "# Heading 2\n\nUpdated Content"},
        )
        assert update_res.status_code == 200

        # Read versions
        vers_res = auth_client.get(f"/api/v1/notes/{note_id}/versions")
        assert vers_res.status_code == 200
        assert len(vers_res.get_json()) >= 2

        # Delete
        del_res = auth_client.delete(f"/api/v1/notes/{note_id}")
        assert del_res.status_code == 200


class TestExpensesApi:
    def test_transactions_and_summary(self, auth_client):
        # Create transaction
        tx_res = auth_client.post(
            "/api/v1/expenses/transactions",
            json={"type": "expense", "amount": 75.50, "category": "Testing", "merchant": "Merchant Co"},
        )
        assert tx_res.status_code == 201

        # Summary
        sum_res = auth_client.get("/api/v1/expenses/summary")
        assert sum_res.status_code == 200
        assert sum_res.get_json()["total_expense"] >= 75.50


class TestColorToolsApi:
    def test_generate_and_contrast(self, auth_client):
        gen_res = auth_client.post(
            "/api/v1/color-tools/generate",
            json={"base_color": "#0ea5e9", "harmony": "Triadic"},
        )
        assert gen_res.status_code == 200
        assert len(gen_res.get_json()["palette"]) == 5

        contrast_res = auth_client.post(
            "/api/v1/color-tools/contrast",
            json={"foreground": "#000000", "background": "#ffffff"},
        )
        assert contrast_res.status_code == 200
        assert contrast_res.get_json()["ratio"] == 21.0


class TestUrlShortenerApi:
    def test_shorten_and_qr(self, auth_client):
        res = auth_client.post(
            "/api/v1/url-shortener",
            json={"url": "https://google.com", "title": "Google Search", "custom_code": "ggl"},
        )
        assert res.status_code == 201
        url_id = res.get_json()["short_url"]["id"]

        # QR Code
        qr_res = auth_client.get(f"/api/v1/url-shortener/{url_id}/qr?format=png")
        assert qr_res.status_code == 200
        assert qr_res.headers["Content-Type"] == "image/png"


class TestGlobalSearchAndNotifications:
    def test_omni_search(self, auth_client):
        res = auth_client.get("/api/v1/search?q=CoreClicks")
        assert res.status_code == 200
        assert "tasks" in res.get_json()["results"]

    def test_notifications(self, auth_client):
        res = auth_client.get("/api/v1/notifications")
        assert res.status_code == 200
        assert "notifications" in res.get_json()
