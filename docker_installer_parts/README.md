# Docker Installer Parts

This directory contains the split parts of the original `docker_installer.exe` file (491.26 MB).

## Files
- `part_1.exe` - Part 1 (80 MB)
- `part_2.exe` - Part 2 (80 MB)
- `part_3.exe` - Part 3 (80 MB)
- `part_4.exe` - Part 4 (80 MB)
- `part_5.exe` - Part 5 (80 MB)
- `part_6.exe` - Part 6 (80 MB)
- `part_7.exe` - Part 7 (11.26 MB)

## Reassembly Instructions

To reassemble the original file:

1. Copy all parts to the same directory
2. Run the following PowerShell command:

```powershell
Get-Content part_*.exe -Encoding Byte | Set-Content docker_installer.exe -Encoding Byte
```

Or manually concatenate the files in order:
```
copy /b part_1.exe + part_2.exe + part_3.exe + part_4.exe + part_5.exe + part_6.exe + part_7.exe docker_installer.exe
```

The original file was split to comply with GitHub's 100MB file size limit.
