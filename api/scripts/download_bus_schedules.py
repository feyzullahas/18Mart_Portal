"""
Bus Schedule PDF Downloader
Scrapes and downloads the latest bus schedule PDFs from Çanakkale Municipality website.
Downloads both weekday and weekend schedules with support for:
- Overwriting existing files (default)
- Timestamped filenames for archival
- Retry logic for reliability
- Enhanced detection for newest schedules
"""

import os
import sys
import re
import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import logging
import time
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Try to import notification config
try:
    import notification_config as config
    NOTIFICATION_ENABLED = True
except ImportError:
    config = None
    NOTIFICATION_ENABLED = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "https://ulasim.canakkale.bel.tr/rehber/hatlar-otobus-saatleri/"
DOWNLOAD_DIR = Path(__file__).parent.parent / "data" / "bus_schedules"
TIMEOUT = 30  # seconds
MAX_RETRIES = 3  # Number of retry attempts
RETRY_DELAY = 5  # seconds between retries

# Turkish month names for date detection
TURKISH_MONTHS = [
    'OCAK', 'ŞUBAT', 'MART', 'NİSAN', 'MAYIS', 'HAZİRAN',
    'TEMMUZ', 'AĞUSTOS', 'EYLÜL', 'EKİM', 'KASIM', 'ARALIK'
]

# Ensure download directory exists
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_headers() -> dict:
    """Return HTTP headers for requests."""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    }


def fetch_with_retry(url: str, stream: bool = False) -> requests.Response:
    """
    Fetch URL content with retry logic.
    
    Args:
        url: The URL to fetch
        stream: Whether to stream the response
        
    Returns:
        Response object
        
    Raises:
        requests.RequestException: If all retries fail
    """
    last_exception = None
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Fetching {url} (attempt {attempt}/{MAX_RETRIES})")
            response = requests.get(
                url, 
                headers=get_headers(), 
                timeout=TIMEOUT,
                stream=stream
            )
            response.raise_for_status()
            return response
            
        except requests.RequestException as e:
            last_exception = e
            logger.warning(f"Attempt {attempt} failed: {str(e)}")
            
            if attempt < MAX_RETRIES:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
    
    raise last_exception


def fetch_page_content(url: str) -> str:
    """
    Fetch the HTML content of the given URL.
    
    Args:
        url: The URL to fetch
        
    Returns:
        HTML content as string
        
    Raises:
        requests.RequestException: If the request fails
    """
    logger.info(f"Fetching page content from {url}")
    response = fetch_with_retry(url)
    logger.info("Page content fetched successfully")
    return response.text


def has_date_indicator(text: str) -> bool:
    """
    Check if text contains date indicators (day numbers or month names).
    This helps identify "newer" schedule announcements.
    
    Args:
        text: The text to check
        
    Returns:
        True if text contains date indicators
    """
    # Check for day numbers (e.g., "20 OCAK", "15 EYLÜL")
    if re.search(r'\b\d{1,2}\s+(' + '|'.join(TURKISH_MONTHS) + r')\b', text.upper()):
        return True
    
    # Check for "İTİBARİYLE" which means "as of" or "starting from"
    if 'İTİBARİYLE' in text.upper() or 'ITIBARIYLE' in text.upper():
        return True
    
    return False


