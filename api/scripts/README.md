# Automated Bus Schedule Download System

## Overview

This system automatically downloads the latest bus schedule PDFs from the Çanakkale Municipality website daily. It includes:

- ✅ **Intelligent PDF Detection**: Automatically finds the newest schedules using date indicators
- ✅ **Change Detection**: Only downloads when PDFs have actually changed
- ✅ **Retry Logic**: Handles temporary network failures gracefully
- ✅ **Multiple Automation Options**: GitHub Actions (cloud) or Windows Task Scheduler (local)
- ✅ **Comprehensive Logging**: Detailed logs and metadata tracking
- ✅ **Error Notifications**: Alerts when downloads fail or site structure changes

## Quick Start

### Option 1: GitHub Actions (Recommended for Cloud Deployment)

The system is already configured to run automatically via GitHub Actions:

- **Schedule**: Daily at 3:00 AM Turkey Time (00:00 UTC)
- **Location**: `.github/workflows/download_bus_schedules.yml`
- **No setup required** - it runs automatically!

#### Manual Trigger

You can manually trigger the workflow from GitHub:

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Download Bus Schedules** workflow
4. Click **Run workflow**
5. Choose options:
   - **use_timestamp**: Save files with date suffix (e.g., `weekday_schedule_20260119.pdf`)
   - **force_update**: Force commit even if files unchanged

### Option 2: Windows Task Scheduler (Local Automation)

For local Windows automation:

1. **Open PowerShell as Administrator**
2. **Navigate to the scripts directory**:
   ```powershell
   cd "c:\Users\feyzu\Desktop\18Mart_Portal\backend\scripts"
   ```
3. **Run the setup script**:
   ```powershell
   .\setup_windows_scheduler.ps1
   ```
4. **Follow the prompts** - the script will:
   - Verify Python installation
   - Create a scheduled task to run daily at 3:00 AM
   - Optionally run a test download

#### Managing the Windows Task

- **View Task**: Open Task Scheduler (`taskschd.msc`) and look for "CanakkaleBusScheduleDownloader"
- **Run Manually**: 
  ```powershell
  Start-ScheduledTask -TaskName "CanakkaleBusScheduleDownloader"
  ```
- **Disable Task**:
  ```powershell
  Disable-ScheduledTask -TaskName "CanakkaleBusScheduleDownloader"
  ```
- **Remove Task**:
  ```powershell
  Unregister-ScheduledTask -TaskName "CanakkaleBusScheduleDownloader"
  ```

### Option 3: Manual Execution

Run the script manually anytime:

```bash
# Basic usage (overwrites existing files)
python download_bus_schedules.py

# With verbose logging
python download_bus_schedules.py --verbose

# Save with timestamp (creates new files, doesn't overwrite)
python download_bus_schedules.py --timestamp

# Force download even if files haven't changed
python download_bus_schedules.py --force

# Custom output directory
python download_bus_schedules.py --output-dir "C:\custom\path"

# Combine options
python download_bus_schedules.py --verbose --timestamp --force
```

## How It Works

### 1. **Intelligent PDF Detection**

The script analyzes the municipality website and:

- Finds all PDF links on the page
- Identifies weekday schedules (keywords: "HAFTA İÇİ", "WEEKDAY")
- Identifies weekend schedules (keywords: "HAFTA SONU", "WEEKEND")
- **Prioritizes PDFs with date indicators** (e.g., "20 OCAK İTİBARİYLE")
- Selects the most recent version when multiple schedules exist

### 2. **Smart Change Detection**

Before downloading:

- Checks the remote PDF file size using HTTP HEAD request
- Compares with local file size
- **Skips download if sizes match** (saves bandwidth and time)
- Can be overridden with `--force` flag

### 3. **Robust Error Handling**

- **Network Failures**: Retries up to 3 times with 5-second delays
- **Site Structure Changes**: Logs detailed errors if PDFs can't be found
- **Invalid Files**: Warns if downloaded files are suspiciously small
- **Comprehensive Logging**: All actions logged with timestamps

