"""
Logic regarding sequential bootstrapping from chapter 4.
"""

import pandas as pd
import numpy as np


def get_ind_matrix(bar_index, label_endtime):
    """
    Snippet 4.3, page 64, Build an Indicator Matrix
    Get indicator matrix
    :param bar_index: (pd.Series): Index of bars
    :param label_endtime: (pd.Series) Label endtime series (t1 for triple barrier events)
    :return: (pd.DataFrame) indicator binary matrix indicating what (price) bars influence the label for each observation
    """
    ind_mat = pd.DataFrame(0, index=bar_index, columns=range(label_endtime.shape[0]))  # zero indicator matrix
    for i, (t_0, t_1) in enumerate(label_endtime.iteritems()):
        ind_mat.loc[t_0:t_1, i] = 1
    return ind_mat


def _get_ind_mat_average_uniqueness(ind_mat):
    """
    Snippet 4.4. page 65, Compute Average Uniqueness
    Average uniqueness from indicator matrix

    :param ind_mat: (pd.Dataframe) indicator binary matrix
    :return: (float) average uniqueness
    """
    conc = ind_mat.sum(axis=1)  # concurrency
    unique = ind_mat.div(conc, axis=0)
    avg_unique = unique[unique > 0].mean()  # average uniqueness
    return avg_unique


def seq_bootstrap(triple_barrier_events, sample_length=None, compare=False):
    """
    Snippet 4.5, Snippet 4.6, page 65, Return Sample from Sequential Bootstrap
    Generate a sample via sequential bootstrap

    :param triple_barrier_events: (data frame) of events from labeling.get_events()
    :param sample_length: (int) Length of bootstrapped sample
    :param compare: (boolean) flag to print standard bootstrap uniqueness vs sequential bootstrap uniqueness
    :return: (array) of bootstrapped samples indexes
    """

    label_endtime = triple_barrier_events.t1

    bar_index = list(triple_barrier_events.index)  # generate index for indicator matrix from t1 and index
    bar_index.extend(triple_barrier_events.t1)
    bar_index = sorted(list(set(bar_index)))

    ind_mat = get_ind_matrix(bar_index, label_endtime)

    if sample_length is None:
        sample_length = ind_mat.shape[1]

    phi = []
    while len(phi) < sample_length:
        avg_unique = pd.Series()
        for i in ind_mat:
            ind_mat_reduced = ind_mat[phi + [i]]  # reduce ind_mat
            avg_unique.loc[i] = _get_ind_mat_average_uniqueness(ind_mat_reduced).iloc[-1]
        prob = avg_unique / avg_unique.sum()  # draw prob
        phi += [np.random.choice(ind_mat.columns, p=prob)]

    if compare is True:
        standard_indx = np.random.choice(ind_mat.columns, size=sample_length)
        standard_unq = _get_ind_mat_average_uniqueness(ind_mat[standard_indx]).mean()
        sequential_unq = _get_ind_mat_average_uniqueness(ind_mat[phi]).mean()
        print('Standard uniqueness: {}\nSequential uniqueness: {}'.format(standard_unq, sequential_unq))

    return phi
