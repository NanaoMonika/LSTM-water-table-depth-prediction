#!usr/bin/env python
#-*- coding:utf-8 -*-



import numpy as np
import theano
import theano.tensor as T
from theano.ifelse import ifelse
from theano.tensor.shared_randomstreams import RandomStreams
from collections import OrderedDict
import copy
import sys


def floatX(X):
    return np.asarray(X, dtype=theano.config.floatX)


def random_weights(shape, name=None):
    # return theano.shared(floatX(np.random.randn(*shape) * 0.01), name=name)
    return theano.shared(floatX(np.random.uniform(size=shape, low=-1, high=1)), name=name)


def random_weights4eva(shape, name=None):
    # return theano.shared(floatX(np.random.randn(*shape) * 0.01), name=name)
    return theano.shared(floatX(np.random.uniform(size=shape, low=-1, high=1)), name=name)


def random_weights4wd(shape, name=None):
    # return theano.shared(floatX(np.random.randn(*shape) * 0.01), name=name)
    return theano.shared(floatX(np.random.uniform(size=shape, low=-1, high=1)), name=name)



def zeros(shape, name=""):
    return theano.shared(floatX(np.zeros(shape)), name=name)



def softmax(X, temperature=1.0):
    e_x = T.exp((X - X.max(axis=1).dimshuffle(0, 'x')) / temperature)   # dimshuffle(0, 'x') output 2 dim array
    return e_x / e_x.sum(axis=1).dimshuffle(0, 'x') # dimshuffle(0, 'x') output 2 dim array



def sigmoid(X):
    return 1 / (1 + T.exp(-X))



def dropout(X, dropout_prob=0.0):
    retain_prob = 1 - dropout_prob
    srng = RandomStreams(seed=1234)
    X *= srng.binomial(X.shape, p=retain_prob, dtype=theano.config.floatX)
    X /= retain_prob
    return X

# def dropout(x, dropout_prob):
#     if dropout_prob < 0. or dropout_prob > 1.:
#         raise Exception('Dropout level must be in interval [0, 1]')
#     retain_prob = 1. - dropout_prob
#     sample=np.random.binomial(n=1, p=retain_prob, size=x.shape)
#     x *= sample
#     x /= retain_prob
#     return x



def rectify(X):
    return T.maximum(X, 0.)



def clip(X, epsilon):
    return T.maximum(T.minimum(X, epsilon), -1*epsilon)



def scale(X, max_norm):
    curr_norm = T.sum(T.abs_(X))
    return ifelse(T.lt(curr_norm, max_norm), X, max_norm * (X / curr_norm))


def SGD(loss, params, learning_rate, lambda2=0.05):
    # problem in update
    # updates = {}
    # grads have no value??
    updates = OrderedDict()
    grads = T.grad(cost=loss, wrt=params)

    for p, g in zip(params, grads):
        # updates.append([p, p-learning_rate*(g+lambda2*p)])  # lambda*p regulzation
        updates[p] = p - learning_rate * (g + lambda2 * p)
    return updates, grads



def momentum(loss, params, caches, learning_rate=0.1, rho=0.1, clip_at=0.0, scale_norm=0.0, lambda2=0.0):
    updates = OrderedDict()
    grads = T.grad(cost=loss, wrt=params)

    for p, c, g in zip(params, caches, grads):
        if clip_at > 0.0:
            grad = clip(g, clip_at) 
        else:
            grad = g

        if scale_norm > 0.0:
            grad = scale(grad, scale_norm)

        delta = rho * grad + (1-rho) * c
        updates[p] = p - learning_rate * (delta + lambda2 * p)

    return updates, grads




def get_params(layers):
    params = []
    for layer in layers:
        for param in layer.get_params():
            params.append(param)
    return params



def make_caches(params):
    caches = []
    for p in params:
        caches.append(theano.shared(floatX(np.zeros(p.get_value().shape))))
    return caches


def one_step_updates(layers):
    updates = []

    for layer in layers:
        updates += layer.updates()

    return updates