### 4. **Metadata Tracking**

After each run, the system creates:

#### `metadata.json` (for programmatic access)
```json
{
  "last_updated": "2026-01-19T17:12:29.379242",
  "source_url": "https://ulasim.canakkale.bel.tr/rehber/hatlar-otobus-saatleri/",
  "timestamped_mode": false,
  "files": {
    "weekday": {
      "filename": "weekday_schedule.pdf",
      "source": "https://ulasim.canakkale.bel.tr/wp-content/uploads/2018/02/20-OCAK-4.pdf",
      "downloaded": true
    },
    "weekend": {
      "filename": "weekend_schedule.pdf",
      "source": "https://ulasim.canakkale.bel.tr/wp-content/uploads/2018/02/24-OCAK.pdf",
      "downloaded": true
    }
  }
}
```

#### `metadata.txt` (human-readable)
Contains download timestamp, source URLs, and all detected PDF links.

## File Structure

```
backend/
├── scripts/
│   ├── download_bus_schedules.py      # Main download script
│   ├── setup_windows_scheduler.ps1    # Windows Task Scheduler setup
│   ├── test_download.py               # Test script
│   ├── requirements.txt               # Python dependencies
│   └── README.md                      # This file
└── data/
    └── bus_schedules/
        ├── weekday_schedule.pdf       # Latest weekday schedule
        ├── weekend_schedule.pdf       # Latest weekend schedule
        ├── metadata.json              # JSON metadata
        ├── metadata.txt               # Human-readable metadata
        └── logs/                      # Log files (Windows scheduler)
```

## Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--verbose` | `-v` | Enable detailed debug logging |
| `--timestamp` | `-t` | Save files with date suffix (e.g., `weekday_schedule_20260119.pdf`) |
| `--force` | `-f` | Force download even if files haven't changed |
| `--output-dir PATH` | `-o PATH` | Custom output directory for downloaded files |

## Troubleshooting

### PDFs Not Downloading

1. **Check your internet connection**
2. **Verify the website is accessible**: Visit https://ulasim.canakkale.bel.tr/rehber/hatlar-otobus-saatleri/
3. **Run with verbose logging**: `python download_bus_schedules.py --verbose`
4. **Check the logs** in `backend/data/bus_schedules/logs/` (Windows scheduler)

### Website Structure Changed

If the script reports "No PDF links found":

1. The municipality may have changed their website structure
2. Check `metadata.txt` to see what links were previously found
3. Visit the website manually to verify PDFs are still available
4. The script may need updates to handle new HTML structure

### Files Not Updating

If you expect new PDFs but files aren't updating:

1. **Check if PDFs actually changed**: The script skips downloads if file sizes match
2. **Force a download**: `python download_bus_schedules.py --force`
3. **Check metadata.json**: See the source URLs and last update time
4. **Verify remote PDFs**: Visit the source URLs in `metadata.json`

### Windows Task Not Running

1. **Open Task Scheduler** (`taskschd.msc`)
2. **Find the task**: "CanakkaleBusScheduleDownloader"
3. **Check "Last Run Result"**: Should be 0x0 for success
4. **View History tab**: See detailed execution logs
5. **Ensure "Run whether user is logged on or not" is selected**
6. **Check network availability**: Task is set to run only when network is available

## Integration with Your Application

### Backend API

The downloaded PDFs can be served through your FastAPI backend:

```python
from fastapi import FastAPI
from fastapi.responses import FileResponse
import json
from pathlib import Path

app = FastAPI()

SCHEDULE_DIR = Path("data/bus_schedules")

@app.get("/api/bus-schedules/weekday")
async def get_weekday_schedule():
    """Serve the weekday bus schedule PDF"""
    pdf_path = SCHEDULE_DIR / "weekday_schedule.pdf"
    if pdf_path.exists():
        return FileResponse(pdf_path, media_type="application/pdf")
    return {"error": "Schedule not found"}

@app.get("/api/bus-schedules/weekend")
async def get_weekend_schedule():
    """Serve the weekend bus schedule PDF"""
    pdf_path = SCHEDULE_DIR / "weekend_schedule.pdf"
    if pdf_path.exists():
        return FileResponse(pdf_path, media_type="application/pdf")
    return {"error": "Schedule not found"}

@app.get("/api/bus-schedules/metadata")
async def get_schedule_metadata():
    """Get metadata about the schedules"""
    metadata_path = SCHEDULE_DIR / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path) as f:
            return json.load(f)
    return {"error": "Metadata not found"}
```

