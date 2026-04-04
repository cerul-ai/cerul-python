from __future__ import annotations

import asyncio
import json
import unittest

import httpx

from cerul import AsyncCerul, Cerul, CerulError


class CerulClientTests(unittest.TestCase):
    def test_search_sends_expected_payload(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.method, "POST")
            self.assertEqual(str(request.url), "https://api.cerul.ai/v1/search")
            self.assertEqual(request.headers["Authorization"], "Bearer cerul_sk_test")
            self.assertEqual(request.headers["X-Cerul-Client-Source"], "sdk-python")
            self.assertEqual(
                json.loads(request.content.decode("utf-8")),
                {
                    "query": "Sam Altman",
                    "max_results": 5,
                    "ranking_mode": "embedding",
                    "include_answer": True,
                    "filters": {"speaker": "Sam Altman"},
                },
            )
            return httpx.Response(
                200,
                json={
                    "results": [],
                    "credits_used": 1,
                    "credits_remaining": 9,
                    "request_id": "req_test_123",
                },
            )

        client = Cerul(api_key="cerul_sk_test", transport=httpx.MockTransport(handler))
        try:
            response = client.search(
                query="Sam Altman",
                max_results=5,
                include_answer=True,
                filters={"speaker": "Sam Altman"},
            )
        finally:
            client.close()

        self.assertEqual(response.request_id, "req_test_123")

    def test_usage_retries_on_server_error(self) -> None:
        attempts = {"count": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            attempts["count"] += 1
            if attempts["count"] == 1:
                return httpx.Response(
                    500,
                    json={"error": {"code": "api_error", "message": "temporary failure"}},
                )
            return httpx.Response(
                200,
                json={
                    "tier": "free",
                    "plan_code": "free",
                    "period_start": "2026-04-01",
                    "period_end": "2026-04-30",
                    "credits_limit": 0,
                    "credits_used": 1,
                    "credits_remaining": 9,
                    "wallet_balance": 9,
                    "credit_breakdown": {
                        "included_remaining": 0,
                        "bonus_remaining": 9,
                        "paid_remaining": 0,
                    },
                    "expiring_credits": [],
                    "rate_limit_per_sec": 1,
                    "api_keys_active": 1,
                    "billing_hold": False,
                    "daily_free_remaining": 9,
                    "daily_free_limit": 10,
                },
            )

        client = Cerul(api_key="cerul_sk_test", retry=True, transport=httpx.MockTransport(handler))
        try:
            response = client.usage()
        finally:
            client.close()

        self.assertEqual(attempts["count"], 2)
        self.assertEqual(response.credits_remaining, 9)

    def test_async_client_raises_timeout(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("timed out", request=request)

        async def run_test() -> None:
            client = AsyncCerul(api_key="cerul_sk_test", transport=httpx.MockTransport(handler))
            try:
                with self.assertRaises(CerulError) as error:
                    await client.search(query="timeout")
            finally:
                await client.close()

            self.assertEqual(error.exception.code, "timeout")
            self.assertEqual(error.exception.status_code, 0)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
