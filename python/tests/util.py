from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import pandas as pd
from six.moves import xrange


def generate_random_df(n_seqs,
                       max_seq_length,
                       unique_times=True,
                       starttimes_min=0,
                       starttimes_max=0):
    """ generates random dataframe for testing.
    :param df: pandas dataframe with columns
      * `id`: integer
      * `t`: integer
      * `dt`: integer mimmicking a global event time
      * `t_ix`: integer contiguous user time count per id 0,1,2,..
      * `t_elapsed`: integer the time from starttime per id ex 0,1,10,..
      * `event`: 0 or 1
      * `int_column`: random data
      * `double_column`: dandom data
    :param unique_times: whether there id,elapsed_time has only one obs. Default true
    :param starttimes_min: integer to generate `dt` the absolute time
    :param starttimes_max: integer to generate `dt` the absolute time
    """

    seq_lengths = np.random.randint(max_seq_length, size=n_seqs) + 1
    id_list = []
    t_list = []
    dt_list = []

    if starttimes_min < starttimes_max:
        starttimes = np.sort(np.random.randint(
            low=starttimes_min, high=starttimes_max, size=n_seqs))
    else:
        starttimes = np.zeros(n_seqs)

    for s in xrange(n_seqs):
        # Each sequence is consists of n_obs in the range 0-seq_lengths[s]
        n_obs = np.sort(np.random.choice(
            seq_lengths[s], 1, replace=False)) + 1

        # Each obs occurred at random times
        t_elapsed = np.sort(np.random.choice(
            seq_lengths[s], n_obs, replace=not unique_times))

        # there's always an obs at the assigned first and last timestep for
        # this seq
        if seq_lengths[s] - 1 not in t_elapsed:
            t_elapsed = np.append(t_elapsed, seq_lengths[s] - 1)
        if 0 not in t_elapsed:
            t_elapsed = np.append(t_elapsed, 0)

        t_elapsed = np.sort(t_elapsed)

        id_list.append(np.repeat(s, repeats=len(t_elapsed)))
        dt_list.append(starttimes[s] + t_elapsed)
        t_list.append(t_elapsed)

    # unlist to one array
    id_column = [item for sublist in id_list for item in sublist]
    dt_column = [item for sublist in dt_list for item in sublist]
    t_column = [item for sublist in t_list for item in sublist]
    del id_list, dt_list, t_list

    # do not assume row indicates event!
    event_column = np.random.randint(2, size=len(t_column))
    int_column = np.arange(len(event_column)).astype(int)
    double_column = np.random.uniform(high=1, low=0, size=len(t_column))

    df = pd.DataFrame({'id': id_column,
                       'dt': dt_column,
                       't_elapsed': t_column,
                       'event': event_column,
                       'int_column': int_column,
                       'double_column': double_column
                       })

    df['t_ix'] = df.groupby(['id'])['t_elapsed'].rank(
        method='dense').astype(int) - 1
    df = df[['id', 'dt', 't_ix', 't_elapsed',
             'event', 'int_column', 'double_column']]
    df = df.reset_index(drop=True)

    return df

def generate_weibull(A, B, C, shape, discrete_time):
    # Generate Weibull random variables
    W = np.sort(A * np.power(-np.log(np.random.uniform(0, 1, shape)), 1 / B))

    if discrete_time:
        C = np.floor(C)
        W = np.floor(W)

    U = np.less_equal(W, C) * 1.
    Y = np.minimum(W, C)
    return W, Y, U
