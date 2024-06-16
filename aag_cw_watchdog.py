#BSD 3-Clause License
#
#Copyright (c) 2024, Nico Gärtner
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#
#1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
#3. Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import time
from datetime import datetime
import subprocess
import sys
import psutil    
import logging
import logging.handlers
import pathlib
import argparse
import winreg

SCRIPT_VERSION = 'v0.0.2'

############## BEGIN - SET YOUR CONSTANTS HERE - BEGIN ######################

### PLEASE use foward "/" as path or file separator - no '\'!

CLOUD_WATCHER_EXE         = "AAG_CloudWatcher.exe"
CLOUD_WATCHER_PATH        = "C:/Program Files (x86)/AAG_CloudWatcher"
CLOUD_WATCHER_TIMEOUT_SEC = 120
CLOUD_WATCHER_AAG_JSON    = "aag_json.dat"
CLOUD_WATCHER_OUTPUT_PATH = ""
LOG_DIR                   = ""
LOG_FILE                  = "aag_cw_watchdog.log"
LOG_LEVEL                 = logging.NOTSET

############## END - SET YOUR CONSTANTS HERE - END ######################


#### initialize argparser for CLI
parser = argparse.ArgumentParser()
parser.add_argument('--cw_path', help="Cloud Watcher Path (contains AAG_CloudWatcher.exe)", default=CLOUD_WATCHER_PATH)
parser.add_argument('--out_path', help=f"Cloud Watcher Output Path (contains {CLOUD_WATCHER_AAG_JSON})", default=CLOUD_WATCHER_OUTPUT_PATH)
parser.add_argument('--timeout', help=f"Timeout to restart inactive Cloud Watcher in seconds - default {CLOUD_WATCHER_TIMEOUT_SEC}s", default=CLOUD_WATCHER_TIMEOUT_SEC)
parser.add_argument('--log_dir', help="Directory to store Log Files", default=LOG_DIR)
parser.add_argument('--log_file', help=f"Log Filename - default {LOG_FILE}", default=LOG_FILE)
parser.add_argument('--log_level', help="Log Level (INFO|WARNING|ERROR) - default INFO", default='INFO', choices=['INFO','WARNING','ERROR'])

args = parser.parse_args()

CLOUD_WATCHER_PATH = args.cw_path
CLOUD_WATCHER_OUTPUT_PATH = args.out_path
CLOUD_WATCHER_TIMEOUT_SEC = args.timeout
LOG_DIR = args.log_dir

match args.log_level:
    case 'INFO':
        LOG_LEVEL = logging.INFO
    case 'WARNING':
        LOG_LEVEL = logging.WARNING
    case 'ERROR':
        LOG_LEVEL = logging.ERROR
    case _:
        LOG_LEVEL = logging.NOTSET



#### logger initialization

if LOG_DIR == "":
    log_file = pathlib.Path(os.getcwd(), LOG_FILE)
else:
    log_file = pathlib.Path(LOG_DIR, LOG_FILE)


logger = logging.getLogger('AAG_CW_WATCHDOG')

log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")

log_file_handler = logging.handlers.TimedRotatingFileHandler(log_file, 'midnight', 1, 7)
log_file_handler.suffix = "%Y-%m-%d"
log_file_handler.setLevel(LOG_LEVEL)
log_file_handler.setFormatter(log_formatter)

log_handler = logging.StreamHandler(sys.stdout)
log_handler.setLevel(LOG_LEVEL)
log_handler.setFormatter(log_formatter)

logger.addHandler(log_handler)
logger.addHandler(log_file_handler)
logger.setLevel(LOG_LEVEL)


#### initialize cloud watcher output path from registry
if CLOUD_WATCHER_OUTPUT_PATH == "":
    try:
        aReg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        aKey = winreg.OpenKey(aReg, r'Software\VB and VBA Program Settings\AAG_CloudWatcher\COMMFile')
        CLOUD_WATCHER_OUTPUT_PATH = winreg.QueryValueEx(aKey, "PathNameCCDAP4")[0]
    except:
        logger.error("Error while reading Windows Registry - Output Path could not be determined automatically!")


#### build filenames to use in the script

cloudwather_exe_file = pathlib.Path(CLOUD_WATCHER_PATH, CLOUD_WATCHER_EXE)
aag_json_file = pathlib.Path(CLOUD_WATCHER_OUTPUT_PATH, CLOUD_WATCHER_AAG_JSON)

print("")
print("####################### AAG Cloud Watcher Watchdog ####################")
print("")
print(f"VERSION   {SCRIPT_VERSION}")
print("AUTHOR    Nico Gärtner - https://github.com/ngaertner")
print("LICENSE   BSD 3-Clause License")
print("")
print("############################## DISCLAIMER #############################")
print('THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,')
print('EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF')
print('MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND')
print('NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE')
print('LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION')
print('OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION')
print('WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.')
print("")
print("######################### ENVIRONMENT INFO ############################")
print(f"Cloud Watcher: {cloudwather_exe_file}")
print(f"File to check: {aag_json_file}")
print(f"Log File:      {log_file}")
print("#######################################################################")
print("")

#### checks

# check if cloud watcher exe exists
if os.path.isfile(cloudwather_exe_file) == False:
    logger.error(f'Cloud Watcher EXE File "{cloudwather_exe_file} was not found!')
    log_file_handler.flush()
    sys.exit()

# check if aag_json.dat exists already
if os.path.isfile(aag_json_file):
    st=os.stat(aag_json_file)
    mtime=st.st_mtime
    last_change = datetime.fromtimestamp(mtime)
    
    json_age = int((datetime.now() -last_change).total_seconds())
    logger.info(f"{CLOUD_WATCHER_AAG_JSON} - last change = {last_change.strftime("%Y-%m-%d, %H:%M:%S")} - age is {json_age} seconds")
    if json_age > CLOUD_WATCHER_TIMEOUT_SEC:
        logger.warning(f"{CLOUD_WATCHER_AAG_JSON} file is not up to date!")
else:
    logger.warning(f'{aag_json_file} does not exist!')
    last_change = datetime.min
    json_age = int((datetime.now() -last_change).total_seconds())

#### restart logic

if (json_age > CLOUD_WATCHER_TIMEOUT_SEC ):
    # trigger restart of cloudwatcher
    logger.info("Initiating (re-)start of Cloud Watcher.")

    if (CLOUD_WATCHER_EXE not in (p.name() for p in psutil.process_iter())):
       logger.warning("Cloud Watcher is not running!")
    else:
       logger.info("Killing running Cloud Watcher!")
       with open(os.devnull, 'w') as fp:
          sp = subprocess.Popen("taskkill /f /im " + CLOUD_WATCHER_EXE, shell=True, stdout = fp, stderr=subprocess.STDOUT)
       time.sleep(2) #wait for two seconds to kill process
       if (CLOUD_WATCHER_EXE not in (p.name() for p in psutil.process_iter())):
            logger.info("Cloud Watcher successfully killed!")
       else:    
           logger.critical("Cloud Watcher could not be killed!")
           log_file_handler.flush()
           sys.exit()

    logger.info("Starting Cloud Watcher!")
    sp = subprocess.Popen([cloudwather_exe_file,""],stderr=subprocess.STDOUT,shell=True)
    time.sleep(1)
    if (CLOUD_WATCHER_EXE not in (p.name() for p in psutil.process_iter())):
        logger.error("Cloud Watcher could not be started!")

    log_file_handler.flush()
