from __future__ import annotations

import math
from typing import Any, Dict, Optional

from .orders import OrderSide, OrderType


class ValidationError(Exception):
    """Raised when user-provided data is invalid."""


def normalize_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not normalized:
        raise ValidationError("Symbol is required.")
    if not normalized.endswith("USDT"):
        raise ValidationError("Only USDT-M symbols are supported (example: BTCUSDT).")
    return normalized


def validate_side(side: str) -> OrderSide:
    value = side.strip().upper()
    try:
        return OrderSide(value)
    except ValueError as exc:
        raise ValidationError("Side must be BUY or SELL.") from exc


def validate_order_type(order_type: str) -> OrderType:
    value = order_type.strip().upper()
    try:
        return OrderType(value)
    except ValueError as exc:
        raise ValidationError(
            "Order type must be one of: MARKET, LIMIT, STOP_MARKET."
        ) from exc


def validate_quantity(quantity: float) -> float:
    if not math.isfinite(quantity) or quantity <= 0:
        raise ValidationError("Quantity must be a positive number.")
    return quantity


def validate_price(
    value: Optional[float],
    *,
    required: bool,
    field_name: str,
) -> Optional[float]:
    if value is None:
        if required:
            raise ValidationError(f"{field_name} is required for this order type.")
        return None

    if not math.isfinite(value) or value <= 0:
        raise ValidationError(f"{field_name} must be a positive number.")
    return value


def validate_symbol_on_exchange(symbol: str, exchange_info: Dict[str, Any]) -> None:
    symbols = exchange_info.get("symbols", [])
    for item in symbols:
        if item.get("symbol") == symbol:
            if item.get("status") != "TRADING":
                raise ValidationError(
                    f"Symbol {symbol} is currently not tradable on Futures Testnet."
                )
            return

    raise ValidationError(f"Symbol {symbol} was not found on Futures Testnet.")
