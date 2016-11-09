import os
import sys
import numpy as np

ORDER = 'C'

def flatten(A):
    A = np.ravel(A, order=ORDER)
    # A = A.flatten(1)
    return A.reshape(len(A), 1)

def init_params(n, d):
    r = np.sqrt(6)/np.sqrt(n+d+1)
    W = np.random.rand(n, d)*2*r - r
    return W

def init_weights(n, d, m):
    # weights = {}
    dim = 7*d**2 + 4*d*(n + 1) + m*(1 + d)
    W = np.zeros((dim, 1))
    start = 0
    end = d*n
    for c in ['i', 'f', 'c', 'o']:
        print "Wx%s: %d %d" % (c, start, end)
        # weights[c] = {}
        W[start:end] = flatten(init_params(d, n))
        start, end = end, end+d*d
        for p in ['h', 'c']:
            print "W%s%s: %d %d" % (p, c, start, end)
            add = True
            step = d*d
            if p == 'c':
                if c == 'c':
                    add = False
                    start, end = start-step, start 
                step = d*n
            if c == 'o':
                if p == 'c':
                    step = m*d
            if add:
                W[start:end] = flatten(init_params(d, d))
            start, end = end, end+step
    print "Why: %d %d" % (start, end)
    W[start:end] = flatten(init_params(m, d))
    return W

def unroll(V, d, n, partial=False):
    wx = V[0:d*n].reshape(d, n, order=ORDER)
    wh = V[d*n:d*n+d*d].reshape(d, d, order=ORDER)
    wc = None
    if not partial:
        wc = V[d*n+d*d:].reshape(d, d, order=ORDER)
    return wx, wh, wc

def logistic(z):
    return 1.0/(1+np.exp(-z))

def eval_num_grad(J, W):
    numgrad = np.zeros(W.shape)
    perturb = np.zeros(W.shape)
    e = 1e-6
    for p in range(0, len(W)):
        perturb[p] = e;
        loss1 = J(W - perturb)[0];
        loss2 = J(W + perturb)[0];
        numgrad[p] = (loss2 - loss1) / (2*e);
        perturb[p] = 0;
    return numgrad

    