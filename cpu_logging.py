"""
CPU logging file
"""

import psutil
import logging
import argparse
import time
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=10)


def get_running_process_details(max_proc_num: int = 10, threshold: int = 10, fp = None) -> None:
    """
    :return:
    """
    logger.debug("checking")
    # Iterate over all running process
    i = 0
    for proc in psutil.process_iter():
        try:
            # Get process name & pid from process object.
            processName = proc.name()
            processID = proc.pid
            cpu_pct = proc.cpu_percent()
            mem = proc.memory_info().vms
            outline = f"{i}, {processName}, {processID}, {cpu_pct}, {mem}"
            logger.debug(outline)
            if cpu_pct > threshold:
                logger.warning(outline)
                fp.write(outline+"\n")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # logger.error(f"oops: {i}")
            pass
    return None



if __name__ == '__main__':
    logger.debug("mapping")
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--delay", default=10, type=int)
    parser.add_argument("-n", "--numproc", default=10, type=int)
    parser.add_argument("-t", "--threshold", default=10, type=int)
    parser.add_argument("-f", "--filename", default="cpu_log", type=str)
    options = parser.parse_args()
    #
    now_str = datetime.now().strftime("%Y-%m-%d")
    outfilename = f"{options.filename}_{now_str}.csv"
    logger.debug(f"file: {outfilename}")
    with open(outfilename, 'w') as f:
        #
        get_running_process_details(fp=f)
        time.sleep(options.delay)
        f.flush()





