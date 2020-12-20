#!/usr/bin/env python
# coding: utf-8

# In[ ]:

#from oracles_utils import obtain_rnd_samples, find_error_number
import numpy as np
#from o_utils import obtain_rnd_samples

def get_errors(trials_nb, shots, PD_model, PD_test,metric='jensenshannon'):
    Error_numbers = np.zeros(np.shape(PD_model)[0]).astype(float) 
    for i_trials in range(trials_nb):
        random_test = obtain_rnd_samples(shots, PD_test)
        Error_numbers += find_error_number(PD_model, random_test, metric)
    return list(Error_numbers)

def obtain_rnd_samples(size, PD): 
    nb_states = np.shape(PD)[0]
    nb_labels = np.shape(PD)[1]
    sample = np.ndarray((nb_states,nb_labels))
    for i_state in range(nb_states): # NB loop because p must be a 1D vector
        choice = np.random.default_rng().choice(nb_labels, size, p=PD[i_state,:]) 
        for i_label in range(nb_labels):
            sample[i_state,i_label] = np.count_nonzero(choice == i_label)
    sample = sample/sample.sum(axis=1, keepdims=True) # normalization
    return sample

from scipy.spatial.distance import cdist
def find_error_number(PD_model, PD_random, metric='jensenshannon'):
    # !this assumes for the moment a "the lower, the better" type of metric 
    Y = cdist(PD_random,PD_model,metric=metric)
    mA = np.shape(Y)[0]
    oracle_counts = np.zeros(mA)
    for i_mA in range(mA):
        if Y[i_mA,i_mA] > min(Y[i_mA, :]):
            oracle_counts[i_mA] = 1   
    return oracle_counts

from scipy.signal import savgol_filter
def provide_error_curve(PD_model, PD_test, trials=100, window=9,
                        epsilon = .0001, max_shots = 500,
                        pol=3, verbosality = -1, metric='jensenshannon'):
    safe_rate = 0.0 # stay at zero before being calculated
    curve = []
    errors = []
    for shots in range(1, max_shots):        
        en = get_errors(trials, shots, PD_model, PD_test,metric)
        error_rate = np.mean(en)/trials
        curve.append(error_rate)
        errors.append(en)
        if shots > window:
            errors.pop(0)
        if shots %verbosality == 0:
            print(shots, curve[shots-1],np.array(en).astype(int))
        if shots >= window:            
            fitted_tail = savgol_filter(errors, window, pol, axis=0)                   
            safe_rate= np.max(fitted_tail[int((window-1)/2),:])/trials 
            if  safe_rate <= epsilon:
                break
    return curve, safe_rate, errors
