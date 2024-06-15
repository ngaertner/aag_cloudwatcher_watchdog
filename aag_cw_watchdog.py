import os
import time
from datetime import datetime
import subprocess
import sys
import psutil    
import logging
import logging.handlers
import pathlib
from io import StringIO
import argparse
import tempfile


############## BEGIN - SET YOUR CONSTANTS HERE - BEGIN ######################

### PLEASE use foward "/" as path or file separator - no '\'!

CLOUD_WATCHER_EXE         = "AAG_CloudWatcher.exe"
CLOUD_WATCHER_PATH        = "C:/Program Files (x86)/AAG_CloudWatcher"
CLOUD_WATCHER_TIMEOUT_SEC = 120
LOG_FILE                  = "aag_watchdog.log"
LOG_LEVEL                 = logging.NOTSET

############## END - SET YOUR CONSTANTS HERE - END ######################

parser = argparse.ArgumentParser()
parser.add_argument('--cw_path', help='Cloud Watcher Path', default=CLOUD_WATCHER_PATH)
parser.add_argument('--out_path', help='Cloud Watcher Output Path (contais aag_json.dat)',required=True)
parser.add_argument('--timeout', help='Timeout to restart Cloud Watcher in Seconds', default=CLOUD_WATCHER_TIMEOUT_SEC)
parser.add_argument('--log_file', help='Logfile', default=LOG_FILE)
parser.add_argument('--log_level', help='Log Level', default='INFO', choices=['INFO','WARNING','ERROR'])

args = parser.parse_args()

CLOUD_WATCHER_PATH = args.cw_path
CLOUD_WATCHER_OUTPUT_PATH = args.out_path
CLOUD_WATCHER_TIMEOUT_SEC = args.timeout
CLOUD_WATCHER_LOG_FILE = args.log_file

match args.log_level:
    case 'INFO':
        LOG_LEVEL = logging.INFO
    case 'WARNING':
        LOG_LEVEL = logging.WARNING
    case 'ERROR':
        LOG_LEVEL = logging.ERROR
    case _:
        LOG_LEVEL = LOG_LEVEL

#logging.basicConfig(encoding='utf-8')
logger = logging.getLogger('AAG_CW_WATCHDOG')

log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")

log_file = logging.handlers.TimedRotatingFileHandler(LOG_FILE, 'D', 1, 5)
log_file.setLevel(LOG_LEVEL)
log_file.setFormatter(log_formatter)

log_handler = logging.StreamHandler(sys.stdout)
log_handler.setLevel(LOG_LEVEL)
log_handler.setFormatter(log_formatter)

logger.addHandler(log_handler)
logger.addHandler(log_file)
logger.setLevel(LOG_LEVEL)

cloudwather_exe_file = pathlib.Path(CLOUD_WATCHER_PATH, CLOUD_WATCHER_EXE)
aag_json_file = pathlib.Path(CLOUD_WATCHER_OUTPUT_PATH, "aag_json.dat")


# check if cloud watcher exe exists
if os.path.isfile(cloudwather_exe_file) == False:
    logger.error(f'Cloud Watcher EXE File "{cloudwather_exe_file} was not found!')
    log_file.flush()
    sys.exit()


# check if aag_json.dat exists already
if os.path.isfile(aag_json_file):
    st=os.stat(aag_json_file)
    mtime=st.st_mtime
    last_change = datetime.fromtimestamp(mtime)
    logger.info(f"{aag_json_file} last change = {last_change}")
else:
    logger.warning(f'{aag_json_file} does not exist!')
    last_change = datetime.min


if ( (datetime.now() -last_change).total_seconds() > CLOUD_WATCHER_TIMEOUT_SEC ):
    # trigger restart of cloudwatcher

    if (CLOUD_WATCHER_EXE not in (p.name() for p in psutil.process_iter())):
       logger.warning("Cloud Watcher is not running!")
    else:
       logger.info("Killing running Cloud Watcher!")
       with open(os.devnull, 'w') as fp:
          sp = subprocess.Popen("taskkill /f /im " + CLOUD_WATCHER_EXE, shell=True, stdout = fp, stderr=subprocess.STDOUT)
       time.sleep(1)
       if (CLOUD_WATCHER_EXE not in (p.name() for p in psutil.process_iter())):
            logger.info("Cloud Watcher successfully killed!")
       else:    
           logger.error("Cloud Watcher could not be killed!")
           log_file.flush()
           sys.exit()

    logger.info("Starting Cloud Watcher!")
    sp = subprocess.Popen([cloudwather_exe_file,""],stderr=subprocess.STDOUT,shell=True)
    time.sleep(1)
    if (CLOUD_WATCHER_EXE not in (p.name() for p in psutil.process_iter())):
        logger.error("Cloud Watcher could not be started!")

    log_file.flush()
