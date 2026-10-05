import concurrent.futures
import pytest
from app.security.ssrf_guard import validate_target_url, SSRFValidationError
from app.services.snowflake import SnowflakeGenerator, generate_snowflake_code
from app.services.bloom_service import BloomFilter
from app.models.webhook import WebhookEndpoint, WebhookDelivery


class TestSSRFGuard:
    """Security tests for Anti-SSRF and DNS rebinding protections."""

    def test_ssrf_blocks_localhost(self):
        with pytest.raises(SSRFValidationError) as exc:
            validate_target_url("http://localhost:5000/admin")
        assert "blocked" in str(exc.value).lower()

    def test_ssrf_blocks_loopback_ip(self):
        with pytest.raises(SSRFValidationError) as exc:
            validate_target_url("http://127.0.0.1:8080")
        assert "blocked" in str(exc.value).lower()

    def test_ssrf_blocks_cloud_metadata(self):
        with pytest.raises(SSRFValidationError) as exc:
            validate_target_url("http://169.254.169.254/latest/meta-data/")
        assert "blocked" in str(exc.value).lower()

    def test_ssrf_blocks_private_rfc1918(self):
        for ip in ("10.0.0.1", "172.16.0.1", "192.168.1.1"):
            with pytest.raises(SSRFValidationError) as exc:
                validate_target_url(f"http://{ip}/secret")
            assert "blocked" in str(exc.value).lower()

    def test_ssrf_blocks_illegal_schemes(self):
        for scheme in ("ftp://example.com", "file:///etc/passwd", "gopher://example.com"):
            with pytest.raises(SSRFValidationError) as exc:
                validate_target_url(scheme)
            assert "prohibited" in str(exc.value).lower()

    def test_ssrf_allows_legitimate_url(self):
        url, ip = validate_target_url("https://example.com")
        assert url.startswith("https://example.com")
        assert ip is not None


class TestSnowflakeConcurrency:
    """Tests Twitter Snowflake Base62 uniqueness and high-throughput concurrency."""

    def test_snowflake_uniqueness_across_threads(self):
        generator = SnowflakeGenerator(node_id=42)
        total_ids = 10000

        def worker(_):
            return generator.next_id()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(worker, range(total_ids)))

        # Assert zero collisions
        unique_results = set(results)
        assert len(unique_results) == total_ids

    def test_snowflake_base62_encoding(self):
        code = generate_snowflake_code()
        assert len(code) >= 6
        assert code.isalnum()


class TestBloomFilter:
    """Tests probabilistic Bloom Filter cache shielding."""

    def test_bloom_membership(self):
        bf = BloomFilter(capacity=10000, error_rate=0.01)
        test_items = [f"short_{i}" for i in range(100)]

        for item in test_items:
            bf.add(item)

        # All added items must return True
        for item in test_items:
            assert bf.contains(item) is True

        # Non-existent item should return False
        assert bf.contains("non_existent_key_999999") is False


class TestWebhooksPlatform:
    """Tests Webhook Interceptor and capture pipeline."""

    def test_webhook_capture_flow(self, app, client):
        with app.app_context():
            from app.models.user import User
            user = User.query.filter_by(email="admin@coreclicks.dev").first()
            endpoint = WebhookEndpoint.query.filter_by(endpoint_token="testtok123").first()
            if not endpoint:
                endpoint = WebhookEndpoint(user_id=user.id, endpoint_token="testtok123", name="Stripe Test")
                from app.extensions import db
                db.session.add(endpoint)
                db.session.commit()
            endpoint_id = endpoint.id

        # Hit public webhook listener
        payload = {"event": "payment.succeeded", "amount": 9900}
        res = client.post(
            "/hook/testtok123",
            json=payload,
            headers={"X-Hub-Signature-256": "sha256=abcdef123456"}
        )
        assert res.status_code == 200
        assert res.json["status"] == "success"

        # Verify recorded delivery
        with app.app_context():
            delivery = WebhookDelivery.query.filter_by(endpoint_id=endpoint_id).first()
            assert delivery is not None
            assert delivery.signature_header == "sha256=abcdef123456"
            assert "payment.succeeded" in delivery.payload_json
