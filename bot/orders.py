from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any, Dict, Optional

from .client import BinanceFuturesTestnetClient

LOGGER = logging.getLogger(__name__)


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_MARKET = "STOP_MARKET"


@dataclass(frozen=True)
class OrderRequest:
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None


@dataclass(frozen=True)
class OrderResult:
    order_id: int
    status: str
    executed_qty: float
    avg_price: Optional[float]
    raw_response: Dict[str, Any]


class OrderPlacementError(Exception):
    """Raised when order placement fails unexpectedly."""


class OrderService:
    def __init__(self, client: BinanceFuturesTestnetClient) -> None:
        self._client = client

    def place_order(self, order_request: OrderRequest) -> OrderResult:
        params: Dict[str, Any] = {
            "symbol": order_request.symbol,
            "side": order_request.side.value,
            "type": order_request.order_type.value,
            "quantity": order_request.quantity,
        }

        if order_request.order_type == OrderType.LIMIT:
            params["timeInForce"] = "GTC"
            params["price"] = order_request.price

        if order_request.order_type == OrderType.STOP_MARKET:
            params["stopPrice"] = order_request.stop_price

        try:
            response = self._client.create_order(**params)
            result = OrderResult(
                order_id=int(response.get("orderId", 0)),
                status=str(response.get("status", "UNKNOWN")),
                executed_qty=float(response.get("executedQty", 0.0)),
                avg_price=self._extract_avg_price(response),
                raw_response=response,
            )
            LOGGER.info("Order placed successfully: order_id=%s", result.order_id)
            return result
        except Exception as exc:  # Handled explicitly at CLI boundary.
            LOGGER.exception("Order placement failed: %s", exc)
            raise OrderPlacementError(str(exc)) from exc

    @staticmethod
    def _extract_avg_price(response: Dict[str, Any]) -> Optional[float]:
        avg_price_raw = response.get("avgPrice")
        if avg_price_raw not in (None, "", "0", "0.0"):
            try:
                avg_price = float(avg_price_raw)
                if avg_price > 0:
                    return avg_price
            except (TypeError, ValueError):
                pass

        try:
            executed_qty = Decimal(str(response.get("executedQty", "0")))
            quote_qty = Decimal(
                str(
                    response.get(
                        "cumQuote",
                        response.get("cummulativeQuoteQty", "0"),
                    )
                )
            )
            if executed_qty > 0 and quote_qty > 0:
                return float(quote_qty / executed_qty)
        except (InvalidOperation, ZeroDivisionError, TypeError, ValueError):
            return None

        return None
