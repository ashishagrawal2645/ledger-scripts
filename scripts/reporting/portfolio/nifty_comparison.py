#!/usr/bin/env python3
"""Nifty vs portfolio comparison (to be built step by step)."""

import argparse
import csv
import os
import sys
import tempfile
from datetime import datetime
from decimal import Decimal
from typing import Optional

from babel.numbers import format_currency

# Run from repo root: python scripts/reporting/portfolio/nifty_comparison.py
_script_dir = os.path.dirname(os.path.abspath(__file__))
_reporting_dir = os.path.join(_script_dir, "..")
_investments_dir = os.path.join(_reporting_dir, "investments")
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)
if _reporting_dir not in sys.path:
    sys.path.insert(0, _reporting_dir)
if _investments_dir not in sys.path:
    sys.path.insert(0, _investments_dir)

from get_transactions import get_transactions
from investments.configs import (
    configs as date_configs,
    main_ledger_file,
    prices_db,
)
from investments.utils import (
    TOTAL_VALUE,
    chart_builder,
    get_month_range,
    get_register_report,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NIFTY_CSV_PATH = os.path.join(_script_dir, "nifty_historical_prices.csv")
CSV_DATE_FMT = "%d-%b-%Y"  # e.g. 01-APR-2024
TMP_LEDGER_PREFIX = "nifty_benchmark_"
TMP_LEDGER_SUFFIX = ".ledger"
TMP_DIR = "/tmp"
PLOT_NAME = "/tmp/nifty_comparison.png"
BENCHMARK_ACCOUNTS = "Equity:MFs:Benchmark"

# ---------------------------------------------------------------------------
# Report configs: label -> { "accounts": [...], "date_config": key in date_configs }
# date_configs (from investments.configs) provide start_date / end_date.
# ---------------------------------------------------------------------------

NIFTY_CONFIGS = {
    "CORE_MF_LEVEL": {
        "accounts": [
            "Assets:MFs:Low-Volatility",
            "Assets:Sejal:MFs:Kotak-Low-Volatility",
            "Assets:MFs:LargeMidCap",
            "Assets:Sejal:MFs:Zerodha-LargeMidCap",
            "Assets:MFs:Midcap-Momentum",
            "Assets:Sejal:MFs:Kotak-Midcap-Momentum",
        ],
        "date_config": "REAL_TTM",
    },
    "CORE_PORTFOLIO": {
        "accounts": [
            "Assets:MFs",
            "Assets:Sejal:MFs",
            "Assets:Sejal:SIF:Altiva",
            "Assets:Sejal:SIF:Isif",
            "Assets:NPS:Equity",
            "Assets:Zerodha:Kite:MFs:NASDAQ",
            "Assets:INDMoney:ETF",
            "Assets:PF",
            "Assets:Sbi:PPF",
            "Assets:NPS:Corp-Debt",
            "Assets:NPS:Govt-Bonds",
            "Assets:Sejal:SIF:MOS-Arbitrate",
        ],
        "date_config": "INCEPTION",
    },
}


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Build and parse command-line arguments. Use either --config or (--accounts + --start + --end)."""
    parser = argparse.ArgumentParser(
        description="Nifty vs portfolio comparison. Use a named config or pass accounts and date range."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--config",
        type=str,
        choices=list(NIFTY_CONFIGS.keys()),
        help="Named config (accounts + date range from investments.configs)",
    )
    group.add_argument(
        "--accounts",
        nargs="+",
        help="Ledger accounts (e.g. Assets:MFs:Low-Volatility); requires --start and --end",
    )
    parser.add_argument(
        "--start",
        metavar="YYYY-MM-DD",
        help="Start date (required when using --accounts)",
    )
    parser.add_argument(
        "--end",
        metavar="YYYY-MM-DD",
        help="End date (required when using --accounts)",
    )
    parser.add_argument(
        "--ledger-file",
        default=os.environ.get("LEDGER_MAIN_FILE"),
        help="Ledger file (default: LEDGER_MAIN_FILE)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress plot display",
    )
    args = parser.parse_args(argv)
    if args.accounts and (args.start is None or args.end is None):
        parser.error("--accounts requires both --start and --end")
    return args


# ---------------------------------------------------------------------------
# Report / data helpers
# ---------------------------------------------------------------------------


def build_report(month_range, reports, field):
    """Align multiple reports by month key; return (data_dict, latest_values). Same as mf_performance."""
    data = {}
    latest_value = []
    desired_length = len(reports)
    for key in month_range:
        value = []
        for report in reports:
            if key in report:
                value.append(report[key][field])
        if len(value) == desired_length:
            data[key] = value
            latest_value = value
    return (data, latest_value)


def _parse_csv_date(date_str: str) -> Optional[datetime]:
    """Parse CSV date (e.g. 01-APR-2024). Returns datetime or None."""
    try:
        return datetime.strptime(date_str.strip(), CSV_DATE_FMT)
    except ValueError:
        return None


def load_nifty_prices_from_csv(
    start_date: datetime,
    end_date: datetime,
) -> list[tuple[str, str]]:
    """
    Read Nifty 50 historical close prices from CSV for the given date range.

    Returns list of (date_str, close_price_str) for dates where
    start_date <= date <= end_date.
    """
    if not os.path.exists(NIFTY_CSV_PATH):
        return []
    result = []
    with open(NIFTY_CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_str = (row.get("date") or "").strip()
            close_str = (row.get("close_price") or "").strip()
            if not date_str or not close_str:
                continue
            dt = _parse_csv_date(date_str)
            if dt is None:
                continue
            d = dt.date()
            if start_date.date() <= d <= end_date.date():
                result.append((date_str, close_str))
    return result


def load_nifty_price_by_date_from_csv() -> dict[str, str]:
    """
    Load full CSV into a dict mapping date (YYYY-MM-DD) to close_price string.
    Used for looking up Nifty price on specific transaction dates.
    """
    out = {}
    if not os.path.exists(NIFTY_CSV_PATH):
        return out
    with open(NIFTY_CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_str = (row.get("date") or "").strip()
            close_str = (row.get("close_price") or "").strip()
            if not date_str or not close_str:
                continue
            dt = _parse_csv_date(date_str)
            if dt is not None:
                key = dt.strftime("%Y-%m-%d")
                out[key] = close_str
    return out


def run(
    accounts: list[str],
    start_date: datetime,
    end_date: datetime,
    ledger_file: Optional[str] = None,
) -> list[dict]:
    """
    Fetch transactions for the given accounts and attach Nifty 50 close price
    for each transaction date from the CSV (only for dates with a transaction).

    Returns list of dicts with keys: date, account, account_invested_amount,
    nifty price of the day.
    """
    ledger_file = ledger_file or os.environ.get("LEDGER_MAIN_FILE")
    if not ledger_file:
        raise ValueError("ledger_file must be passed or LEDGER_MAIN_FILE set")

    transactions = get_transactions(
        accounts,
        ledger_file=ledger_file,
        start_date=start_date,
        end_date=end_date,
    )

    nifty_by_date = load_nifty_price_by_date_from_csv()

    rows = []
    for t in transactions:
        date_str = t["date"]
        nifty_price = nifty_by_date.get(date_str, "")
        rows.append({
            "date": date_str,
            "account": t["account"],
            "account_invested_amount": t["amount"],
            "nifty price of the day": nifty_price,
        })
    return rows


def rows_to_ledger_file(rows: list[dict]) -> str:
    """
    Write the constructed rows to a temporary ledger file in /tmp/ in the
    format of benchmark-sip.ledger. Returns the absolute path of the created file.

    Only includes entries for rows that have a non-empty nifty price of the day.
    Ledger format per entry:
      YYYY/MM/DD Benchmark investment
        Equity:MFs:Benchmark  <qty> NIFTY {<price> INR} @ <price> INR
        Equity:Accounting  -<amount> INR
        Equity:Adjustments  <adjustment> INR
    """
    fd, path = tempfile.mkstemp(
        prefix=TMP_LEDGER_PREFIX,
        suffix=TMP_LEDGER_SUFFIX,
        dir=TMP_DIR,
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            for r in rows:
                nifty_str = (r.get("nifty price of the day") or "").strip()
                if not nifty_str:
                    continue
                try:
                    amount = abs(Decimal(r["account_invested_amount"]))
                    price = Decimal(nifty_str)
                except Exception:
                    continue
                if price <= 0:
                    continue
                date_ledger = r["date"].replace("-", "/")
                quantity = amount / price
                quantity_rounded = round(quantity, 3)
                adjustment = amount - (quantity_rounded * price)
                adjustment_rounded = round(adjustment, 2)
                amount_str = f"{amount:.2f}"
                price_str = f"{price:.2f}"
                qty_str = f"{quantity_rounded:.3f}"
                adj_str = f"{adjustment_rounded:.2f}"
                f.write(f"{date_ledger} Benchmark investment\n")
                f.write(
                    f"\tEquity:MFs:Benchmark    {qty_str} NIFTY {{{price_str} INR}} @ {price_str} INR\n"
                )
                f.write(f"\tEquity:Accounting      -{amount_str} INR\n")
                f.write(f"\tEquity:Adjustments     {adj_str} INR\n")
                f.write("\n")
    except Exception:
        try:
            os.unlink(path)
        except OSError:
            pass
        raise
    return os.path.abspath(path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    args = parse_args()

    if args.config:
        cfg = NIFTY_CONFIGS[args.config]
        accounts = cfg["accounts"]
        date_cfg = date_configs[cfg["date_config"]]
        start_date = date_cfg["start_date"]
        end_date = date_cfg["end_date"]
    else:
        accounts = args.accounts
        start_date = datetime.strptime(args.start, "%Y-%m-%d")
        end_date = datetime.strptime(args.end, "%Y-%m-%d")

    main_ledger = args.ledger_file or main_ledger_file
    if not main_ledger:
        raise ValueError("ledger_file must be passed or LEDGER_MAIN_FILE set")

    rows = run(
        accounts=accounts,
        start_date=start_date,
        end_date=end_date,
        ledger_file=main_ledger,
    )

    ledger_path = rows_to_ledger_file(rows)

    month_range = get_month_range(start_date, end_date)
    investment_report = get_register_report(
        ledger_file=main_ledger,
        accounts=" ".join(accounts),
        start_date=start_date,
        end_date=end_date,
        prices_db=prices_db,
    )
    benchmark_report = get_register_report(
        ledger_file=ledger_path,
        accounts=BENCHMARK_ACCOUNTS,
        start_date=start_date,
        end_date=end_date,
        prices_db=prices_db,
    )
    final_report, latest_values = build_report(
        month_range, [investment_report, benchmark_report], TOTAL_VALUE
    )
    plot_file = chart_builder(
        final_report, "time", "amount", ["Investment", "Benchmark"], PLOT_NAME
    )

    if not args.quiet:
        os.system("~/.iterm2/imgcat -W 95% -H 95% {}".format(plot_file))
    if latest_values:
        gains = (latest_values[0] - latest_values[1]) / 100000
        print("Gains over benchmark: " + format_currency(gains, "INR", locale="en_IN") + " lacs")


if __name__ == "__main__":
    main()
