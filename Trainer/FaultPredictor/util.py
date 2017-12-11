# ------------------------------------------------------------------------------
# 
#    Deep learning utilities.
#
#    Copyright (C) 2017 Pooya Ronagh
# 
# ------------------------------------------------------------------------------

import numpy as np
from builtins import range

def y2indicator(y, width):

    N = len(y)
    ind = np.matrix(np.zeros((N, width))).astype(np.int8)
    for i in range(N):
        assert(y[i] >= 0)
        ind[i, y[i]] = 1
    return ind

def vec_to_index(vec):

    return np.dot(vec, np.matrix(2**np.arange(vec.shape[1])[::-1]).transpose())

def perp(key):

    if (key=='X'):
        return 'Z'
    if (key=='Z'):
        return 'X'
    if (key=='errX3'):
        return 'errZ3'
    if (key=='errX4'):
        return 'errZ4'
    if (key=='errZ3'):
        return 'errX3'
    if (key=='errZ4'):
        return 'errX4'
    print('Error: Unrecognized key for perp module!')

def raise_ten(elt):

    return 10**elt

def int_times_ten(elt):

    return int(10 * elt)

def identity(elt):

    return elt

def activation_category(elt):

    if (elt < 1):
        return 'id'
    if (elt < 2):
        return 'relu'
    if (elt < 3):
        return 'sigmoid'
    if (elt < 4):
        return 'tanh'
    raise Exception('Activation function not determined.')

def boolean_category(elt):

    if (elt < 1):
        return True
    if (elt < 2):
        return False
    raise Exception('Truth value not determined.')

def cyc_pick(vec, beg, num_rows):

    total_num_rows= np.shape(vec)[0]
    end= (beg + num_rows) % total_num_rows
    if not end: end = None
    if (beg < end):
        return vec[beg:end]
    return np.concatenate((vec[beg:], vec[:end]), axis=0)