### Frontend Display

Display the PDFs in your React frontend:

```jsx
import React, { useState, useEffect } from 'react';

function BusSchedules() {
  const [metadata, setMetadata] = useState(null);
  const [activeSchedule, setActiveSchedule] = useState('weekday');

  useEffect(() => {
    fetch('/api/bus-schedules/metadata')
      .then(res => res.json())
      .then(data => setMetadata(data));
  }, []);

  return (
    <div className="bus-schedules">
      <h2>Otobüs Saatleri</h2>
      
      {metadata && (
        <p className="last-updated">
          Son Güncelleme: {new Date(metadata.last_updated).toLocaleString('tr-TR')}
        </p>
      )}
      
      <div className="schedule-tabs">
        <button 
          onClick={() => setActiveSchedule('weekday')}
          className={activeSchedule === 'weekday' ? 'active' : ''}
        >
          Hafta İçi
        </button>
        <button 
          onClick={() => setActiveSchedule('weekend')}
          className={activeSchedule === 'weekend' ? 'active' : ''}
        >
          Hafta Sonu
        </button>
      </div>
      
      <iframe
        src={`/api/bus-schedules/${activeSchedule}`}
        width="100%"
        height="600px"
        title={`${activeSchedule} schedule`}
      />
      
      <a 
        href={`/api/bus-schedules/${activeSchedule}`}
        download
        className="download-button"
      >
        PDF İndir
      </a>
    </div>
  );
}
```

## Monitoring & Notifications

### Current Notifications

The script logs all events with severity levels:
- **INFO**: Normal operations
- **WARNING**: Non-critical issues (e.g., file unchanged)
- **ERROR**: Critical failures

### Future Enhancements

The `send_notification()` function is designed to be extended with:

- **Email notifications** (SMTP)
- **Slack/Discord webhooks**
- **Push notifications** (Pushover, Pushbullet)
- **SMS alerts** (Twilio)

Example email notification:

```python
import smtplib
from email.mime.text import MIMEText

def send_notification(message: str, is_error: bool = False):
    # Existing logging
    if is_error:
        logger.error(f"NOTIFICATION: {message}")
    else:
        logger.info(f"NOTIFICATION: {message}")
    
    # Email notification
    if is_error:  # Only send emails for errors
        msg = MIMEText(message)
        msg['Subject'] = 'Bus Schedule Download Error'
        msg['From'] = 'your-email@example.com'
        msg['To'] = 'admin@example.com'
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('your-email@example.com', 'your-password')
            server.send_message(msg)
```

## Dependencies

Install required Python packages:

```bash
pip install -r requirements.txt
```

Required packages:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser (faster than default)

## Security Considerations

- **No authentication required**: The municipality website is public
- **Rate limiting**: Script includes delays between retries
- **User-Agent**: Uses realistic browser user-agent to avoid blocking
- **HTTPS**: All requests use secure HTTPS connections
- **No sensitive data**: No credentials or API keys required

## Performance

- **First run**: ~5-10 seconds (downloads both PDFs)
- **Subsequent runs**: ~2-3 seconds (if no changes detected)
- **Bandwidth**: ~2-3 MB per download (both PDFs)
- **Storage**: ~2-3 MB for PDFs + minimal metadata

## License

This automation system is part of the 18 Mart Portal project.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the logs in `backend/data/bus_schedules/logs/`
3. Run with `--verbose` flag for detailed debugging
4. Check GitHub Actions workflow runs for cloud automation issues

---

**Last Updated**: January 19, 2026
**Version**: 2.0 (with change detection and Windows scheduler support)
