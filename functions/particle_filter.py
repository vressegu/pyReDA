# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 16:18:00 2019

@author: matheus.ladvig
"""
import numpy as np
import collections
from evol_forward_bt_MCMC import evol_forward_bt_MCMC
from scipy import optimize



def resample(weigths):
    
    
    
    
    nb_weigths = weigths.shape[0]
    if np.sum(weigths) < 1:
        weigths[-1] = weigths[-1] + (1 - np.sum(weigths))
    
    indexes = np.random.choice(nb_weigths,nb_weigths, p=weigths)
    
    return indexes
    
def calculate_effective_sample_size(weigths):
    
    
    return 1/np.sum(np.power(weigths,2))
    
    
def f(x,*params):
    likelihood,N_threshold,phi = params
    
    likeli_i = np.power(likelihood,(x-1+phi))
    weigths = likeli_i/np.sum(likeli_i)
    ess= 1/np.sum(np.power(weigths,2))
    
    
    return np.abs(ess-N_threshold)
#    return (np.sum(np.power(likelihood,2*(x-1+phi)))/np.power(np.sum(np.power(likelihood,(x-1+phi))),2) - 1/N_threshold)
    
def find_tempering_coeff(likelihood,N_threshold,phi):
    low_inter = 1 - phi
    high_inter = 1
 
    params = (likelihood,N_threshold,phi)
    rranges = (slice(low_inter,high_inter),)
    resbrute = optimize.brute(f, ranges=rranges, args=params, full_output=True,  finish=optimize.fmin)
    
#    print(resbrute[0])
    return resbrute[0][0]

def calculate_champs_likelihood(particles_chronos,obs_K,phi,Hr_K):
    
    
    
    likeli = np.zeros(shape=particles_chronos.shape[1])
    values = np.zeros(shape=particles_chronos.shape[1])
    
    
    particles_chronos = np.vstack((particles_chronos,np.ones((1,particles_chronos.shape[1]))))
    
    a = obs_K @ particles_chronos
    c = np.einsum('ij,ji->i', (particles_chronos.T @ Hr_K), particles_chronos) 
    values = -2*a + c
    
    values = -0.5*phi*values
        
    explosures = np.isinf(values)
    if np.any(explosures):
        print('EXPLOSED: Recalculating weigths')
        
        likeli[explosures] = 5
        likeli[np.logical_not(explosures)] = 1
    
    else:  
        
        b = values-np.max(values)
        
#        c = teste-np.max(teste)
        
        likeli = np.exp(90)*np.exp(b)   
        
#        likeli_teste = np.exp(90)*np.exp(c)
        
        

    return likeli



def propagate_all_particles(particles_past_original,noises_accepted_original, dt, I,L,C,delta_t,pho,pchol_cov_noises,dt_adapted ):
    
   
    bt_all_particles = particles_past_original # 6 x nb_particles
    noises_updated = np.zeros(shape=noises_accepted_original.shape) # time x 42 x nb_particles
    
    for time in range(delta_t-1):
        
        bt_all_particles,noise_time_n = evol_forward_bt_MCMC(I,L,C, pchol_cov_noises, dt,bt_all_particles,0,0,True,noises_accepted_original[time,...],pho)
        
        noises_updated[time,...] = noise_time_n
        
    
    time = delta_t-1
    bt_all_particles,noise_time_n = evol_forward_bt_MCMC(I,L,C, pchol_cov_noises,dt_adapted,bt_all_particles,0,0,True,noises_accepted_original[time,...],pho)
    noises_updated[time,...] = noise_time_n
    
    
    return bt_all_particles,noises_updated



def calculate_acceptance_prob_champ_all_particles_and_sample(particles_candidate,particles_accepted,obs_K,Hr_K,noises,noises_candidate):
    
    particles_candidate = np.vstack((particles_candidate,np.ones((1,particles_candidate.shape[1]))))
    particles_accepted = np.vstack((particles_accepted,np.ones((1,particles_accepted.shape[1]))))
    particles_chronos = np.concatenate((particles_accepted,particles_candidate),axis=1)
    
    
    
    values = (-2*obs_K @ particles_chronos + np.einsum('ij,ji->i', (particles_chronos.T @ Hr_K), particles_chronos))[0,:]
      
    value_accepted = values[:int(len(values)/2)]
    value_candidate = values[int(len(values)/2):]
    delta_value = value_candidate-value_accepted
    ratio = np.exp(-0.5*(delta_value))
    prob = np.minimum(np.ones(len(ratio)),ratio)
    
    
    particles_final = np.zeros((particles_candidate.shape[0]-1,particles_candidate.shape[1]))
    noise_final = np.zeros(noises.shape)
    for i in range(len(prob)):
        if np.random.uniform(0,1)<prob[i]:

            particles_final[:,i] = particles_candidate[:-1,i]
            noise_final[...,i] = noises_candidate[...,i]
            
        else:
            particles_final[:,i] = particles_accepted[:-1,i]
            noise_final[...,i] = noises[...,i]
            
    
    
    
    return particles_final,noise_final


def particle_filter(ILC_a_cst,obs,K,Hpiv_K,particles_chronos,N_threshold,noises,particles_past,nb_mutation_steps,dt_original,\
                    dt_adapted,pho,delta_t,pchol_cov_noises,time_):
    
    
    I = ILC_a_cst['I']  
    L = ILC_a_cst['L']
    C = ILC_a_cst['C']    
    
    obs_K = obs.T @ K 
    likelihood = calculate_champs_likelihood(particles_chronos,obs_K,1,Hpiv_K)
#    likelihood = np.ones(particles_chronos.shape[1])
    
##    weigths = likelihood/np.sum(likelihood)
##    ess = calculate_effective_sample_size(weigths)

    if (nb_mutation_steps == -1): # No tempering / mutation
        
        weigths = (likelihood/np.sum(likelihood))[0,:]

        index_print = np.where((weigths>0.05))
        ess = calculate_effective_sample_size(weigths)
        print('  > indexes with more than 5% probability of sampling: '+ str(index_print[0]))
        print('  > ESS: '+ str(ess))
        
#        if (ess <= N_threshold):
#            #### Resampling
#            indexes = resample(weigths)
#            particles_chronos = particles_chronos[:,indexes]
        
        #### Resampling
        indexes = resample(weigths)
        particles_chronos = particles_chronos[:,indexes]
                
        return particles_chronos

    
    r = 0
    phi = 1
    phi_guime = 0
    
    while (r<10): # Tempering loop
        
        
        if (phi_guime>0.95): # End of the tempering (phi close to 0)
            index_print = np.where((weigths>0.05))
#            print('indexes with more than 5% probability of sampling: '+ str(index_print[0]))
#            print('phi guime: '+ str(phi_guime))
            
            phi = 1
            phi_guime = 1
#            print(len(collections.Counter(indexes).keys()))  
#            print('Number of temp iter: '+str(r))
            print('\n')
            
            return particles_chronos
        
        else:
#            likelihood = calculate_likelihood(particles,obs,lambda_values,beta_1,1)
            if r>0:
                likelihood = calculate_champs_likelihood(particles_chronos,obs_K,1,Hpiv_K)
            phi_guime = find_tempering_coeff(likelihood,N_threshold,phi)
            if phi_guime>0.99:
                phi_guime = 0.99
                
            
            print('                    -- Time : '+str(time_)+' sec --                  ')
            print('                    -- Tempering number '+str(r+1)+' --                ')
            print('phi guime: '+ str(phi_guime))
            

        print('phi effective:' + str(phi_guime-1+phi))
#        likelihood = calculate_likelihood(particles,obs,lambda_values,beta_1,phi_guime-1+phi)
        likelihood = calculate_champs_likelihood(particles_chronos,obs_K,phi_guime-1+phi,Hpiv_K)
#        likelihood = np.power(likelihood,(phi_guime-1+phi))
#        print(likelihood)
        weigths = (likelihood/np.sum(likelihood))[0,:]
        
        index_print = np.where((weigths>0.05))
        ess = calculate_effective_sample_size(weigths)
        print('indexes with more than 5% probability of sampling: '+ str(index_print[0]))
        print('ESS: '+ str(ess))

        indexes = resample(weigths)
        
        #### Resampling
        noises = noises[...,indexes]
        particles_chronos = particles_chronos[:,indexes]
        particles_past = particles_past[:,indexes]
        
        
        print('\n')
        print('                         ... Mutation ...                           ')
        print('\n')
        for mutation in range(nb_mutation_steps): # Mutation loop
            particles_candidates,noises_candidate = propagate_all_particles(particles_past, noises, dt_original, I,L,C,delta_t,pho,pchol_cov_noises,dt_adapted )
##            calculate accept prob all and sample
            particles_chronos,noises= calculate_acceptance_prob_champ_all_particles_and_sample(particles_candidates,particles_chronos,obs_K,Hpiv_K,\
                                                                                                noises,noises_candidate)
        
        
        phi = 1 - phi_guime
        r += 1
        
     
        print('-----------------------------------------------------------')
        
        
   
    
    print('\n')
    
    
    return particles_chronos
    
    


    
    
    
    
    
    
    
    









    
    
    
    
    
