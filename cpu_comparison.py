#! /usr/bin/env python3
"""
Script to compare outputs of find-cpu-hogs.sh

Alex Shires
14-05-2020
"""
import logging
import os
import sys
from typing import Dict

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=10)

process_names = ["VShieldScanner", "CyOptics", "Microsoft", "Google", "Skype",
                 "snowagent", "jamfdaemon", 'pycharm',
                 "com.docker.hyperkit", 'teams', 'windowserver', 'mds_stores', 'kernel_task']
process_names = [x.lower() for x in process_names]


def get_file(csvfile: str) -> pd.DataFrame:
    """
    get data
    :param csvfile:
    :return:
    """
    #
    if not os.path.exists(csvfile):
        logger.warning("file does not exist")
        exit()
    df = pd.read_csv(csvfile, parse_dates=['Timestamp'], dayfirst=True)
    df['CPU'] = df.CPU.astype(float)
    df['Process'] = df.Process.apply(lambda x: x.lower())
    df = df[df.CPU > 20.]
    df.set_index('Timestamp', inplace=True)
    return df


def process_df(df: pd.DataFrame) -> Dict:
    """
    convert df into dict
    :param df:
    :return:
    """
    cpu_ave = df.groupby('Timestamp').apply(lambda x: sum(x.CPU))  # / 400.
    # specific processes
    # get anything else in the top ten
    # process_names += [ x.lower() for x in df.Process.value_counts().index[:10] ]
    # remove duplicates

    df_dict = dict()
    for process_name in process_names:
        tmp_df = df[df['Process'] == process_name].groupby('Timestamp').apply(
            lambda x: sum(x.CPU))  # / 400.
        logger.warning(tmp_df.shape) # df_dict[process_name].shape)
        #if tmp_df.shape[0] > 50:
        df_dict[process_name] = tmp_df
    print(df_dict.keys())
    return df_dict


if __name__ == '__main__':

    file1 = sys.argv[1]
    file2 = sys.argv[2]
    logger.debug(f"comparsiong {file1} and {file2}")

    df1 = get_file(file1)
    df2 = get_file(file2)


    df1_dict = process_df(df1)
    df2_dict = process_df(df2)

    legend1 = file1[:-4].split("_")[1]
    legend2 = file2[:-4].split("_")[1]

    with PdfPages(f"cpu_comparison_of_{legend1}_{legend2}.pdf") as pdf:
        for process_name in process_names:
            cpu_ave_data1 = df1_dict[process_name].rolling(window=40).mean()
            if cpu_ave_data1.shape[0] == 0:
                continue
            else:
                cpu_ave_data1.plot(label=process_name)
        plt.xlabel("Time")
        plt.ylabel("total CPU usage (%)")
        plt.legend()
        plt.title(f"Process CPU average - rolling {legend1}")
        plt.tight_layout()
        pdf.savefig()
        plt.clf()
        # rolling 2
        for process_name in process_names:
            cpu_ave_data2 = df2_dict[process_name].rolling(window=40).mean()
            if cpu_ave_data2.shape[0] == 0:
                continue
            else:
                cpu_ave_data2.plot(label=process_name)
        plt.xlabel("Time")
        plt.ylabel("total CPU usage (%)")
        plt.legend()
        plt.title(f"Process CPU average - rolling {legend2}")
        plt.tight_layout()
        pdf.savefig()
        plt.clf()
        # histograms
        for process_name in process_names:
            cpu_ave_data1 = df1_dict[process_name]
            cpu_ave_data2 = df2_dict[process_name]
            if cpu_ave_data1.shape[0] == 0 or cpu_ave_data2.shape[0] == 0:
                continue
            cpu_ave_data1.hist(bins=50, label=legend1, alpha=0.5, density=True)
            cpu_ave_data2.hist(bins=50, label=legend2, alpha=0.5, density=True)
            plt.xlabel(f"% CPU usage")
            plt.ylabel("frequency of usage")
            plt.legend()
            plt.title(f"Histogram of {process_name} measurements")
            pdf.savefig()
            plt.tight_layout()
            plt.clf()


