from __future__ import annotations

import logging
from typing import Optional

import requests
import typer
from binance.exceptions import BinanceAPIException, BinanceRequestException
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from bot.client import BinanceFuturesTestnetClient
from bot.logging_config import LOG_FILE_PATH, configure_logging
from bot.orders import OrderRequest, OrderService, OrderType
from bot.validators import (
    ValidationError,
    normalize_symbol,
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol_on_exchange,
)

app = typer.Typer(help="Binance Futures Testnet trading bot", no_args_is_help=True)
console = Console()
logger = logging.getLogger(__name__)


def _render_request_summary(order_request: OrderRequest) -> None:
    table = Table(title="Order Request Summary", box=box.ROUNDED)
    table.add_column("Field", style="cyan", justify="right")
    table.add_column("Value", style="white")
    table.add_row("Symbol", order_request.symbol)
    table.add_row("Side", order_request.side.value)
    table.add_row("Order Type", order_request.order_type.value)
    table.add_row("Quantity", str(order_request.quantity))
    table.add_row("Price", "-" if order_request.price is None else str(order_request.price))
    table.add_row(
        "Stop Price",
        "-" if order_request.stop_price is None else str(order_request.stop_price),
    )
    console.print(table)


def _render_order_response(result: dict) -> None:
    table = Table(title="Order Response Details", box=box.ROUNDED)
    table.add_column("Field", style="green", justify="right")
    table.add_column("Value", style="white")
    table.add_row("orderId", str(result.get("orderId", "N/A")))
    table.add_row("status", str(result.get("status", "N/A")))
    table.add_row("executedQty", str(result.get("executedQty", "N/A")))

    avg_price = result.get("avgPrice")
    if avg_price in (None, "", "0", "0.0"):
        avg_price = result.get("price", "N/A")
    table.add_row("avgPrice", str(avg_price))

    console.print(table)


@app.command("place")
def place_order(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Example: BTCUSDT"),
    side: str = typer.Option(..., "--side", "-d", help="BUY or SELL"),
    order_type: str = typer.Option(
        ..., "--order-type", "-t", help="MARKET, LIMIT, STOP_MARKET"
    ),
    quantity: float = typer.Option(..., "--quantity", "-q", help="Order quantity"),
    price: Optional[float] = typer.Option(
        None,
        "--price",
        "-p",
        help="Required for LIMIT orders",
    ),
    stop_price: Optional[float] = typer.Option(
        None,
        "--stop-price",
        help="Required for STOP_MARKET orders",
    ),
) -> None:
    """Place a Futures order on Binance USDT-M Testnet."""
    configure_logging()

    console.print(
        Panel.fit(
            "[bold blue]Binance Futures Testnet Order Executor[/bold blue]",
            border_style="blue",
        )
    )

    try:
        validated_symbol = normalize_symbol(symbol)
        validated_side = validate_side(side)
        validated_order_type = validate_order_type(order_type)
        validated_quantity = validate_quantity(quantity)

        validated_price = validate_price(
            price,
            required=validated_order_type == OrderType.LIMIT,
            field_name="price",
        )
        validated_stop_price = validate_price(
            stop_price,
            required=validated_order_type == OrderType.STOP_MARKET,
            field_name="stop_price",
        )

        if validated_order_type != OrderType.LIMIT and price is not None:
            console.print("[yellow]Warning:[/yellow] --price is ignored for non-LIMIT orders.")
        if validated_order_type != OrderType.STOP_MARKET and stop_price is not None:
            console.print(
                "[yellow]Warning:[/yellow] --stop-price is ignored for non-STOP_MARKET orders."
            )

        client = BinanceFuturesTestnetClient.from_env()
        client.ping()
        exchange_info = client.exchange_info()
        validate_symbol_on_exchange(validated_symbol, exchange_info)

        order_request = OrderRequest(
            symbol=validated_symbol,
            side=validated_side,
            order_type=validated_order_type,
            quantity=validated_quantity,
            price=validated_price,
            stop_price=validated_stop_price,
        )

        _render_request_summary(order_request)

        order_service = OrderService(client)
        order_result = order_service.place_order(order_request)

        _render_order_response(order_result.raw_response)
        console.print(
            f"[bold green]Success:[/bold green] Order placed with ID {order_result.order_id}"
        )

    except ValidationError as exc:
        logger.exception("Validation error: %s", exc)
        console.print(f"[bold red]Validation Error:[/bold red] {exc}")
        raise typer.Exit(code=1)
    except BinanceAPIException as exc:
        logger.exception("Binance API error: %s", exc)
        console.print(
            f"[bold red]Binance API Error:[/bold red] code={exc.code}, message={exc.message}"
        )
        raise typer.Exit(code=1)
    except BinanceRequestException as exc:
        logger.exception("Binance request error: %s", exc)
        console.print(f"[bold red]Network/API Request Error:[/bold red] {exc}")
        raise typer.Exit(code=1)
    except requests.RequestException as exc:
        logger.exception("Network failure: %s", exc)
        console.print(f"[bold red]Network Failure:[/bold red] {exc}")
        raise typer.Exit(code=1)
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        console.print(f"[bold red]Unexpected Error:[/bold red] {exc}")
        raise typer.Exit(code=1)
    finally:
        console.print(f"[dim]Log file: {LOG_FILE_PATH}[/dim]")


if __name__ == "__main__":
    app()
