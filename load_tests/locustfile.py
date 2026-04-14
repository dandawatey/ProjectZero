"""
ProjectZero Factory — Locust load test — PRJ0-68

Usage:
  locust -f load_tests/locustfile.py --headless -u 50 -r 10 --run-time 60s --host http://localhost:8000

Targets:
  - GET /health            (unauthenticated, lightest)
  - GET /api/v1/agents     (authenticated, list)
  - GET /api/v1/commands/sprint (authenticated, JIRA fetch)
  - GET /api/v1/brain/memories (authenticated, DB query)
  - POST /api/v1/commands/check (authenticated, subprocess)
"""

from locust import HttpUser, task, between, events
import os, json, logging

logger = logging.getLogger(__name__)

# Set via env or hardcode test credentials
TEST_EMAIL = os.getenv("LOAD_TEST_EMAIL", "loadtest@example.com")
TEST_PASSWORD = os.getenv("LOAD_TEST_PASSWORD", "LoadTest123!")


class ProjectZeroUser(HttpUser):
    wait_time = between(1, 3)
    token: str = ""

    def on_start(self):
        """Login and store JWT token."""
        # Try register first (idempotent — may already exist)
        self.client.post("/api/v1/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": "Load Test User",
        }, name="[setup] register")

        resp = self.client.post("/api/v1/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        }, name="[setup] login")

        if resp.status_code == 200:
            self.token = resp.json().get("access_token", "")
        else:
            logger.warning("Login failed: %s %s", resp.status_code, resp.text[:100])

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    @task(5)
    def health_check(self):
        self.client.get("/health", name="GET /health")

    @task(4)
    def list_agents(self):
        self.client.get("/api/v1/agents", headers=self._headers(), name="GET /agents")

    @task(3)
    def list_agent_skills(self):
        self.client.get("/api/v1/agents/skills", headers=self._headers(), name="GET /agents/skills")

    @task(3)
    def get_dashboard(self):
        self.client.get("/api/v1/dashboard", headers=self._headers(), name="GET /dashboard")

    @task(2)
    def list_brain_memories(self):
        self.client.get("/api/v1/brain/memories", headers=self._headers(), name="GET /brain/memories")

    @task(2)
    def get_sprint(self):
        with self.client.get(
            "/api/v1/commands/sprint",
            headers=self._headers(),
            name="GET /commands/sprint",
            catch_response=True,
        ) as resp:
            # JIRA may be slow — accept 503 as non-failure
            if resp.status_code in (200, 400, 503):
                resp.success()

    @task(2)
    def list_activities(self):
        self.client.get("/api/v1/activities", headers=self._headers(), name="GET /activities")

    @task(1)
    def run_check_command(self):
        with self.client.post(
            "/api/v1/commands/check",
            headers=self._headers(),
            json={"repo_path": "/tmp", "product_id": "load-test"},
            name="POST /commands/check",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code in (401, 422):
                resp.failure(f"Unexpected {resp.status_code}")

    @task(1)
    def list_products(self):
        self.client.get("/api/v1/products", headers=self._headers(), name="GET /products")