def extract_pdf_links(html_content: str) -> dict:
    """
    Extract PDF links from the HTML content.
    Prioritizes links with date indicators as they are typically the newest schedules.
    
    Args:
        html_content: HTML content as string
        
    Returns:
        Dictionary with 'weekday', 'weekend', and 'all_weekday' PDF URLs
    """
    logger.info("Parsing HTML content to extract PDF links")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    pdf_links = {
        'weekday': None,
        'weekend': None,
        'all_weekday': [],  # Store all weekday links for reference
        'all_weekend': [],  # Store all weekend links for reference
    }
    
    # Find all links that end with .pdf
    all_links = soup.find_all('a', href=lambda href: href and href.lower().endswith('.pdf'))
    
    logger.info(f"Found {len(all_links)} PDF links total")
    
    weekday_candidates = []
    weekend_candidates = []
    
    for link in all_links:
        href = link.get('href')
        text = link.get_text(strip=True).upper()
        
        logger.debug(f"Processing link: {text} -> {href}")
        
        # Check for weekday schedules
        if 'HAFTA İÇİ' in text or 'HAFTA IÇI' in text or 'WEEKDAY' in text:
            has_date = has_date_indicator(text)
            weekday_candidates.append({
                'href': href,
                'text': text,
                'has_date': has_date
            })
            pdf_links['all_weekday'].append({'href': href, 'text': text})
            logger.info(f"Found weekday schedule: {text[:50]}... (has_date={has_date})")
        
        # Check for weekend schedules
        elif 'HAFTA SONU' in text or 'WEEKEND' in text:
            has_date = has_date_indicator(text)
            weekend_candidates.append({
                'href': href,
                'text': text,
                'has_date': has_date
            })
            pdf_links['all_weekend'].append({'href': href, 'text': text})
            logger.info(f"Found weekend schedule: {text[:50]}... (has_date={has_date})")
    
    # Select the best weekday schedule (prefer ones with dates as they're usually newer)
    if weekday_candidates:
        # First, try to find one with a date indicator
        dated_weekday = [c for c in weekday_candidates if c['has_date']]
        if dated_weekday:
            # Take the last dated one (usually the newest)
            pdf_links['weekday'] = dated_weekday[-1]['href']
            logger.info(f"Selected dated weekday schedule: {dated_weekday[-1]['text'][:50]}...")
        else:
            # Fall back to the last found
            pdf_links['weekday'] = weekday_candidates[-1]['href']
            logger.info(f"Selected weekday schedule: {weekday_candidates[-1]['text'][:50]}...")
    
    # Select the best weekend schedule
    if weekend_candidates:
        dated_weekend = [c for c in weekend_candidates if c['has_date']]
        if dated_weekend:
            pdf_links['weekend'] = dated_weekend[-1]['href']
            logger.info(f"Selected dated weekend schedule: {dated_weekend[-1]['text'][:50]}...")
        else:
            pdf_links['weekend'] = weekend_candidates[-1]['href']
            logger.info(f"Selected weekend schedule: {weekend_candidates[-1]['text'][:50]}...")
    
    return pdf_links


def check_if_pdf_changed(url: str, filename: str) -> tuple[bool, int]:
    """
    Check if the PDF at the URL has changed compared to the local file.
    
    Args:
        url: URL of the PDF file
        filename: Local filename to compare against
        
    Returns:
        Tuple of (has_changed, remote_size)
    """
    filepath = DOWNLOAD_DIR / filename
    
    try:
        # Get remote file size without downloading
        response = requests.head(url, headers=get_headers(), timeout=TIMEOUT)
        remote_size = int(response.headers.get('Content-Length', 0))
        
        # If local file doesn't exist, it has "changed"
        if not filepath.exists():
            logger.info(f"Local file {filename} doesn't exist, will download")
            return True, remote_size
        
        # Compare file sizes
        local_size = filepath.stat().st_size
        
        if local_size != remote_size:
            logger.info(f"File size changed: {local_size:,} -> {remote_size:,} bytes")
            return True, remote_size
        else:
            logger.info(f"File {filename} unchanged ({local_size:,} bytes)")
            return False, remote_size
            
    except Exception as e:
        logger.warning(f"Could not check if file changed: {str(e)}, will download anyway")
        return True, 0


def download_pdf(url: str, filename: str, force: bool = False) -> bool:
    """
    Download a PDF file from the given URL with retry logic.
    
    Args:
        url: URL of the PDF file
        filename: Name to save the file as
        force: Force download even if file hasn't changed
        
    Returns:
        True if download was successful, False otherwise
    """
    filepath = DOWNLOAD_DIR / filename
    
    try:
        # Check if file has changed (unless forced)
        if not force:
            has_changed, remote_size = check_if_pdf_changed(url, filename)
            if not has_changed:
                logger.info(f"Skipping download of {filename} (no changes detected)")
                return True  # Return True because the file is up-to-date
        
        logger.info(f"Downloading PDF from {url}")
        response = fetch_with_retry(url, stream=True)
        
        # Write the PDF content to file
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = filepath.stat().st_size
        
        # Validate PDF file
        if file_size < 1000:  # Less than 1KB is suspicious
            logger.warning(f"Downloaded file seems too small ({file_size} bytes)")
        
        logger.info(f"Successfully downloaded {filename} ({file_size:,} bytes)")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download {filename}: {str(e)}")
        return False


