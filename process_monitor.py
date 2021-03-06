"""
Process monitor from
https://raw.githubusercontent.com/x4nth055/pythoncode-tutorials/master/general/process-monitor/process_monitor.py

USage:
python3 process_monitor.py --sort-by create_time -n 10
"""

import psutil
from datetime import datetime
import pandas as pd
import time
import os
# import ipdb
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(10)


def get_size(bytes):
    """
    Returns size of bytes in a nice format
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024


def get_processes_info():
    # the list the contain all process dictionaries
    processes = []
    for process in psutil.process_iter():
        # get all process info in one shot
        with process.oneshot():
            # get the process id
            pid = process.pid
            if pid == 0:
                # System Idle Process for Windows NT, useless to see anyways
                continue
            # get the name of the file executed
            name = process.name()
            # get the time the process was spawned
            try:
                create_time = datetime.fromtimestamp(process.create_time())
            except OSError:
                # system processes, using boot time instead
                create_time = datetime.fromtimestamp(psutil.boot_time())
            try:
                # get the number of CPU cores that can execute this process
                cores = len(process.cpu_affinity())
            except psutil.AccessDenied:
                cores = 0
            except AttributeError:
                cores = 0
            # get the CPU usage percentage
            try:
                cpu_usage = process.cpu_percent(interval=None)
            except psutil.ZombieProcess:
                # print("zombie")
                cpu_usage = 0
            # get the status of the process (running, idle, etc.)
            status = process.status()
            try:
                # get the process priority (a lower value means a more prioritized process)
                nice = int(process.nice())
            except psutil.AccessDenied:
                nice = 0
            except psutil.ZombieProcess:
                nice = 0
            try:
                # get the memory usage in bytes
                memory_usage = process.memory_full_info().uss
            except psutil.AccessDenied:
                memory_usage = 0
            except psutil.ZombieProcess:
                memory_usage = 0
            # total process read and written bytes
            io_counters = 0 # process.io_counters()
            read_bytes = 0 # io_counters.read_bytes
            write_bytes = 0 # io_counters.write_bytes
            # get the number of total threads spawned by this process
            try:
                n_threads = process.num_threads()
            except psutil.ZombieProcess:
                n_threads = 0
            # get the username of user spawned the process
            try:
                username = process.username()
            except psutil.AccessDenied:
                username = "N/A"
            except psutil.ZombieProcess:
                username = "N/A"
        # print(pid, name, cpu_usage)
        processes.append({
            'pid': pid, 'name': name, 'create_time': create_time,
            'cores': cores, 'cpu_usage': cpu_usage, 'status': status, 'nice': nice,
            'memory_usage': memory_usage, 'read_bytes': read_bytes, 'write_bytes': write_bytes,
            'n_threads': n_threads, 'username': username,
        })

    return processes


def construct_dataframe(processes):
    # convert to pandas dataframe
    df = pd.DataFrame(processes)
    # set the process id as index of a process
    df.set_index('pid', inplace=True)
    # print(df.head())
    # sort rows by the column passed as argument
    df.sort_values(by=["cpu_usage"], ascending=False, inplace=True) #  sort_by, inplace=True, ascending=not descending)
    logger.debug(df.describe())
    # pretty printing bytes
    df['memory_usage'] = df['memory_usage'].apply(get_size)
    df['write_bytes'] = df['write_bytes'].apply(get_size)
    df['read_bytes'] = df['read_bytes'].apply(get_size)
    # convert to proper date format
    df['create_time'] = df['create_time'].apply(datetime.strftime, args=("%Y-%m-%d %H:%M:%S",))
    # reorder and define used columns
    df = df[columns.split(",")]
    return df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process Viewer & Monitor")
    parser.add_argument("-c", "--columns", help="""Columns to show,
                                                available are name,create_time,cores,cpu_usage,status,nice,memory_usage,read_bytes,write_bytes,n_threads,username.
                                                Default is name,cpu_usage,memory_usage,read_bytes,write_bytes,status,create_time,nice,n_threads,cores.""",
                        default="name,cpu_usage,memory_usage,read_bytes,write_bytes,status,create_time,nice,n_threads,cores")
    parser.add_argument("-s", "--sort-by", dest="sort_by", help="Column to sort by, default is memory_usage .",
                        default="memory_usage")
    parser.add_argument("--descending", action="store_true", help="Whether to sort in descending order.")
    parser.add_argument("-n", help="Number of processes to show, will show all if 0 is specified, default is 25 .",
                        default=25)
    parser.add_argument("-u", "--live-update", action="store_true",
                        help="Whether to keep the program on and updating process information each second")
    parser.add_argument("-f", "--filename", default="cpu_log")
    parser.add_argument("-d", "--delay", default=10, type=int)
    parser.add_argument("-t", "--threshold", default=10, type=int)

    # parse arguments
    args = parser.parse_args()
    columns = args.columns
    sort_by = args.sort_by
    descending = args.descending
    n = int(args.n)
    live_update = args.live_update
    # print the processes for the first time
    processes = get_processes_info()
    df = construct_dataframe(processes)
    if n == 0:
        logger.debug(df.to_string())
    elif n > 0:
        logger.debug(df.head(n).to_string())
    # print continuously
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{args.filename}_{date_str}_logs.csv"
    subdf = df[df.cpu_usage > args.threshold]
    if not os.path.exists(filename) and subdf.shape[0] > 0:
        with open(filename, 'a+') as f:
            subdf.to_csv(path_or_buf=f, header=True)
    elif subdf.shape[0] > 0:
        with open(filename, 'a+') as f:
            subdf.to_csv(path_or_buf=f, header=False)
    continue_int = 0
    while live_update:
        # get all process info
        try:
            processes = get_processes_info()
            df = construct_dataframe(processes)
            # clear the screen depending on your OS
            os.system("cls") if "nt" in os.name else os.system("clear")
            if n == 0:
                logger.debug(df.to_string())
            elif n > 0:
                logger.debug(df.head(n).to_string())
            # write to CSV
            subdf = df[df.cpu_usage > args.threshold]
            if subdf.shape[0] > 0:
                with open(filename, 'a+') as f:
                    subdf.to_csv(path_or_buf=f, header=False)
            # ipdb.set_trace()
            time.sleep(15)
        except (psutil.AccessDenied, KeyError, ProcessLookupError, RuntimeError) as e:
            logger.error(e)
            time.sleep(1)
            continue_int += 1
            if continue_int > 100:
                break
            else:
                continue
