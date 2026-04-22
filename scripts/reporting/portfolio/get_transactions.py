"""Ledger-cli register (transactions) for given accounts."""

import os
import subprocess
from datetime import datetime
from typing import Optional

FIELD_SEP = "\x1f"


def _account_matches(acc: str, accounts: list[str]) -> bool:
    """True if acc is one of the requested accounts or a subaccount of one."""
    acc = acc.strip()
    for a in accounts:
        if acc == a or acc.startswith(a + ":"):
            return True
    return False


def _ledger_reg_args(
    ledger_file: str,
    accounts: list[str],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> list[str]:
    """Build argument list for ledger reg -B -X INR."""
    fmt = (
        f"%(format_date(date, '%Y-%m-%d')){FIELD_SEP}"
        f"%(account){FIELD_SEP}"
        f"%(scrub(display_amount))\n"
    )
    args = [
        "ledger", "-f", ledger_file, "-B", "-X", "INR",
        "reg", *accounts, "--format", fmt,
    ]
    if start_date:
        args.extend(["-b", start_date.strftime("%Y-%m-%d")])
    if end_date:
        args.extend(["-e", end_date.strftime("%Y-%m-%d")])
    return args


def _parse_register_line(line: str, accounts: list[str]) -> Optional[dict]:
    """Parse one ledger reg line (date, account, amount). Returns None if not 3 fields or account not in accounts."""
    parts = line.split(FIELD_SEP, 2)
    if len(parts) != 3:
        return None
    date_str, account_str, amount_str = parts
    account_str = account_str.strip()
    if not _account_matches(account_str, accounts):
        return None
    amount = amount_str.strip().removesuffix(" INR").strip()
    return {
        "date": date_str.strip(),
        "account": account_str,
        "amount": amount,
    }


def _parse_register_output(stdout: str, accounts: list[str]) -> list[dict]:
    """Parse ledger reg stdout into list of {date, account, amount} dicts."""
    out = (stdout or "").strip()
    if not out:
        return []
    rows = []
    for line in out.split("\n"):
        row = _parse_register_line(line, accounts)
        if row is not None:
            rows.append(row)
    return rows


def get_transactions(
    accounts: list[str],
    ledger_file: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> list[dict]:
    """Run ledger reg for given accounts. Returns [{date, account, amount}, ...]; amount is numeric only, INR."""
    if not accounts:
        return []

    path = ledger_file or os.environ.get("LEDGER_MAIN_FILE")
    if not path:
        raise ValueError("ledger_file must be passed or LEDGER_MAIN_FILE set")

    args = _ledger_reg_args(path, accounts, start_date, end_date)
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"ledger reg failed: {result.stderr or result.stdout or 'unknown error'}"
        )

    return _parse_register_output(result.stdout or "", accounts)


if __name__ == "__main__":
    ledger_file = os.environ.get("LEDGER_MAIN_FILE")
    accounts = ["Assets:MFs:Low-Volatility", "Assets:MFs:LargeMidCap"]
    transactions = get_transactions(
        accounts,
        ledger_file=ledger_file,
        start_date=datetime(2025, 4, 1),
        end_date=datetime(2026, 3, 31),
    )
    for t in transactions:
        print(t["date"], t["account"], t["amount"])
