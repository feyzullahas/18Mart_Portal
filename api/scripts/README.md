# Bus schedule PDF refresh

The scheduled refresh is defined in `.github/workflows/download_bus_schedules.yml`. It runs every six hours and calls `refresh_bus_schedules.py`, which reads every PDF link from the official Çanakkale Municipality schedule page, downloads each valid PDF, and writes the exact page title and source URL to `api/data/bus_schedules/metadata.json` and `metadata.txt`.

Run it manually from the repository root:

```powershell
.venv\Scripts\python.exe api\scripts\refresh_bus_schedules.py
```

Use `--output-dir PATH` to select another output directory. The API separately refreshes the list and proxies requested PDFs with a six-hour cache.
