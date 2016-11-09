import os
import sys
import utils
import lstm_plain
import numpy as np

def cost_function(W, x, y):
    xt = x[:, 0]
    yt = y[:, 0]
    xt = xt.reshape(len(xt), 1)
    yt = yt.reshape(len(yt), 1)
    ct, ht = xt, xt
    cost, grad, ht, ct = lstm_plain.cost_function(W, xt, yt, ht, ct, True)
    for t in range(1, x.shape[-1]):
        xt = x[:, t]
        yt = y[:, t]
        xt = xt.reshape(len(xt), 1)
        yt = yt.reshape(len(yt), 1)
        c, g, ht, ct = lstm_plain.cost_function(W, xt, yt, ht, ct, True)
        cost += c
        grad += g
    return cost, grad

def cost_function_full(W, X, Y):
    xt = X[:, 0, 0]
    yt = Y[:, 0, 0]
    xt = xt.reshape(len(xt), 1)
    yt = yt.reshape(len(yt), 1)
    ht, ct = xt, xt
    cost, grad, ht, ct = lstm_plain.cost_function(W, xt, yt, ht, ct, True)
    for p in range(1, X.shape[-1]):
        for t in range(1, X.shape[1]):
            xt = X[:, t, p]
            yt = Y[:, t, p]
            xt = xt.reshape(len(xt), 1)
            yt = yt.reshape(len(yt), 1)
            c, g, ht, ct = lstm_plain.cost_function(W, xt, yt, ht, ct, True)
            cost += c
            grad += g
    return cost, grad        



def forward_pass(W, x, y):
    xt = x[:, 0]
    yt = y[:, 0]
    xt = xt.reshape(len(xt), 1)
    yt = yt.reshape(len(yt), 1)
    ct, ht = xt, xt
    cost, yp, ht, ct = lstm_plain.forward_pass(W, xt, yt, ht, ct, True)
    # print yp
    for t in range(1, x.shape[-1]):
        print t
        xt = x[:, t]
        yt = y[:, t]
        xt = xt.reshape(len(xt), 1)
        yt = yt.reshape(len(yt), 1)
        cost, yp1, ht, ct = lstm_plain.forward_pass(W, xt, yt, ht, ct, True)
        yp = np.vstack((yp, yp1))
    return yp

def gradient_descent(input_size, output_size, memory_size, 
                     cost_function, inputs, labels, alpha, n_iter, W = None):
    if W is None:
       W = utils.init_weights(input_size, memory_size, output_size)
    eps = 1e-8
    beta1 = 0.9
    beta2 = 0.999

    m = np.zeros(W.shape)
    v = np.zeros(W.shape)
    n_cases = inputs.shape[-1]
    next_case = 0
    try:
        for iter in xrange(0, n_iter) or cost < 7:
            xt = inputs;
            yt = labels;
            # xt = inputs[:, :, next_case]
            # yt = labels[:, :, next_case]
            cost, grad = cost_function(W, xt, yt)
            m = beta1*m + (1-beta1)*grad
            v = beta2*v + (1-beta2)*(grad**2)
            m_c = m/(1 - beta1**(iter+1))
            v_c = v/(1 - beta2**(iter+1)) 
            W += - alpha * m_c / (np.sqrt(v_c) + eps)
            print 'Iteration %d | Case # %d | Cost: %g\n' % (iter+1, next_case, cost);
            next_case = (next_case + 1) % n_cases
            if iter % 100 == 0:
                np.savez('W_partial', W)
                # alpha /= 2.0
    except:
        np.savez('W_partial', W)
    return W

if __name__ == '__main__':
    D = np.load('data.npz')
    X = D['arr_0']
    Y = D['arr_1']
    n = X.shape[0]
    d = X.shape[0]
    m = Y.shape[0]
    X = np.delete(X, [3, 4], 2)
    Y = np.delete(Y, [3, 4], 2)
    W = np.load('W_partial.npz')['arr_0']
    W = gradient_descent(n, m, d, cost_function_full, X, Y, 0.001, 500000, W)
    np.savez('weights', W)    


