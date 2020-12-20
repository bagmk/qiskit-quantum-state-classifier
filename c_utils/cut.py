#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import numpy as np
import time
import copy
from qiskit import transpile

def circuit_builder(Circuit, q_list, state_1, state_2):
    if state_1 == "GHZ":
        Circuit.h(q_list[0])
        Circuit.cx(q_list[0],q_list[1])
        Circuit.cx(q_list[1],q_list[2])
    
    
    elif state_1[0] == "W": 
        Circuit.x(q_list[2])                        
        Circuit.ry(-0.955316618124509, q_list[1])
        Circuit.cz(q_list[2],q_list[1])           
        Circuit.ry(0.955316618124509, q_list[1])            
        Circuit.ry(-np.pi/4, q_list[0])      
        Circuit.cz(q_list[1],q_list[0])
        Circuit.ry(np.pi/4, q_list[0])                                   
        Circuit.cx(q_list[0],q_list[1])
        Circuit.cx(q_list[0],q_list[2])
        Circuit.cx(q_list[1],q_list[2])
    
    if state_1[1:] == "bar":
        Circuit.x(q_list[0])
        Circuit.x(q_list[1])
        Circuit.x(q_list[2])
    
    # common for Phi+ and Phi+ states:
    Circuit.h(q_list[3])
    Circuit.cx(q_list[3],q_list[4])            
   
    if state_2 == "Psi+":
        Circuit.x(q_list[4])
    return Circuit

def add_barrier_and_measure(Circuit, q_list):
        Circuit.barrier()
        Circuit.measure(q_list,q_list)
        return Circuit

def prepare_circuits(qubit_list,cqi_list, circ_ori, nb_trials, level, seed_trans, device, coupling_map, nb_id_gates=0, verbose=False):
    
    #version with a limit of trials
   
    start_time = time.strftime('%d/%m/%Y %H:%M:%S')    
    print("Start at DMY: ",start_time)
    
    summary_dic = {}
        
    for cqi in cqi_list:
        circuit = copy.deepcopy(circ_ori[cqi])
        if nb_id_gates > 0:
            circuit.barrier()
            for id_nb_id_gates in range(nb_id_gates):
                for index, value in enumerate(qubit_list):
                    circuit.id(value)
        add_barrier_and_measure(circuit, qubit_list)
        summary = []        
        depth_list = []
        count_run = 0
        max_count_run = nb_trials * 3
        break_flag = False
        for j in range(nb_trials):
                        
            if seed_trans != None:
                seed_transpiler=seed_trans[j*len(cqi_list)+1]
            else:
                seed_transpiler = None
                        
            new_depth = 0
                
            while not break_flag and (new_depth == 0 or depth_list.count(new_depth) != 0): 
                
                Q_state_opt_new = transpile(circuit, backend=device,
                                    coupling_map = coupling_map,
                                    seed_transpiler=seed_transpiler,
                                    optimization_level=level,
                                    initial_layout=qubit_list)

                new_depth = Q_state_opt_new.depth()
                if count_run == 0:
                    to_insert = {"depth": new_depth, 'circuit':Q_state_opt_new}
                count_run += 1
                if count_run == max_count_run:
                        break_flag = True
                                
            if not break_flag:
                depth_list.append(new_depth)            
                summary.append({"depth": new_depth, 'circuit':Q_state_opt_new})
            
            if break_flag:
                len_list = len(depth_list)
                for i_trial in range(nb_trials - len_list):
                        summary.insert(0, to_insert)
                break
            
        time_exp = time.strftime('%d/%m/%Y %H:%M:%S')    
        if verbose:
            print("%2i" % cqi,"DMY: ",time_exp)
            
        summary_dic[cqi] = summary 
    
    end_time = time.strftime('%d/%m/%Y %H:%M:%S')  
    print("Completed at DMY: ",end_time)    
    return summary_dic

