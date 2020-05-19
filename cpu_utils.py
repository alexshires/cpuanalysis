#! /usr/bin/env python3
"""
Script to compare outputs of find-cpu-hogs.sh

common utils

import pandas as pd

Alex Shires
14-05-2020
"""

import logging
import os
import sys
from typing import Dict

import pandas as pd


logger = logging.getLogger(__name__)
logging.basicConfig(level=10)

process_names = ["VShieldScanner", "CyOptics", "Microsoft", "Google", "Skype",
                 "snowagent", "jamfdaemon", 'pycharm',
                 "com.docker.hyperkit", 'teams', 'windowserver', 'mds_stores', 'kernel_task', 'AgentService']
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
    df.sort_index(inplace=True)
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