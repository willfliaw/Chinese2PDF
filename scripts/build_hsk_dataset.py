"""
HSK vocabulary dataset builder for multiple levels (fetch all pages).

Usage:
    python build_hsk_dataset.py --out hsk_words.csv
    python build_hsk_dataset.py --levels 1 2 3 --out hsk123.csv
    python build_hsk_dataset.py --levels 4 5 --out hsk45.csv --page-size 200

Output CSV columns:
    level, hanzi, pinyin, english
"""

import argparse
import json
import math
import sys
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm

API_URL = "https://api.hskmock.com/mock/word/searchWords"


def build_session() -> requests.Session:
    """Create a requests session with retries and default headers."""
    s = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=["POST"],
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.headers.update({"Content-Type": "application/json"})
    return s


def fetch_page(
    session: requests.Session, level_id: int, page_num: int, page_size: int
) -> Dict[str, Any]:
    """Fetch one page of words for a given HSK level."""
    payload = {
        "level_ids": [level_id],
        "page_num": page_num,
        "page_size": page_size,
    }
    resp = session.post(API_URL, data=json.dumps(payload), timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
    return resp.json()


def extract_items_and_total(
    data: Dict[str, Any],
) -> (List[Dict[str, Any]], Optional[int]):
    """Extract the list of words and total count from API response."""
    container = data.get("data") or {}
    items = container.get("list") or []
    total = container.get("level_count") or None
    return items, total


def normalize_item(level: int, item: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a raw API item into a clean dictionary row."""
    field_map = {
        "hanzi": "word",
        "pinyin": "pinyin",
        "pinyin_tone": "pinyin_tone",
        "pinyin_num": "pinyin_num",
        "english": "translation",
        "pos": "syntax",
        "tts_url": "tts_url",
    }

    row = {"level": level}
    for key, source in field_map.items():
        val = item.get(source)
        if isinstance(val, str):
            val = val.strip()
        row[key] = val
    return row


def collect_level(
    level_id: int, session: requests.Session, page_size: int
) -> List[Dict[str, Any]]:
    """Download all pages of words for one HSK level."""
    rows: List[Dict[str, Any]] = []

    first = fetch_page(session, level_id, page_num=1, page_size=page_size)
    first_items, total = extract_items_and_total(first)

    if not isinstance(total, int) or total <= 0:
        raise ValueError(f"Invalid total for HSK{level_id}: {total!r}")
    pages = max(1, math.ceil(total / page_size))

    for it in first_items:
        rows.append(normalize_item(level_id, it))

    with tqdm(total=pages, initial=1, desc=f"HSK{level_id}", unit="page") as pbar:
        for page_num in range(2, pages + 1):
            data = fetch_page(session, level_id, page_num, page_size)
            items, _ = extract_items_and_total(data)
            for it in items:
                rows.append(normalize_item(level_id, it))
            pbar.update(1)

    return rows


def parse_args():
    """Parse command-line arguments for levels, output file, and page size."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--levels",
        nargs="+",
        type=int,
        default=[1, 2, 3, 4, 5, 6],
        help="HSK levels to fetch (default: all 1-6)",
    )
    parser.add_argument(
        "--out",
        type=str,
        required=True,
        help="Output CSV filename",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=100,
        help="Number of words per page (default: 100)",
    )
    return parser.parse_args()


def main():
    """Fetch HSK words for given levels and save them into a CSV file."""
    args = parse_args()
    session = build_session()
    all_rows: List[Dict[str, Any]] = []

    for level in args.levels:
        all_rows.extend(collect_level(level, session, args.page_size))

    if not all_rows:
        print("No data collected. Check token or headers.", file=sys.stderr)
        sys.exit(1)

    df = pd.DataFrame(all_rows).drop_duplicates().reset_index(drop=True)
    df.to_csv(args.out, index=False)
    print(f"Saved {len(df)} rows across levels {args.levels} to {args.out}")


if __name__ == "__main__":
    main()
