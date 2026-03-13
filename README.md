# Binance Futures Testnet Trading Bot (Python)

A structured Python CLI application for placing **USDT-M Futures** orders on the **Binance Futures Testnet** using `python-binance`.

This project supports:
- `MARKET` orders
- `LIMIT` orders
- `STOP_MARKET` orders (bonus)
- `BUY` and `SELL` sides

It includes:
- layered architecture (client/API + order service + validators + CLI)
- robust error handling (validation, API, and network)
- Rich CLI output (tables, colored messages)
- file-based logging to `bot_activity.log`

## Project Structure

```text
trading_bot/
  bot/
    __init__.py
    client.py
    orders.py
    validators.py
    logging_config.py
  cli.py
  .env.example
  README.md
  requirements.txt
```

## Requirements

- Python 3.10+ (Python 3.x supported)
- Binance Futures Testnet account
- Binance Futures Testnet API key and secret

Base URL used for Futures API:
- `https://testnet.binancefuture.com`

## Setup

1. Clone or download this repository.
2. Create and activate a virtual environment.

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root.

```bash
cp .env.example .env
```

If you are on Windows PowerShell and `cp` is unavailable:

```powershell
Copy-Item .env.example .env
```

5. Edit `.env` and set your credentials:

```env
BINANCE_API_KEY=your_real_testnet_api_key
BINANCE_API_SECRET=your_real_testnet_api_secret
```

## Usage

Run the CLI:

```bash
python cli.py place --help
```

### 1) Place a MARKET order

```bash
python cli.py place --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001
```

### 2) Place a LIMIT order

```bash
python cli.py place --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 80000
```

### 3) Place a STOP_MARKET order

```bash
python cli.py place --symbol BTCUSDT --side SELL --order-type STOP_MARKET --quantity 0.001 --stop-price 60000
```

## Output Behavior

For each run, the CLI prints:
- order request summary
- order response details (`orderId`, `status`, `executedQty`, `avgPrice`)
- clear success/failure message

## Logging

All request/response/error activity is logged to:

- `bot_activity.log`

Examples of what gets logged:
- API call payloads for order placement
- API responses
- validation failures
- Binance API errors and network failures

## Exception Handling

The application handles and logs:
- invalid user input (`ValidationError`)
- `BinanceAPIException`
- `BinanceRequestException`
- network failures (`requests.RequestException`)
- unexpected exceptions (fallback safety)

## Assumptions

- only USDT-M Futures symbols are accepted (example: `BTCUSDT`)
- valid symbol check is performed against `futures_exchange_info`
- for `LIMIT`, `timeInForce` is set to `GTC`
- `--price` is required for `LIMIT`
- `--stop-price` is required for `STOP_MARKET`

## Assignment Log Artifacts

To produce the required log artifacts:
1. Run one successful `MARKET` order command.
2. Run one successful `LIMIT` order command.
3. Submit generated `bot_activity.log` (or a copy) with your assignment.
