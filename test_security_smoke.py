import os
import unittest
from unittest.mock import patch

import app as trend_app


class ApiSecuritySmokeTests(unittest.TestCase):
    def setUp(self):
        self.client = trend_app.app.test_client()

    def test_api_trends_rejects_unknown_origin_without_api_key(self):
        with patch.dict(os.environ, {
            "FRONTEND_ORIGIN": "https://techtrendmonitor.onrender.com",
            "API_ROUTE_KEY": "demo-api-key",
        }, clear=False):
            response = self.client.get("/api/trends", headers={
                "Origin": "https://unknown.example.com",
            })

        self.assertEqual(response.status_code, 401)
        payload = response.get_json()
        self.assertEqual(payload["error"], "Unauthorized")

    def test_api_trends_allows_matching_frontend_origin(self):
        with patch.dict(os.environ, {
            "FRONTEND_ORIGIN": "https://techtrendmonitor.onrender.com",
            "API_ROUTE_KEY": "demo-api-key",
        }, clear=False), patch("app.get_trending_items", return_value=[]):
            response = self.client.get("/api/trends", headers={
                "Origin": "https://techtrendmonitor.onrender.com",
            })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Access-Control-Allow-Origin"),
            "https://techtrendmonitor.onrender.com",
        )

    def test_api_trends_allows_valid_api_key(self):
        with patch.dict(os.environ, {
            "FRONTEND_ORIGIN": "https://techtrendmonitor.onrender.com",
            "API_ROUTE_KEY": "demo-api-key",
        }, clear=False), patch("app.get_trending_items", return_value=[]):
            response = self.client.get("/api/trends", headers={
                "x-api-key": "demo-api-key",
            })

        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
