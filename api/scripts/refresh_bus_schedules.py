"""Fetch every PDF linked by the official Çanakkale bus schedule page."""

import argparse
import json
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


SOURCE_URL = "https://ulasim.canakkale.bel.tr/rehber/hatlar-otobus-saatleri/"
SOURCE_HOST = "ulasim.canakkale.bel.tr"
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "data" / "bus_schedules"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36", "Accept": "text/html,application/pdf,*/*"}


def slugify(value: str) -> str:
    value = value.lower().replace("ı", "i").replace("ğ", "g").replace("ü", "u")
    value = value.replace("ş", "s").replace("ö", "o").replace("ç", "c")
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")[:72] or "bus-schedule"


def collect_links(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    seen = set()
    for anchor in soup.find_all("a", href=True):
        url = urljoin(SOURCE_URL, anchor["href"])
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != SOURCE_HOST or not parsed.path.lower().endswith(".pdf"):
            continue
        if url in seen:
            continue
        seen.add(url)
        label = " ".join(anchor.get_text(" ", strip=True).split())
        if not label:
            label = Path(parsed.path).stem.replace("-", " ")
        links.append({"url": url, "label": label})
    if not links:
        raise RuntimeError("No official schedule PDFs were found on the source page")
    return links


def download_pdf(session: requests.Session, url: str, destination: Path) -> int:
    with session.get(url, headers={**HEADERS, "Referer": SOURCE_URL}, timeout=(5, 20), stream=True) as response:
        response.raise_for_status()
        if urlparse(response.url).hostname != SOURCE_HOST:
            raise RuntimeError(f"PDF redirected away from official host: {response.url}")
        if "application/pdf" not in response.headers.get("Content-Type", "").lower():
            raise RuntimeError(f"Source did not return a PDF: {url}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        size = 0
        with destination.open("wb") as output:
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if chunk:
                    if size == 0 and not chunk.startswith(b"%PDF-"):
                        raise RuntimeError(f"Invalid PDF signature: {url}")
                    size += len(chunk)
                    if size > 30 * 1024 * 1024:
                        raise RuntimeError(f"PDF is larger than 30 MB: {url}")
                    output.write(chunk)
    return size


def main() -> None:
    parser = argparse.ArgumentParser(description="Download all bus schedule PDFs from the official source page")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with requests.Session() as session:
        page = session.get(SOURCE_URL, headers=HEADERS, timeout=(5, 20))
        page.raise_for_status()
        if urlparse(page.url).hostname != SOURCE_HOST:
            raise RuntimeError(f"Schedule page redirected away from official host: {page.url}")
        pdfs = collect_links(page.text)

        for index, pdf in enumerate(pdfs, start=1):
            filename = f"{index:02d}-{slugify(pdf['label'])}.pdf"
            destination = args.output_dir / filename
            with tempfile.NamedTemporaryFile(dir=args.output_dir, suffix=".pdf", delete=False) as temp_file:
                temp_path = Path(temp_file.name)
            try:
                size = download_pdf(session, pdf["url"], temp_path)
                temp_path.replace(destination)
            finally:
                temp_path.unlink(missing_ok=True)
            pdf["filename"] = filename
            pdf["size_bytes"] = size
            print(f"Downloaded {pdf['label']}: {filename} ({size:,} bytes)")

    metadata = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source_url": SOURCE_URL,
        "pdfs": pdfs,
    }
    (args.output_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = [f"Fetched at: {metadata['fetched_at']}", f"Source: {SOURCE_URL}", "", "PDFs:"]
    summary.extend(f"- {pdf['label']} | {pdf['filename']} | {pdf['url']}" for pdf in pdfs)
    (args.output_dir / "metadata.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(f"Updated metadata for {len(pdfs)} official PDFs in {args.output_dir}")


if __name__ == "__main__":
    main()