def update_metadata(pdf_links: dict, download_status: dict, use_timestamp: bool = False):
    """
    Update metadata file with download information.
    Creates both a human-readable text file and a JSON file for programmatic access.
    
    Args:
        pdf_links: Dictionary of PDF links
        download_status: Dictionary of download success status
        use_timestamp: Whether timestamped filenames were used
    """
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime('%Y%m%d') if use_timestamp else None
    
    # Text metadata
    metadata_file = DOWNLOAD_DIR / "metadata.txt"
    try:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write(f"Last Updated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source URL: {BASE_URL}\n")
            f.write(f"Timestamped Mode: {use_timestamp}\n\n")
            
            f.write("Downloaded Files:\n")
            if download_status.get('weekday'):
                weekday_file = f"canakkale_bus_weekday_{timestamp_str}.pdf" if use_timestamp else "canakkale_bus_weekday_latest.pdf"
                f.write(f"  - Weekday Schedule: {weekday_file}\n")
                f.write(f"    Source: {pdf_links['weekday']}\n")
            
            if download_status.get('weekend'):
                weekend_file = f"canakkale_bus_weekend_{timestamp_str}.pdf" if use_timestamp else "canakkale_bus_weekend_latest.pdf"
                f.write(f"  - Weekend Schedule: {weekend_file}\n")
                f.write(f"    Source: {pdf_links['weekend']}\n")
            
            # Log all found links for debugging
            if pdf_links.get('all_weekday'):
                f.write("\nAll Weekday Links Found:\n")
                for link in pdf_links['all_weekday']:
                    f.write(f"  - {link['text'][:60]}\n")
                    f.write(f"    {link['href']}\n")
            
            if pdf_links.get('all_weekend'):
                f.write("\nAll Weekend Links Found:\n")
                for link in pdf_links['all_weekend']:
                    f.write(f"  - {link['text'][:60]}\n")
                    f.write(f"    {link['href']}\n")
        
        logger.info("Text metadata file updated successfully")
        
    except Exception as e:
        logger.error(f"Failed to update text metadata: {str(e)}")
    
    # JSON metadata for programmatic access
    json_metadata_file = DOWNLOAD_DIR / "metadata.json"
    try:
        metadata_json = {
            'last_updated': timestamp.isoformat(),
            'source_url': BASE_URL,
            'timestamped_mode': use_timestamp,
            'files': {
                'weekday': {
                    'filename': f"canakkale_bus_weekday_{timestamp_str}.pdf" if use_timestamp else "canakkale_bus_weekday_latest.pdf",
                    'source': pdf_links.get('weekday'),
                    'downloaded': download_status.get('weekday', False)
                },
                'weekend': {
                    'filename': f"canakkale_bus_weekend_{timestamp_str}.pdf" if use_timestamp else "canakkale_bus_weekend_latest.pdf",
                    'source': pdf_links.get('weekend'),
                    'downloaded': download_status.get('weekend', False)
                }
            }
        }
        
        with open(json_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_json, f, indent=2, ensure_ascii=False)
        
        logger.info("JSON metadata file updated successfully")
        
    except Exception as e:
        logger.error(f"Failed to update JSON metadata: {str(e)}")


def send_notification(message: str, is_error: bool = False):
    """
    Send notification about the download status via Email or Webhook.
    
    Args:
        message: Notification message
        is_error: Whether this is an error notification
    """
    # Log the notification
    if is_error:
        logger.error(f"NOTIFICATION: {message}")
    else:
        logger.info(f"NOTIFICATION: {message}")
    
    if not NOTIFICATION_ENABLED or not config:
        return

    # Check if we should notify for this level
    if is_error and not getattr(config, 'NOTIFY_ON_ERROR', True):
        return
    if not is_error and not getattr(config, 'NOTIFY_ON_SUCCESS', False):
        return

    # Email Notification
    if getattr(config, 'EMAIL_ENABLED', False):
        try:
            msg = MIMEMultipart()
            msg['From'] = config.EMAIL_FROM
            msg['To'] = config.EMAIL_TO
            prefix = getattr(config, 'EMAIL_SUBJECT_PREFIX', '[Bus Schedules]')
            status = 'ERROR' if is_error else 'SUCCESS'
            msg['Subject'] = f"{prefix} {status} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP(config.EMAIL_SMTP_SERVER, config.EMAIL_SMTP_PORT) as server:
                server.starttls()
                server.login(config.EMAIL_FROM, config.EMAIL_PASSWORD)
                server.send_message(msg)
            logger.info("Email notification sent successfully")
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")

    # Webhook Notification (Slack/Discord)
    if getattr(config, 'WEBHOOK_ENABLED', False):
        try:
            payload = {}
            if config.WEBHOOK_TYPE == 'slack':
                payload = {"text": f"*{'🚨 ERROR' if is_error else '✅ SUCCESS'}*: {message}"}
            elif config.WEBHOOK_TYPE == 'discord':
                payload = {"content": f"**{'🚨 ERROR' if is_error else '✅ SUCCESS'}**: {message}"}
            else:
                payload = {"message": message, "status": "error" if is_error else "success"}

            requests.post(config.WEBHOOK_URL, json=payload, timeout=10)
            logger.info("Webhook notification sent successfully")
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {str(e)}")


