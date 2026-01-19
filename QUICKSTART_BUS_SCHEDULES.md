# Bus Schedule Automation - Quick Reference

## 🚀 Quick Commands

### Run Manually
```bash
# Basic run (with change detection)
python download_bus_schedules.py

# Force download (skip change detection)
python download_bus_schedules.py --force

# With detailed logging
python download_bus_schedules.py --verbose

# Save with timestamp
python download_bus_schedules.py --timestamp
```

### Test the System
```bash
# Run all tests
python test_download.py

# Test with verbose output
python download_bus_schedules.py --verbose --force
```

### Windows Task Scheduler
```powershell
# Setup (run as Administrator)
.\setup_windows_scheduler.ps1

# Run task manually
Start-ScheduledTask -TaskName "CanakkaleBusScheduleDownloader"

# Check task status
Get-ScheduledTask -TaskName "CanakkaleBusScheduleDownloader"

# View task history
Get-ScheduledTaskInfo -TaskName "CanakkaleBusScheduleDownloader"

# Disable task
Disable-ScheduledTask -TaskName "CanakkaleBusScheduleDownloader"

# Remove task
Unregister-ScheduledTask -TaskName "CanakkaleBusScheduleDownloader"
```

## 📁 File Locations

| File | Location | Purpose |
|------|----------|---------|
| Main Script | `backend/scripts/download_bus_schedules.py` | Downloads PDFs |
| Weekday PDF | `backend/data/bus_schedules/canakkale_bus_weekday_latest.pdf` | Latest weekday schedule |
| Weekend PDF | `backend/data/bus_schedules/canakkale_bus_weekend_latest.pdf` | Latest weekend schedule |
| Metadata JSON | `backend/data/bus_schedules/metadata.json` | Machine-readable metadata |
| Metadata Text | `backend/data/bus_schedules/metadata.txt` | Human-readable metadata |
| GitHub Workflow | `.github/workflows/download_bus_schedules.yml` | Automated cloud runs |
| Scheduler Setup | `backend/scripts/setup_windows_scheduler.ps1` | Windows automation |

## ⏰ Automation Schedule

- **GitHub Actions**: Daily at 3:00 AM Turkey Time (00:00 UTC)
- **Windows Task Scheduler**: Daily at 3:00 AM (configurable)

## 🔍 Check Status

### View Metadata
```bash
# JSON format
cat backend/data/bus_schedules/metadata.json

# Text format
cat backend/data/bus_schedules/metadata.txt
```

### Check Last Update
```bash
# On Windows
Get-Item backend/data/bus_schedules/*.pdf | Select-Object Name, LastWriteTime

# On Linux/Mac
ls -lh backend/data/bus_schedules/*.pdf
```

## 🐛 Troubleshooting

### Issue: PDFs not downloading
**Solution**: Run with verbose logging
```bash
python download_bus_schedules.py --verbose
```

### Issue: Files not updating
**Solution**: Force download
```bash
python download_bus_schedules.py --force
```

### Issue: Website structure changed
**Solution**: Check the website manually and review logs
1. Visit: https://ulasim.canakkale.bel.tr/rehber/hatlar-otobus-saatleri/
2. Check if PDFs are still available
3. Review `metadata.txt` for detected links

### Issue: Windows Task not running
**Solution**: Check Task Scheduler
```powershell
# View task details
Get-ScheduledTask -TaskName "CanakkaleBusScheduleDownloader" | Format-List *

# Check last run result (0 = success)
Get-ScheduledTaskInfo -TaskName "CanakkaleBusScheduleDownloader"
```

## 📊 Understanding Metadata

### metadata.json Structure
```json
{
  "last_updated": "ISO 8601 timestamp",
  "source_url": "Municipality website URL",
  "timestamped_mode": false,
  "files": {
    "weekday": {
      "filename": "canakkale_bus_weekday_latest.pdf",
      "source": "Direct PDF URL",
      "downloaded": true
    },
    "weekend": {
      "filename": "canakkale_bus_weekend_latest.pdf", 
      "source": "Direct PDF URL",
      "downloaded": true
    }
  }
}
```

## 🔧 Advanced Usage

### Custom Output Directory
```bash
python download_bus_schedules.py --output-dir "C:\custom\path"
```

### Archive Mode (Keep History)
```bash
# Creates files like: weekday_schedule_20260119.pdf
python download_bus_schedules.py --timestamp
```

### Combine Options
```bash
python download_bus_schedules.py --verbose --timestamp --force
```

## 📝 Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - all schedules downloaded |
| 1 | Error - download failed or PDFs not found |

## 🔗 Useful Links

- **Source Website**: https://ulasim.canakkale.bel.tr/rehber/hatlar-otobus-saatleri/
- **Full Documentation**: `backend/scripts/README.md`
- **GitHub Actions**: Repository → Actions → Download Bus Schedules

## 💡 Tips

1. **First time setup**: Run `python test_download.py` to verify everything works
2. **Monitor changes**: Check `metadata.json` to see when PDFs were last updated
3. **Save bandwidth**: The script automatically skips downloads if files haven't changed
4. **Manual trigger**: Use `--force` flag to download regardless of changes
5. **Keep history**: Use `--timestamp` flag to archive old schedules

---

**Need help?** Check the full documentation in `README.md`
