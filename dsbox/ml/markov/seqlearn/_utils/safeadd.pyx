# Copyright 2013 Lars Buitinck / University of Amsterdam

import cython

import numpy as np
from scipy.sparse import isspmatrix_csc, isspmatrix_csr

cimport numpy as cnp
cnp.import_array()


@cython.boundscheck(False)
@cython.wraparound(False)
def safe_add(cnp.ndarray[ndim=2, dtype=cnp.float64_t] A, B):
    """A += B where B is a sparse (CSR or CSC) matrix.

    __rsub__ on a sparse matrix densifies prior to subtracting, making it
    unacceptably slow.

    Only dtype=np.float64 is supported, and shapes are not checked.
    """

    cdef:
        cnp.ndarray[ndim=1, dtype=cnp.float64_t, mode="c"] data
        cnp.ndarray[ndim=1, dtype=int, mode="c"] indices
        cnp.ndarray[ndim=1, dtype=int, mode="c"] indptr

        int i, j, jj

    if isinstance(B, np.ndarray):
        A += B
        return

    if isspmatrix_csc(B):
        A = A.T
    elif not isspmatrix_csr(B):
        raise TypeError("Type {0} not supported.".format(type(B)))

    data = B.data
    indices = B.indices
    indptr = B.indptr

    for i in range(A.shape[0]):
        for jj in range(indptr[i], indptr[i + 1]):
            j = indices[jj]
            A[i, j] += data[jj]
