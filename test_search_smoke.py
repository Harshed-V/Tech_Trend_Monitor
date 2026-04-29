import unittest
from unittest.mock import patch

import app as trend_app
from trend_service import filter_items_by_query


class SearchSmokeTests(unittest.TestCase):
    def test_filter_handles_none_fields(self):
        items = [
            {
                "title": "Open AI Toolkit",
                "description": None,
                "topic": "AI",
                "name": "open-ai-toolkit",
                "source": "GitHub"
            }
        ]

        result = filter_items_by_query(items, "ai")
        self.assertEqual(len(result), 1)

    def test_api_trends_search_returns_json(self):
        mocked_items = [
            {
                "title": "AI Repo",
                "name": "AI Repo",
                "score": 1200,
                "score_label": "stars",
                "description": "AI utilities",
                "link": "https://example.com/ai-repo",
                "topic": "AI",
                "source": "GitHub",
                "why_trending": "Strong adoption"
            }
        ]

        with patch("app.search_items_across_pages", return_value=mocked_items):
            client = trend_app.app.test_client()
            response = client.get("/api/trends?type=weekly&page=1&q=ai")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIsInstance(payload, dict)
        self.assertIn("items", payload)
        self.assertEqual(len(payload["items"]), 1)
        self.assertEqual(payload["items"][0]["title"], "AI Repo")


if __name__ == "__main__":
    unittest.main()
