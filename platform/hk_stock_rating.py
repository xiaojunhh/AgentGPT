"""Simple Hong Kong stock rating system prototype."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests

API_ENDPOINT = "https://query1.finance.yahoo.com/v7/finance/quote"
HKEX_LISTING_URL = "https://example.com/hkex/listing"  # placeholder


@dataclass
class StockData:
    """Container for stock information used for rating."""

    symbol: str
    name: str
    industry: Optional[str]
    fundamentals: Dict[str, float]
    market_sentiment: float


@dataclass
class Rating:
    total: float
    details: Dict[str, float]


WEIGHTS: Dict[str, float] = {
    "fundamentals": 0.30,
    "industry_outlook": 0.20,
    "underwriters_sentiment": 0.15,
    "innovation": 0.15,
    "investor_feedback": 0.10,
    "ipo_pricing": 0.10,
}


def fetch_stock_data(symbol_or_name: str) -> StockData:
    """Fetch stock data from Yahoo Finance.

    Note: This function uses a public API and may require additional error
    handling for production use.
    """
    params = {"symbols": symbol_or_name}
    resp = requests.get(API_ENDPOINT, params=params, timeout=10)
    resp.raise_for_status()
    result = resp.json()["quoteResponse"]["result"][0]
    return StockData(
        symbol=result.get("symbol", symbol_or_name),
        name=result.get("longName", result.get("shortName", symbol_or_name)),
        industry=result.get("industry"),
        fundamentals={
            "eps": result.get("epsTrailingTwelveMonths", 0.0),
            "pe_ratio": result.get("trailingPE", 0.0),
        },
        market_sentiment=result.get("regularMarketChangePercent", 0.0),
    )


def calculate_score(data: StockData) -> Rating:
    """Calculate a rating out of 10 based on weighted dimensions."""
    fundamentals_score = min(max(data.fundamentals.get("pe_ratio", 0.0), 0.0), 50.0)
    fundamentals_score = 10.0 - fundamentals_score / 50.0 * 10.0

    industry_outlook_score = 6.0  # placeholder logic
    underwriter_score = 7.0  # placeholder
    innovation_score = 6.5  # placeholder
    investor_feedback_score = max(min(data.market_sentiment, 10.0), 0.0)
    ipo_pricing_score = 6.0  # placeholder

    details = {
        "fundamentals": fundamentals_score,
        "industry_outlook": industry_outlook_score,
        "underwriters_sentiment": underwriter_score,
        "innovation": innovation_score,
        "investor_feedback": investor_feedback_score,
        "ipo_pricing": ipo_pricing_score,
    }

    total = sum(details[k] * WEIGHTS[k] for k in WEIGHTS)
    return Rating(total=round(total, 2), details=details)


def fetch_recent_listings() -> List[str]:
    """Return recent listing submissions in the last two weeks.

    This is a placeholder that should call the HKEX API.
    """
    # Example: pretend we fetched this data
    today = datetime.utcnow().date()
    companies = [
        (today - timedelta(days=i), f"Company {i}")
        for i in range(1, 10)
    ]
    return [name for date, name in companies if (today - date).days <= 14]


def get_stock_rating(symbol_or_name: str) -> Rating:
    data = fetch_stock_data(symbol_or_name)
    return calculate_score(data)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HK Stock Rating")
    parser.add_argument("query", help="Stock symbol or name")
    args = parser.parse_args()

    rating = get_stock_rating(args.query)
    print(f"Rating for {args.query}: {rating.total}/10")
    for k, v in rating.details.items():
        print(f"  {k}: {v}")

    print("\nRecent listing submissions:")
    for name in fetch_recent_listings():
        print(f" - {name}")
