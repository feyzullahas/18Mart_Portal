# Bus Schedule PDF Downloader

This project includes an automated system to download the latest bus schedule PDFs from the Çanakkale Municipality website.

## Features

- 🚌 **Automatic PDF Download**: Scrapes and downloads both weekday and weekend bus schedules
- 🔄 **Daily Updates**: GitHub Actions workflow runs daily at 3:00 AM UTC
- 📝 **Metadata Tracking**: Keeps track of download timestamps and source URLs
- 🔍 **Smart Detection**: Dynamically finds PDF links using BeautifulSoup
- 💾 **Overwrite Old Files**: Automatically replaces old schedules with new ones
- 📊 **Logging**: Comprehensive logging for debugging and monitoring

## File Structure

```
18Mart_Portal/
├── backend/
│   ├── data/
│   │   └── bus_schedules/          # Downloaded PDFs stored here
│   │       ├── weekday_schedule.pdf
│   │       ├── weekend_schedule.pdf
│   │       └── metadata.txt
│   └── scripts/
│       ├── download_bus_schedules.py  # Main scraper script
│       └── requirements.txt           # Python dependencies
└── .github/
    └── workflows/
        └── download_bus_schedules.yml # GitHub Actions workflow
```

## Local Usage

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. Navigate to the scripts directory:
```bash
cd backend/scripts
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Script

Run the download script manually:

```bash
python backend/scripts/download_bus_schedules.py
```

The script will:
1. Fetch the bus schedules page from the municipality website
2. Parse the HTML to find PDF links
3. Download weekday and weekend schedules
4. Save them to `backend/data/bus_schedules/`
5. Create a metadata file with download information

## GitHub Actions Automation

### How It Works

The GitHub Actions workflow (`download_bus_schedules.yml`) automatically:

1. **Runs Daily**: Executes at 3:00 AM UTC every day
2. **Downloads PDFs**: Runs the Python script to fetch latest schedules
3. **Commits Changes**: If PDFs are updated, commits them to the repository
4. **Uploads Artifacts**: Saves PDFs as workflow artifacts for 7 days

### Manual Trigger

You can manually trigger the workflow:

1. Go to your repository on GitHub
2. Click on **Actions** tab
3. Select **Download Bus Schedules** workflow
4. Click **Run workflow**

### Monitoring

- Check workflow runs in the **Actions** tab
- View logs for each step
- Download artifacts if needed

## Configuration

### Change Schedule Time

Edit `.github/workflows/download_bus_schedules.yml`:

```yaml
schedule:
  - cron: '0 3 * * *'  # Change this cron expression
```

Cron format: `minute hour day month weekday`
- Example: `'0 6 * * *'` = 6:00 AM UTC daily
- Example: `'0 */6 * * *'` = Every 6 hours

### Change Download Directory

Edit `backend/scripts/download_bus_schedules.py`:

```python
DOWNLOAD_DIR = Path(__file__).parent.parent / "data" / "bus_schedules"
```

### Add More PDF Types

Modify the `extract_pdf_links()` function to detect additional PDF types:

```python
# Add new PDF type
if 'SPECIAL_SCHEDULE' in text:
    pdf_links['special'] = href
```

## Troubleshooting

### Script Fails to Download

1. **Check Internet Connection**: Ensure the server has internet access
2. **Verify URL**: Confirm the municipality website is accessible
3. **Check Logs**: Review the script output for specific errors

### GitHub Actions Fails

1. **Check Workflow Logs**: View detailed logs in the Actions tab
2. **Verify Permissions**: Ensure the workflow has write permissions
3. **Check Dependencies**: Confirm all Python packages are installed

### PDFs Not Updating

1. **Verify Source Website**: Check if the municipality has updated their PDFs
2. **Check Metadata**: Review `metadata.txt` for last update time
3. **Manual Run**: Try running the script manually to test

## API Integration

The downloaded PDFs can be served through your FastAPI backend:

```python
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/api/bus-schedules/weekday")
async def get_weekday_schedule():
    return FileResponse("data/bus_schedules/weekday_schedule.pdf")

@app.get("/api/bus-schedules/weekend")
async def get_weekend_schedule():
    return FileResponse("data/bus_schedules/weekend_schedule.pdf")
```

## License

This script is part of the 18Mart_Portal project.

## Support

For issues or questions:
- Check the logs in `backend/scripts/download_bus_schedules.py`
- Review GitHub Actions workflow runs
- Verify the source website structure hasn't changed
