"""Download the EX-10 contracts attached to a month of SEC 8-K filings.

    python edgar.py 2026-11

Writes one file per filing day to data/exhibits/, newest day first. Days already on
disk are skipped, so running the command again resumes an interrupted download.
"""

import json
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit

import httpx
from bs4 import BeautifulSoup

ARCHIVES = "https://www.sec.gov/Archives/"
CONTACT = "ZazenCodes SEC research alex@zazencodes.com"
EXHIBIT_TYPE = re.compile(r"EX-10(?:\.\d+)*", re.IGNORECASE)
EXHIBITS = Path(__file__).with_name("data") / "exhibits"
CLOSED = {date(2026, 11, 11), date(2026, 11, 26)}  # Veterans Day and Thanksgiving: EDGAR takes no filings.
PACE = 0.125  # Seconds between requests: 8 a second, under the SEC's published limit of 10.
WORKERS = 8  # Filings read at the same time. PACE still spaces out every request.

_gate = threading.Lock()
_next_start = 0.0


def fetch(client, url):
    global _next_start
    with _gate:
        start = max(_next_start, time.monotonic())
        _next_start = start + PACE
    time.sleep(max(0.0, start - time.monotonic()))
    return client.get(url).raise_for_status().text


def fetch_filing(client, filing) -> list[dict]:
    cik, company, _, _, path = filing
    accession = path.rsplit("/", 1)[1].removesuffix(".txt")
    filing_url = f"{ARCHIVES}edgar/data/{cik}/{accession.replace('-', '')}/{accession}-index.htm"
    manifest = BeautifulSoup(fetch(client, filing_url), "html.parser")
    exhibits = []
    for row in manifest.select("table.tableFile tr"):
        cells = row.find_all("td")
        if len(cells) < 4 or not EXHIBIT_TYPE.fullmatch(cells[3].get_text(strip=True)):
            continue
        link = cells[2].find("a", href=True)
        if not link:
            continue
        href = link["href"]
        parts = urlsplit(href)
        if parts.path in {"/ix", "/ixviewer/doc/action"}:
            href = parse_qs(parts.query)["doc"][0]
        url = urljoin(filing_url, href)
        if not url.startswith(ARCHIVES) or not url.lower().endswith((".htm", ".html", ".txt")):
            continue
        page = BeautifulSoup(fetch(client, url), "html.parser")
        for tag in page.find_all(["style", "script", "ix:header"]):
            tag.decompose()
        text = " ".join(page.get_text(" ", strip=True).split())
        # Keep complete machine-readable exhibits that fit the stage workload.
        if not 500 <= len(text.encode()) <= 55_000:
            continue
        exhibits.append({"title": company, "text": text, "url": url})
    return exhibits


def fetch_day(client, filed_on: date) -> list[dict]:
    quarter = (filed_on.month - 1) // 3 + 1
    index_url = f"{ARCHIVES}edgar/daily-index/{filed_on.year}/QTR{quarter}/master.{filed_on:%Y%m%d}.idx"
    filings = [line.split("|") for line in fetch(client, index_url).splitlines() if "|8-K|" in line]
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        found = [exhibit for exhibits in pool.map(lambda filing: fetch_filing(client, filing), filings) for exhibit in exhibits]
    return [
        {"id": f"{filed_on:%m%d}-{number:03d}", "filed": filed_on.isoformat(), **exhibit}
        for number, exhibit in enumerate(found, 1)
    ]


def download_month(month: str) -> None:
    year, number = map(int, month.split("-"))
    days = [date(year, number, 1) + timedelta(days=offset) for offset in range(31)]
    days = [day for day in days if day.month == number and day.weekday() < 5 and day < date.today() and day not in CLOSED]
    EXHIBITS.mkdir(parents=True, exist_ok=True)
    with httpx.Client(headers={"User-Agent": CONTACT}, timeout=8, follow_redirects=True) as client:
        for day in reversed(days):
            target = EXHIBITS / f"{day}.jsonl"
            if target.exists():
                continue
            exhibits = fetch_day(client, day)
            partial = target.with_suffix(".part")
            partial.write_text("".join(json.dumps(exhibit, ensure_ascii=False) + "\n" for exhibit in exhibits))
            partial.rename(target)
            print(f"{day}: {len(exhibits)} contracts", flush=True)


if __name__ == "__main__":
    download_month(sys.argv[1])
