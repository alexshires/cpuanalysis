#! /usr/bin/env python3
"""
Script to parse the CPU hog
* Alex Shires - 28-4-2020
"""
import logging
import os
import sys

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=20)


if __name__ == '__main__':
    logger.debug("arguments: %s", sys.argv)
    csvfile = sys.argv[1]
    logger.debug("analysing cpu performance from CSV: %s", csvfile)
    #
    if not os.path.exists(csvfile):
        logger.warning("file does not exist")
        exit()
    df = pd.read_csv(csvfile, parse_dates=['Timestamp'], dayfirst=True)
    df['CPU'] = df.CPU.astype(float)
    df['Process'] = df.Process.apply(lambda x: x.lower())
    # first plot - CPU usage over time
    cpu_ave = df.groupby('Timestamp').apply(lambda x: sum(x.CPU)) # / 400.
    # specific processes
    process_names = ["VShieldScanner", "CyOptics", "Microsoft", "Google", "Skype",
                     "snowagent", "jamfdaemon", 'pycharm',
                     "com.docker.hyperkit" , 'teams', 'windowserver']
    process_names = [x.lower() for x in process_names]
    # get anything else in the top ten
    # process_names += [ x.lower() for x in df.Process.value_counts().index[:10] ]
    # remove duplicates
    process_names = sorted(list(set(process_names)))

    df_dict = dict()
    for process_name in process_names:
        df_dict[process_name] = df[df['Process'] == process_name].groupby('Timestamp').apply(
            lambda x: sum(x.CPU)) # / 400.
        logger.warning(df_dict[process_name].shape)

    base, filename = os.path.split(csvfile)
    with PdfPages(f"cpu_analysis_of_{filename}.pdf") as pdf:
        # fig = plt.figure()
        cpu_ave.plot(label="Total")
        plt.xlabel("Time")
        plt.ylabel("total CPU usage (%)")
        plt.title("total CPU usage over time")
        plt.tight_layout()
        pdf.savefig()
        # timeseries
        plt.clf()
        for process_name in process_names:
            cpu_ave_data = df_dict[process_name]
            if cpu_ave_data.shape[0] == 0:
                continue
            else:
                cpu_ave_data.plot(label=process_name)
        plt.xlabel("Time")
        plt.ylabel("total CPU usage (%)")
        plt.legend()
        plt.title("Process CPU total")
        plt.tight_layout()
        pdf.savefig()
        # Rolling means
        plt.clf()
        for process_name in process_names:
            cpu_ave_data = df_dict[process_name].rolling(window=40).mean()
            if cpu_ave_data.shape[0] == 0:
                continue
            else:
                cpu_ave_data.plot(label=process_name)
        plt.xlabel("Time")
        plt.ylabel("total CPU usage (%)")
        plt.legend()
        plt.title("Process CPU average - rolling")
        plt.tight_layout()
        pdf.savefig()
        # 1D histograms
        plt.clf()
        for process_name in process_names:
            cpu_ave_data = df_dict[process_name]
            if cpu_ave_data.shape[0] == 0:
                continue
            cpu_ave_data.hist(bins=50, label=process_name, alpha=0.5)
        plt.xlabel("% CPU usage")
        plt.ylabel("frequency of usage")
        plt.legend()
        plt.title("Histogram of measuremnets")
        plt.tight_layout()
        pdf.savefig()
        # 2D histograms
        plt.clf()
        #
        for process_name in process_names:
            cpu_ave_data = df_dict[process_name]
            if cpu_ave_data.shape[0] == 0:
                continue
            cpu_ave_data.hist(bins=50, label=process_name, alpha=0.5)
            plt.xlabel(f"% CPU usage")
            plt.ylabel("frequency of usage")
            plt.legend()
            plt.title(f"Histogram of {process_name} measurements")
            pdf.savefig()
            plt.tight_layout()
            plt.clf()

        # for process_name1 in process_names:
        #     for process_name2 in process_names:
        #             if process_name1 == process_name2:
        #                 continue
        #             try:
        #                 cpu_ave_data1 = df_dict[process_name1]
        #                 cpu_ave_data2 = df_dict[process_name2]
        #                 if cpu_ave_data.shape[0] == 0:
        #                     continue
        #                 hist, xs, ys = np.histogram2d(cpu_ave_data1.values, cpu_ave_data2.values)
        #                 sns.heatmap(hist)
        #                 plt.xlabel(f"% CPU usage {process_name1}")
        #                 plt.ylabel(f"% CPU usage {process_name2}")
        #                 plt.legend()
        #                 plt.title("Histogram of correlated process measurements")
        #                 pdf.savefig()
        #             except Exception as e:
        #                 logger.error("failed with %s, %s with %s", process_name1, process_name2, e)
        plt.clf()