# aag_cloudwatcher_watchdog
This is a simple watchdog script to check if AAG Cloud Watcher is working as expected, and restart it in case it is not.

The script is checking if the age of the aag_json.dat file is older than an expected value.
If this is the case it kills the Cloud Watcher process and (re-)starts it.

Please customize the constants at the beginning of the script for your environment.
