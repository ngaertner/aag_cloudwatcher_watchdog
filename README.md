# Watchdog Script for AAG Cloud Watcher
This is a simple watchdog script to check if AAG Cloud Watcher is working as expected, and restart it in case it is not.

The script is checking if the age of the aag_json.dat file is older than an expected value.
If this is the case it kills the Cloud Watcher process and (re-)starts it.

You can use the following command line arguments to configure the script:

`
usage: aag_cw_watchdog [-h] [--cw_path CW_PATH] --out_path OUT_PATH [--timeout TIMEOUT] [--log_file LOG_FILE] [--log_level {INFO,WARNING,ERROR}]

options:
  -h, --help                        show this help message and exit
  --cw_path CW_PATH                 Cloud Watcher Path (contains AAG_CloudWatcher.exe)
  --out_path OUT_PATH               Cloud Watcher Output Path (contains aag_json.dat)
  --timeout TIMEOUT                 Timeout to restart inactive Cloud Watcher in seconds (default 120s)
  --log_file LOG_FILE               Logfile
  --log_level {INFO,WARNING,ERROR}  Log Level
`

The following example assumes that AAG Cloud Watcher is installed in the default directory "C:/Program Files (x86)/AAG_CloudWatcher". The output path where aag_json.dat is written is "C:\aag".
Please specify the correct paths for your installation.

`
aag_cw_watchdog --out_path c:\aag
`