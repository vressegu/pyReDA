# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 14:18:28 2019

@author: matheus.ladvig
"""
import numpy as np
def fct_name_2nd_result(param,modal_dt,reconstruction):
    
    if param['a_time_dependant']:
        dependance_on_time_of_a = '_a_time_dependant_'
    else:
        dependance_on_time_of_a = '_a_cst_'
    
    if param['decor_by_subsampl']['bool']:
        if dependance_on_time_of_a == 'a_t':
            char_filter = '_on_' + str(param['type_filter_a'])
        else:
            char_filter = None
        
        if param['decor_by_subsampl']['choice_n_subsample'] == 'auto_shanon':
            if char_filter == None:
                param['name_file_2nd_result'] = param['folder_results'] + '\\' +'2ndresult_' + param['type_data'] + '_' + str(int(param['nb_modes'])) + \
                                            '_modes_' + dependance_on_time_of_a + \
                                            '_decor_by_subsampl_' + str(param['decor_by_subsampl']['meth']) + \
                                            '_choice_' + str(param['decor_by_subsampl']['choice_n_subsample']) + \
                                            '_threshold_' + str(param['decor_by_subsampl']['spectrum_threshold']) + \
                                            'fct_test_' + str(param['decor_by_subsampl']['test_fct'])
            else:
                param['name_file_2nd_result'] = param['folder_results'] + '2ndresult_' + param['type_data'] + '_' + str(int(param['nb_modes'])) + \
                                            '_modes_' + dependance_on_time_of_a + char_filter +\
                                            '_decor_by_subsampl_' + str(param['decor_by_subsampl']['meth']) + \
                                            '_choice_' + str(param['decor_by_subsampl']['choice_n_subsample']) + \
                                            '_threshold_' + str(param['decor_by_subsampl']['spectrum_threshold']) + \
                                            'fct_test_' + str(param['decor_by_subsampl']['test_fct'])
        
        elif param['decor_by_subsampl']['choice_n_subsample'] == 'auto_corr_time':
            if char_filter == None:
                param['name_file_2nd_result'] = param['folder_results'] + '2ndresult_' + param['type_data'] + '_' + str(int(param['nb_modes'])) + \
                                            '_modes_' + dependance_on_time_of_a + \
                                            '_decor_by_subsampl_' + str(param['decor_by_subsampl']['meth']) + \
                                            '_choice_' + str(param['decor_by_subsampl']['choice_n_subsample']) + \
                                            'fct_test_' + param['decor_by_subsampl']['test_fct']
                                            
            else:
                param['name_file_2nd_result'] = param['folder_results'] + '2ndresult_' + param['type_data'] + '_' + str(int(param['nb_modes'])) + \
                                            '_modes_' + dependance_on_time_of_a + char_filter + \
                                            '_decor_by_subsampl_' + str(param['decor_by_subsampl']['meth']) + \
                                            '_choice_' + str(param['decor_by_subsampl']['choice_n_subsample']) + \
                                            'fct_test_' + param['decor_by_subsampl']['test_fct']
            
    else:
        param['name_file_2nd_result'] = param['folder_results'] + '2ndresult_' + param['type_data'] + '_' + str(int(param['nb_modes'])) + \
                                        '_modes_' + dependance_on_time_of_a
                                        
                                        

    param['name_file_2nd_result'] = param['name_file_2nd_result'] + '_fullsto'
    
    
    if modal_dt == 1:
        param['name_file_2nd_result'] = param['name_file_2nd_result'] + '_modal_dt'
    elif modal_dt == 2:
        param['name_file_2nd_result'] = param['name_file_2nd_result'] + '_real_dt'
    
    if np.logical_not(param['adv_corrected']):
        param['name_file_2nd_result'] = param['name_file_2nd_result'] + '_no_correct_drift'
    
    if param['decor_by_subsampl']['no_subampl_in_forecast']:
        param['name_file_2nd_result'] = param['name_file_2nd_result'] + '_no_subampl_in_forecast'
    
    if reconstruction:
        param['reconstruction'] = True
        param['name_file_2nd_result'] = param['name_file_2nd_result'] + '_reconstruction'
    else:
        param['reconstruction'] = False
    
    
#    
#    np.savez(param['name_file_2nd_result']+'_Numpy',param['dX'])    
                                        
    return param
                                        
                                        
                                        
                                        
                                        
                                        
                                        
                                        
                                        
                                        
                                        
                                        
                                        
                                        
                                        
                                        
                                        
                                        