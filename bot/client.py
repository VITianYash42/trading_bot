from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict

from binance.client import Client
from dotenv import load_dotenv

LOGGER = logging.getLogger(__name__)

FUTURES_TESTNET_BASE_URL = "https://testnet.binancefuture.com"
FUTURES_API_PREFIX = "/fapi"


@dataclass(frozen=True)
class BinanceCredentials:
    api_key: str
    api_secret: str


class BinanceFuturesTestnetClient:
    """Wrapper around python-binance configured for USDT-M Futures Testnet."""

    def __init__(self, credentials: BinanceCredentials, timeout: int = 15) -> None:
        self._client = Client(
            api_key=credentials.api_key,
            api_secret=credentials.api_secret,
            requests_params={"timeout": timeout},
        )

        # Force Futures API calls to use Futures Testnet host only.
        self._client.FUTURES_URL = f"{FUTURES_TESTNET_BASE_URL}{FUTURES_API_PREFIX}"

        LOGGER.info(
            "Initialized Binance Futures testnet client with base URL %s",
            self._client.FUTURES_URL,
        )

    @classmethod
    def from_env(cls) -> "BinanceFuturesTestnetClient":
        load_dotenv()

        api_key = os.getenv("BINANCE_API_KEY", "").strip()
        api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

        if not api_key or not api_secret:
            raise ValueError(
                "Missing BINANCE_API_KEY or BINANCE_API_SECRET in environment variables."
            )

        credentials = BinanceCredentials(api_key=api_key, api_secret=api_secret)
        return cls(credentials=credentials)

    def ping(self) -> Dict[str, Any]:
        LOGGER.info("Request: futures_ping")
        response = self._client.futures_ping()
        LOGGER.info("Response: futures_ping -> %s", response)
        return response

    def exchange_info(self) -> Dict[str, Any]:
        LOGGER.info("Request: futures_exchange_info")
        response = self._client.futures_exchange_info()
        LOGGER.info("Response: futures_exchange_info received")
        return response

    def create_order(self, **order_params: Any) -> Dict[str, Any]:
        safe_payload = {
            key: str(value) if key in {"price", "quantity", "stopPrice"} else value
            for key, value in order_params.items()
        }
        LOGGER.info("Request: futures_create_order payload=%s", safe_payload)
        response = self._client.futures_create_order(**order_params)
        LOGGER.info("Response: futures_create_order -> %s", response)
        return response
