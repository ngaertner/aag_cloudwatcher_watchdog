import os
import time
from datetime import datetime
import subprocess
import sys
import psutil    
import logging
import pathlib
from io import StringIO

############## BEGIN - SET YOUR CONSTANTS HERE - BEGIN ######################

### PLEASE use foward "/" as path or file separator - no '\'!

CLOUD_WATCHER_EXE         = "AAG_CloudWatcher.exe"
CLOUD_WATCHER_PATH        = "C:/Program Files (x86)/AAG_CloudWatcher"
CLOUD_WATCHER_OUTPUT_PATH = "C:/aag"
CLOUD_WATCHER_TIMEOUT_SEC = 120
LOG_FILE                  = "C:/aag/aag_watchdog.log"
LOG_LEVEL                 = logging.INFO

############## END - SET YOUR CONSTANTS HERE - END ######################



logging.basicConfig(filename=LOG_FILE, encoding='utf-8')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

log_handler = logging.StreamHandler(sys.stdout)
log_handler.setLevel(LOG_LEVEL)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

cloudwather_exe_file = pathlib.Path(CLOUD_WATCHER_PATH, CLOUD_WATCHER_EXE)
aag_json_file = pathlib.Path(CLOUD_WATCHER_OUTPUT_PATH, "aag_json.dat")


# check if cloud watcher exe exists
if os.path.isfile(cloudwather_exe_file) == False:
    logging.error('Cloud Watcher EXE File was not found!')
    sys.exit()


# check if aag_json.dat exists already
if os.path.isfile(aag_json_file):
    st=os.stat(aag_json_file)
    mtime=st.st_mtime
    last_change = datetime.fromtimestamp(mtime)
    logging.info("aag_json.dat last change = {}".format(last_change))
else:
    logging.warning('aag_json.dat does not exist!')
    last_change = datetime.min


if ( (datetime.now() -last_change).total_seconds() > CLOUD_WATCHER_TIMEOUT_SEC ):
    # trigger restart of cloudwatcher

    if (CLOUD_WATCHER_EXE not in (p.name() for p in psutil.process_iter())):
       logging.warning("Cloud Watcher is not running!")
    else:
       logging.info("Killing running Cloud Watcher!")
       with open(os.devnull, 'w') as fp:
          sp = subprocess.Popen("taskkill /f /im " + CLOUD_WATCHER_EXE, shell=True, stdout = fp, stderr=subprocess.STDOUT)
       time.sleep(1)
       if (CLOUD_WATCHER_EXE not in (p.name() for p in psutil.process_iter())):
           logging.info("Cloud Watcher successfully killed!")
       else:    
           logging.error("Cloud Watcher could not be killed!")
           sys.exit()

    logging.info("Starting Cloud Watcher!")
    sp = subprocess.Popen([cloudwather_exe_file,""],stderr=subprocess.STDOUT,shell=True)
    time.sleep(1)
    if (CLOUD_WATCHER_EXE not in (p.name() for p in psutil.process_iter())):
        logging.error("Cloud Watcher could not be started!")

