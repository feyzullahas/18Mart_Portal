# Windows Task Scheduler Setup Script for Bus Schedule Downloads
# This script creates a scheduled task to run the bus schedule downloader daily at 3:00 AM

# Configuration
$TaskName = "CanakkaleBusScheduleDownloader"
$TaskDescription = "Automatically downloads the latest bus schedules from Çanakkale Municipality website"
$ScriptPath = Join-Path $PSScriptRoot "download_bus_schedules.py"
$PythonPath = "python"  # Adjust if needed (e.g., "C:\Python311\python.exe")
$LogDir = Join-Path $PSScriptRoot "..\data\bus_schedules\logs"
$LogFile = Join-Path $LogDir "scheduler_$(Get-Date -Format 'yyyyMMdd').log"

# Ensure log directory exists
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Bus Schedule Downloader - Task Scheduler Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Verify Python is available
try {
    $pythonVersion = & $PythonPath --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found at: $PythonPath" -ForegroundColor Red
    Write-Host "Please install Python or update the `$PythonPath variable in this script" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Verify script exists
if (-not (Test-Path $ScriptPath)) {
    Write-Host "✗ Script not found at: $ScriptPath" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Download script found" -ForegroundColor Green

# Remove existing task if it exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host ""
    Write-Host "Found existing task. Removing..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "✓ Existing task removed" -ForegroundColor Green
}

# Create the scheduled task action
# The action runs Python with the download script and logs output
$action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "`"$ScriptPath`" --verbose" `
    -WorkingDirectory (Split-Path $ScriptPath)

# Create the trigger (daily at 3:00 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At "03:00AM"

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# Create principal (run whether user is logged on or not)
$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType S4U `
    -RunLevel Highest

# Register the scheduled task
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Description $TaskDescription `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Force | Out-Null
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ Task created successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  Name: $TaskName"
    Write-Host "  Schedule: Daily at 3:00 AM"
    Write-Host "  Script: $ScriptPath"
    Write-Host "  Log Directory: $LogDir"
    Write-Host ""
    Write-Host "To manage this task:" -ForegroundColor Yellow
    Write-Host "  - Open Task Scheduler (taskschd.msc)"
    Write-Host "  - Look for '$TaskName' in Task Scheduler Library"
    Write-Host ""
    Write-Host "To run the task manually:" -ForegroundColor Yellow
    Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""
    
    # Ask if user wants to run the task now
    $runNow = Read-Host "Would you like to run the task now to test it? (Y/N)"
    if ($runNow -eq 'Y' -or $runNow -eq 'y') {
        Write-Host ""
        Write-Host "Running task..." -ForegroundColor Cyan
        Start-ScheduledTask -TaskName $TaskName
        Start-Sleep -Seconds 2
        
        # Check task status
        $task = Get-ScheduledTask -TaskName $TaskName
        $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
        
        Write-Host "Task Status: $($task.State)" -ForegroundColor Cyan
        Write-Host "Last Run Time: $($taskInfo.LastRunTime)" -ForegroundColor Cyan
        Write-Host "Last Result: $($taskInfo.LastTaskResult)" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Check the log files in: $LogDir" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host ""
    Write-Host "✗ Failed to create scheduled task: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Read-Host "Press Enter to exit"
