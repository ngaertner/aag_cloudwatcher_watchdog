# Watchdog Script for AAG Cloud Watcher
This is a simple watchdog script to check if [AAG Cloud Watcher](https://eu.lunaticoastro.com/product/aag-cloudwatcher-cloud-detector/) is working as expected, and restart it in case it is not.
It is intended to mitigate instabilites of Cloud Watcher which can lead to crashes (e.g. "Run-time error '6': Overflow").

The script is checking if the age of the aag_json.dat file is older than an expected value.
If this is the case it kills the Cloud Watcher process and (re-)starts it.

In general the script should be running out of the box without arguments if Cloud Watcher is installed in the default directory "C:/Program Files (x86)/AAG_CloudWatcher".

Please enable the options "Start & Connect" and "Connect & Record" in the Cloud Watcher Device settings in the Setup tab, so that it immeadiately starts to create and update the "aag_json.dat" file.

I am providing a compiled (.exe) tool in the [releases](https://github.com/ngaertner/aag_cloudwatcher_watchdog/releases) section, which includes the python runtime and all required libraries.


## USAGE

You can use the following command line arguments to configure the script:
```
usage: aag_cw_watchdog [-h] [--cw_path CW_PATH] [--out_path OUT_PATH] [--timeout TIMEOUT] [--log_dir LOG_DIR] [--log_file LOG_FILE] [--log_level {INFO,WARNING,ERROR}]

options:
  -h, --help                        show this help message and exit
  --cw_path CW_PATH                 Cloud Watcher Path (contains AAG_CloudWatcher.exe)
  --out_path OUT_PATH               Cloud Watcher Output Path (contains aag_json.dat)
  --timeout TIMEOUT                 Timeout to restart inactive Cloud Watcher in seconds - default 120s
  --log_dir LOG_DIR                 Directory to store Log Files
  --log_file LOG_FILE               Log Filename - default aag_cw_watchdog.log
  --log_level {INFO,WARNING,ERROR}  Log Level - default INFO
```

It is recommended to schedule the script using the Windows Task Scheduler.
- Start the Task Scheduler using keys "Windows + R" and enter "%windir%\system32\taskschd.msc /s"
- Create a new Task
- Select "Run wether user is logged on or not" and select "Run with highest privileges"
- Create a Trigger to execute the Task with a repeat interval of "1 Minute" and set a starting time and select to end the Task after "30 Minutes"
- Create an Action and point to the compiled .exe or the python file of the script (depending on your environment)

## DISCLAIMER

Please note that I have no affiliation whatsoever with Lunático Astronomía, S.L. ! 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