def main():
    """Main execution function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Download bus schedule PDFs from Çanakkale Municipality website'
    )
    parser.add_argument(
        '--timestamp', '-t',
        action='store_true',
        help='Save files with timestamp (e.g., weekday_schedule_20260119.pdf)'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Force download even if files haven\'t changed'
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default=None,
        help='Custom output directory for downloaded files'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose/debug logging'
    )
    
    args = parser.parse_args()
    
    # Update logging level if verbose
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Update output directory if specified
    global DOWNLOAD_DIR
    if args.output_dir:
        DOWNLOAD_DIR = Path(args.output_dir)
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("Starting Bus Schedule PDF Download")
    logger.info(f"Timestamp mode: {args.timestamp}")
    logger.info(f"Output directory: {DOWNLOAD_DIR}")
    logger.info("=" * 60)
    
    try:
        # Fetch the page content
        html_content = fetch_page_content(BASE_URL)
        
        # Extract PDF links
        pdf_links = extract_pdf_links(html_content)
        
        # Validate that we found the necessary links
        if not pdf_links['weekday'] and not pdf_links['weekend']:
            error_msg = "No PDF links found on the page! The website structure may have changed."
            logger.error(error_msg)
            send_notification(error_msg, is_error=True)
            sys.exit(1)
        
        # Generate filenames based on timestamp option
        timestamp_str = datetime.now().strftime('%Y%m%d')
        weekday_filename = f"canakkale_bus_weekday_{timestamp_str}.pdf" if args.timestamp else "canakkale_bus_weekday_latest.pdf"
        weekend_filename = f"canakkale_bus_weekend_{timestamp_str}.pdf" if args.timestamp else "canakkale_bus_weekend_latest.pdf"
        
        # Download the PDFs
        download_status = {}
        
        if pdf_links['weekday']:
            download_status['weekday'] = download_pdf(
                pdf_links['weekday'], 
                weekday_filename,
                force=args.force
            )
        else:
            logger.warning("No weekday schedule link found")
            send_notification("Weekday schedule link not found on the page", is_error=True)
            download_status['weekday'] = False
        
        if pdf_links['weekend']:
            download_status['weekend'] = download_pdf(
                pdf_links['weekend'], 
                weekend_filename,
                force=args.force
            )
        else:
            logger.warning("No weekend schedule link found")
            send_notification("Weekend schedule link not found on the page", is_error=True)
            download_status['weekend'] = False
        
        # Update metadata
        update_metadata(pdf_links, download_status, use_timestamp=args.timestamp)
        
        # Summary
        logger.info("=" * 60)
        logger.info("Download Summary:")
        logger.info(f"  Weekday Schedule: {'✓ Success' if download_status['weekday'] else '✗ Failed'}")
        logger.info(f"  Weekend Schedule: {'✓ Success' if download_status['weekend'] else '✗ Failed'}")
        logger.info(f"  Files saved to: {DOWNLOAD_DIR}")
        logger.info("=" * 60)
        
        # Exit with error code if any download failed
        if not all(download_status.values()):
            failed_items = [k for k, v in download_status.items() if not v]
            send_notification(f"Failed to download: {', '.join(failed_items)}", is_error=True)
            sys.exit(1)
        
        send_notification("All bus schedules downloaded successfully!")
        logger.info("All downloads completed successfully!")
        
    except requests.RequestException as e:
        error_msg = f"Network error while fetching data: {str(e)}"
        logger.error(error_msg, exc_info=True)
        send_notification(error_msg, is_error=True)
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"Unexpected error occurred: {str(e)}"
        logger.error(error_msg, exc_info=True)
        send_notification(error_msg, is_error=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
