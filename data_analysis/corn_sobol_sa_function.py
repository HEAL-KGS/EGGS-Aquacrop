#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 19:26:14 2023

@author: wayne
"""

!pip install aquacrop==2.2
!pip install numba==0.55
!pip install statsmodels==0.13.2
!pip install SALib
from SALib.analyze import sobol
from SALib.sample import saltelli
from SALib.test_functions import Ishigami
from SALib.util import read_param_file

from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, IrrigationManagement
from aquacrop import Crop
from os import chdir, getcwd
import pickle 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms


wd=getcwd() # set working directory
chdir(wd)
corn_params = read_param_file(wd+"/data/sa_params/CornSA_GMD4_WNdlovu_v1_20230125.txt") # read in corn parameters

# parameter names
param_names = dict((k, corn_params[k]) for k in ['names'] # get key with names
           if k in corn_params)
param_names = param_names.get('names') # get values from names dictionary


# influential parameters from morris method
with open(wd+'/data/analysis_results/sensitivity_analysis_runs/ks_irrig_corn_morris_r4.pickle', 'rb') as mi: 
    influ_morris_irrig_full = pickle.load(mi)
  
    
influ_morris_irrig = [item[1:2]  + item[3:] for item in influ_morris_irrig_full]  # the influential parameters dataframes
 

with open(wd+'/data/analysis_results/sensitivity_analysis_runs/ks_rainfed_corn_morris_r4.pickle', 'rb') as mr: 
    influ_morris_rainfed_full = pickle.load(mr)

influ_morris_rainfed = [(item[1],) for item in influ_morris_rainfed_full] # the influential parameters dataframes

# meteorological
with open(wd+'/data/hydrometeorology/gridMET/ks_gridMET.pickle', 'rb') as met: 
    gridMET_county = pickle.load(met)
   
    
with open(wd+'/data/groupings/ks_ccm.pickle', 'rb') as info: 
    grouped_info = pickle.load(info)   


sher_gridMET = gridMET_county[10]
sher_gridMET = sher_gridMET.assign(year = sher_gridMET['Date'].dt.year) # create year variable


# soils
with open(wd+'/data/agricLand/soils/ks_soil.pickle', 'rb') as sl: 
    soil_data = pickle.load(sl) 
    
 
custom_soil = []
for soil_df in soil_data:
   for i, row in soil_df.iterrows():   #soil_df.itertuples():
        ids = soil_df['UID'][i] #create soil_df with UID from the soils file used - fix this
        #id_list.append(ids)
        if row['depth_cm'] == "0-5":
            pred_thWP_5 = ((-0.024*((soil_df['sand_prc'][i])/100))) + ((0.487*((soil_df['clay_prc'][i])/100))) + ((0.006*((soil_df['om'][i])/100))) + ((0.005*((soil_df['sand_prc'][i])/100))*((soil_df['om'][i])/100))- ((0.013*((soil_df['clay_prc'][i])/100))*((soil_df['om'][i])/100))+ ((0.068*((soil_df['sand_prc'][i])/100))*((soil_df['clay_prc'][i])/100))+ 0.031
            wp_5 = pred_thWP_5 + (0.14 * pred_thWP_5) - 0.02
            pred_thFC_5 = ((-0.251*((soil_df['sand_prc'][i])/100))) + ((0.195*((soil_df['clay_prc'][i])/100)))+ ((0.011*((soil_df['om'][i])/100))) + ((0.006*((soil_df['sand_prc'][i])/100))*((soil_df['om'][i])/100))- ((0.027*((soil_df['clay_prc'][i])/100))*((soil_df['om'][i])/100))+ ((0.452*((soil_df['sand_prc'][i])/100))*((soil_df['clay_prc'][i])/100))+ 0.299
            fc_5 = pred_thFC_5 + (1.283 * (np.power(pred_thFC_5, 2))) - (0.374 * pred_thFC_5) - 0.015
            #fc = pred_thFC + (1.283 * (pred_thFC*pred_thFC)) - (0.374 * pred_thFC) - 0.015
            ts_5 =soil_df["thetaS_m3m3"][i]
            ks_5=(soil_df['Ksat_cmHr'][i])*240
        if row['depth_cm'] == "5-15":
            pred_thWP_15 = ((-0.024*((soil_df['sand_prc'][i])/100))) + ((0.487*((soil_df['clay_prc'][i])/100))) + ((0.006*((soil_df['om'][i])/100))) + ((0.005*((soil_df['sand_prc'][i])/100))*((soil_df['om'][i])/100))- ((0.013*((soil_df['clay_prc'][i])/100))*((soil_df['om'][i])/100))+ ((0.068*((soil_df['sand_prc'][i])/100))*((soil_df['clay_prc'][i])/100))+ 0.031
            wp_15 = pred_thWP_15 + (0.14 * pred_thWP_15) - 0.02
            pred_thFC_15 = ((-0.251*((soil_df['sand_prc'][i])/100))) + ((0.195*((soil_df['clay_prc'][i])/100)))+ ((0.011*((soil_df['om'][i])/100))) + ((0.006*((soil_df['sand_prc'][i])/100))*((soil_df['om'][i])/100))- ((0.027*((soil_df['clay_prc'][i])/100))*((soil_df['om'][i])/100))+ ((0.452*((soil_df['sand_prc'][i])/100))*((soil_df['clay_prc'][i])/100))+ 0.299
            fc_15 = pred_thFC_15 + (1.283 * (np.power(pred_thFC_15, 2))) - (0.374 * pred_thFC_15) - 0.015
            #fc = pred_thFC + (1.283 * (pred_thFC*pred_thFC)) - (0.374 * pred_thFC) - 0.015
            ts_15 =soil_df["thetaS_m3m3"][i]
            ks_15=(soil_df['Ksat_cmHr'][i])*240
        if row['depth_cm'] == "15-30":
            pred_thWP_30 = ((-0.024*((soil_df['sand_prc'][i])/100))) + ((0.487*((soil_df['clay_prc'][i])/100))) + ((0.006*((soil_df['om'][i])/100))) + ((0.005*((soil_df['sand_prc'][i])/100))*((soil_df['om'][i])/100))- ((0.013*((soil_df['clay_prc'][i])/100))*((soil_df['om'][i])/100))+ ((0.068*((soil_df['sand_prc'][i])/100))*((soil_df['clay_prc'][i])/100))+ 0.031
            wp_30 = pred_thWP_30 + (0.14 * pred_thWP_30) - 0.02
            pred_thFC_30 = ((-0.251*((soil_df['sand_prc'][i])/100))) + ((0.195*((soil_df['clay_prc'][i])/100)))+ ((0.011*((soil_df['om'][i])/100))) + ((0.006*((soil_df['sand_prc'][i])/100))*((soil_df['om'][i])/100))- ((0.027*((soil_df['clay_prc'][i])/100))*((soil_df['om'][i])/100))+ ((0.452*((soil_df['sand_prc'][i])/100))*((soil_df['clay_prc'][i])/100))+ 0.299
            fc_30 = pred_thFC_30 + (1.283 * (np.power(pred_thFC_30, 2))) - (0.374 * pred_thFC_30) - 0.015
            #fc = pred_thFC + (1.283 * (pred_thFC*pred_thFC)) - (0.374 * pred_thFC) - 0.015
            ts_30 =soil_df["thetaS_m3m3"][i]
            ks_30=(soil_df['Ksat_cmHr'][i])*240
        if row['depth_cm'] == "30-60":
            pred_thWP_60 = ((-0.024*((soil_df['sand_prc'][i])/100))) + ((0.487*((soil_df['clay_prc'][i])/100))) + ((0.006*((soil_df['om'][i])/100))) + ((0.005*((soil_df['sand_prc'][i])/100))*((soil_df['om'][i])/100))- ((0.013*((soil_df['clay_prc'][i])/100))*((soil_df['om'][i])/100))+ ((0.068*((soil_df['sand_prc'][i])/100))*((soil_df['clay_prc'][i])/100))+ 0.031
            wp_60 = pred_thWP_60 + (0.14 * pred_thWP_60) - 0.02
            pred_thFC_60 = ((-0.251*((soil_df['sand_prc'][i])/100))) + ((0.195*((soil_df['clay_prc'][i])/100)))+ ((0.011*((soil_df['om'][i])/100))) + ((0.006*((soil_df['sand_prc'][i])/100))*((soil_df['om'][i])/100))- ((0.027*((soil_df['clay_prc'][i])/100))*((soil_df['om'][i])/100))+ ((0.452*((soil_df['sand_prc'][i])/100))*((soil_df['clay_prc'][i])/100))+ 0.299
            fc_60 = pred_thFC_60 + (1.283 * (np.power(pred_thFC_60, 2))) - (0.374 * pred_thFC_60) - 0.015
            #fc = pred_thFC + (1.283 * (pred_thFC*pred_thFC)) - (0.374 * pred_thFC) - 0.015
            ts_60 =soil_df["thetaS_m3m3"][i]
            ks_60=(soil_df['Ksat_cmHr'][i])*240
        if row['depth_cm'] == "60-100":
            pred_thWP_100 = ((-0.024*((soil_df['sand_prc'][i])/100))) + ((0.487*((soil_df['clay_prc'][i])/100))) + ((0.006*((soil_df['om'][i])/100))) + ((0.005*((soil_df['sand_prc'][i])/100))*((soil_df['om'][i])/100))- ((0.013*((soil_df['clay_prc'][i])/100))*((soil_df['om'][i])/100))+ ((0.068*((soil_df['sand_prc'][i])/100))*((soil_df['clay_prc'][i])/100))+ 0.031
            wp_100 = pred_thWP_100 + (0.14 * pred_thWP_100) - 0.02
            pred_thFC_100 = ((-0.251*((soil_df['sand_prc'][i])/100))) + ((0.195*((soil_df['clay_prc'][i])/100)))+ ((0.011*((soil_df['om'][i])/100))) + ((0.006*((soil_df['sand_prc'][i])/100))*((soil_df['om'][i])/100))- ((0.027*((soil_df['clay_prc'][i])/100))*((soil_df['om'][i])/100))+ ((0.452*((soil_df['sand_prc'][i])/100))*((soil_df['clay_prc'][i])/100))+ 0.299
            fc_100 = pred_thFC_100 + (1.283 * (np.power(pred_thFC_100, 2))) - (0.374 * pred_thFC_100) - 0.015
            #fc = pred_thFC + (1.283 * (pred_thFC*pred_thFC)) - (0.374 * pred_thFC) - 0.015
            ts_100 =soil_df["thetaS_m3m3"][i]
            ks_100=(soil_df['Ksat_cmHr'][i])*240
        if row['depth_cm'] == "100-200":
            pred_thWP_200 = ((-0.024*((soil_df['sand_prc'][i])/100))) + ((0.487*((soil_df['clay_prc'][i])/100))) + ((0.006*((soil_df['om'][i])/100))) + ((0.005*((soil_df['sand_prc'][i])/100))*((soil_df['om'][i])/100))- ((0.013*((soil_df['clay_prc'][i])/100))*((soil_df['om'][i])/100))+ ((0.068*((soil_df['sand_prc'][i])/100))*((soil_df['clay_prc'][i])/100))+ 0.031
            wp_200 = pred_thWP_200 + (0.14 * pred_thWP_200) - 0.02
            pred_thFC_200 = ((-0.251*((soil_df['sand_prc'][i])/100))) + ((0.195*((soil_df['clay_prc'][i])/100)))+ ((0.011*((soil_df['om'][i])/100))) + ((0.006*((soil_df['sand_prc'][i])/100))*((soil_df['om'][i])/100))- ((0.027*((soil_df['clay_prc'][i])/100))*((soil_df['om'][i])/100))+ ((0.452*((soil_df['sand_prc'][i])/100))*((soil_df['clay_prc'][i])/100))+ 0.299
            fc_200 = pred_thFC_200 + (1.283 * (np.power(pred_thFC_200, 2))) - (0.374 * pred_thFC_200) - 0.015
            #fc = pred_thFC + (1.283 * (pred_thFC*pred_thFC)) - (0.374 * pred_thFC) - 0.015
            ts_200 =soil_df["thetaS_m3m3"][i]
            ks_200=(soil_df['Ksat_cmHr'][i])*240
        

            # create soil compartments
            custom = Soil('custom',cn=46,rew=7, dz=[0.025]*2+[0.05]*2+[0.075]*2+[0.15]*2+[0.2]*2+[0.5]*2)

            custom.add_layer(thickness=0.05,thS=ts_5, # assuming soil properties are the same in the upper 0.1m
                 Ksat=ks_5,thWP =wp_5 , 
                 thFC = fc_5, penetrability = 100.0)
            custom.add_layer(thickness=0.15,thS=ts_15, # assuming soil properties are the same in the upper 0.1m
                         Ksat=ks_15,thWP =wp_15 , 
                         thFC = fc_15, penetrability = 100.0)
            custom.add_layer(thickness=0.3,thS=ts_30, # assuming soil properties are the same in the upper 0.1m
                         Ksat=ks_30,thWP =wp_30 , 
                         thFC = fc_30, penetrability = 100.0)
            custom.add_layer(thickness=0.3,thS=ts_60, # assuming soil properties are the same in the upper 0.1m
                         Ksat=ks_60,thWP =wp_60 , 
                         thFC = fc_60, penetrability = 100.0)
            custom.add_layer(thickness=0.4,thS=ts_100, # assuming soil properties are the same in the upper 0.1m
                         Ksat=ks_100,thWP =wp_100 , 
                         thFC = fc_100, penetrability = 100.0)
            custom.add_layer(thickness=1,thS=ts_200, # assuming soil properties are the same in the upper 0.1m
                         Ksat=ks_200,thWP =wp_200 , 
                         thFC = fc_200, penetrability = 100.0)
            custom_soil.append(custom)


# sheridan soils
sher_soils = custom_soil[10]
custom = sher_soils

# morris sensitive parameters
# function used to create a list of dictionaries of the sensitive parameters for 
# yield and irrigation


def Parameters(morris_results): 
    yield_params_list = [] 
    irrig_params_list = []
    if list(map(len, morris_results)) == [1, 1, 1]: # for rainfed yield with tuple of length 1
       for item in morris_results:
        
            # yield
            yield_influ = list(item[0]['names'])

            yield_params = {
                'bounds': [],
                'dists': corn_params['dists'],
                'groups': [],
                'names': [],
                'num_vars': 0
            }

            yield_names_list = corn_params['names']
            yield_count = 0

            for i in range(len(yield_names_list)):
                if yield_names_list[i] in yield_influ:
                    yield_count +=1
                    yield_params['bounds'].append(corn_params['bounds'][i])
                    yield_params['names'].append(yield_names_list[i])
                    yield_params['groups'].append(yield_names_list[i])
                    yield_params['num_vars'] = yield_count
            yield_params_list.append(yield_params) 
            
       return yield_params_list           

    else:
       for item in morris_results:
            yield_influ = list(item[0]['names'])

            yield_params = {
                'bounds': [],
                'dists': corn_params['dists'],
                'groups': [],
                'names': [],
                'num_vars': 0
            }

            yield_names_list = corn_params['names']
            yield_count = 0

            for i in range(len(yield_names_list)):
                if yield_names_list[i] in yield_influ:
                    yield_count +=1
                    yield_params['bounds'].append(corn_params['bounds'][i])
                    yield_params['names'].append(yield_names_list[i])
                    yield_params['groups'].append(yield_names_list[i])
                    yield_params['num_vars'] = yield_count
            yield_params_list.append(yield_params)  


            irrig_influ = list(item[1]['names'])

            irrig_params = {
                'bounds': [],
                'dists': corn_params['dists'],
                'groups': [],
                'names': [],
                'num_vars': 0
            }

            irrig_names_list = corn_params['names']
            irrig_count = 0

            for i in range(len(irrig_names_list)):
                if irrig_names_list[i] in irrig_influ:
                    irrig_count +=1
                    irrig_params['bounds'].append(corn_params['bounds'][i])
                    irrig_params['names'].append(irrig_names_list[i])
                    irrig_params['groups'].append(irrig_names_list[i])
                    irrig_params['num_vars'] = irrig_count
            irrig_params_list.append(irrig_params)  

       return yield_params_list, irrig_params_list


# create list of dataframes with the influential parameters for each treatment (rainfed and irrigated)
# the lists influ_morris_rainfed and influ_morris_irrig each contain 
# 3 tuples: each tuple has data for a specified year/treatment (dry, normal, wet) and these years are in the following order
# [2002, 2019, 2021] which is dry, wet and normal
# Each tuple has 3 dataframes
# first dataframe is the aquacrop simulation results from morris
# second dataframe has influential parameters for yield
# third dataframe has influential parameters for irrigation


# irrigated
yield_list_irrig = list(map(Parameters, [influ_morris_irrig]))[0][0] # influential parameters for irrigated yield for 2002, 2019 and 2021
irrig_list_irrig = list(map(Parameters, [influ_morris_irrig]))[0][1] # influential parameters for irrigation for 2002, 2019 and 2021

# rainfed
yield_list_rainfed = list(map(Parameters, [influ_morris_rainfed]))[0]  # influential parameters for rainfed yield for 2002, 2019 and 2021


# sobol function for irrigated corn
def SobolCornIrrigated(df, problem_dict, year):
    # weather data
    x = df  # make it generic
    x = x[x['year']== year]  # filter for yr

    wdf = x.drop(['year'], axis=1) # drop year variable

    # aquacrop set up constant conditions
    sim_start = f'{year}/01/01'#'2021/01
    sim_end = f'{year}/12/31'
    initWC = InitialWaterContent(value=['FC'])
        
    # total runs = 2N(p+1)
    param_values_sobol = saltelli.sample(problem_dict, 1024, calc_second_order=False, skip_values=2048)
    param_values_sobol = pd.DataFrame(param_values_sobol)
    param_values_sobol.columns = problem_dict['names']
    
    # figure out how to rename cols
    
    new_names = {
        'tb': 'Tbase', 
        'tu': 'Tupp',
        'ccs': 'SeedSize',
        'den': 'PlantPop',
        'eme': 'Emergence',
        'cgc':'CGC',
        'ccx': 'CCx',
        'sen': 'Senescence',
        'cdc': 'CDC',
        'mat': 'Maturity',
        'rtm': 'Zmin',
        'flolen': 'Flowering',
        'rtx': 'Zmax',
        'rtshp': 'fshape_r',
        'root': 'MaxRooting',
        'rtexup': 'SxTopQ',
        'rtexlw': 'SxBotQ',
         #Crop Transpiration
        'kc': 'Kcb',
        'kcdcl': 'fage',
         #Biomass and Yield
        'wp': 'WP',
        'wpy': 'WPy',
        'hi': 'HI0',
        'hipsflo': 'dHI_pre',
        'exc': 'exc',
        'hipsveg': 'a_HI',
        'hingsto': 'b_HI',
        'hinc': 'dHI0',
        'hilen': 'YldForm',
         #Water and Temperature Stress
        'polmn': 'Tmin_up',
        'polmx': 'Tmax_up',
        'pexup': 'p_up',
        'pexlw': 'p_lo',
        'pexshp': 'fshape_w',
        'smt': 'SMT'
        }

    param_values_sobol = param_values_sobol.rename(columns=new_names)
    
    
    sobol_list_yield = []
    sobol_list_irrig = []
    model_list = []

    # Loop through the rows of the dataframe and extract each row into a new dataframe
    for i in range(0,len(param_values_sobol)):
        # Create an empty list to store the ith row
        ith_row = []
        
        # Loop through the columns of the dataframe and extract the ith value
        for col_name in param_values_sobol.columns:
            ith_value = param_values_sobol[col_name][i]
            ith_row.append(ith_value)
        
        # Create a new dataframe with data from the ith row
        new_df = pd.DataFrame([ith_row], columns=param_values_sobol.columns)
        new_df_melt = new_df.melt(ignore_index=True).reset_index()
        new_df_melt = new_df_melt[new_df_melt.variable != 'SMT']
        
        crop = Crop("Maize", planting_date='05/01')
        
        if 'SMT' in new_df.columns:
        
            irr_mngt = IrrigationManagement(irrigation_method=1,
                                       SMT=[new_df['SMT'][0]]*4)

            for index, row in new_df_melt.iterrows():
            
                
                
                if hasattr(crop, row['variable']):
                   setattr(crop, row['variable'], row['value'])
                
                #irr_mngt = IrrigationManagement(irrigation_method=1,
                                               #SMT=[new_df['SMT'][0]]*4)
                model = AquaCropModel(sim_start,sim_end,wdf,custom,crop,initWC, irr_mngt)
                    #model_irrig.append(model)
                model.run_model(till_termination=True) # run model till the end
                model_df = model._outputs.final_stats
                    #print(model_df)
                   # model_df = model_df.reset_index()
                    #model_irrig.append(model_df)
                
                
                # Append the new dataframe to the list of new dataframes
                
        else:
            irr_mngt = IrrigationManagement(irrigation_method=1,
                                       SMT=[80]*4)
            for index, row in new_df_melt.iterrows():
             
                 
                 
                 if hasattr(crop, row['variable']):
                    setattr(crop, row['variable'], row['value'])
                 
                 #irr_mngt = IrrigationManagement(irrigation_method=1,
                                                #SMT=[new_df['SMT'][0]]*4)
                 model = AquaCropModel(sim_start,sim_end,wdf,custom,crop,initWC, irr_mngt)
                     #model_irrig.append(model)
                 model.run_model(till_termination=True) # run model till the end
                 model_df = model._outputs.final_stats
                
        model_list.append(model_df)
    
    model_df_full = pd.concat(model_list)
    # yield analysis  
    yield_vals = np.array(model_df_full[['Yield (tonne/ha)']]).ravel() # select yield column and tranform to array (x,)
          

    Si_sobol_yield = sobol.analyze( # returns dictionary
            problem_dict, yield_vals, calc_second_order=False, conf_level=0.95, print_to_console=True
            )
    
    # save as df
    Si_sobol_ydf = pd.DataFrame(Si_sobol_yield)
    Si_sobol_ydf['names'] = problem_dict['names']
    
    sobol_list_yield.append(Si_sobol_ydf)
    
    
    # irrigation values
    irrig_vals = np.array(model_df_full[['Seasonal irrigation (mm)']]).ravel() # select yield column and tranform to array (x,)
          

    Si_sobol_irrig = sobol.analyze( # returns dictionary
            problem_dict, irrig_vals, calc_second_order=False, conf_level=0.95, print_to_console=True
            )
    
    # save as df
    Si_sobol_idf = pd.DataFrame(Si_sobol_irrig)
    Si_sobol_idf['names'] = problem_dict['names']
    
    sobol_list_yield.append(Si_sobol_idf)
    
       
    return sobol_list_yield, sobol_list_irrig




# function for rainfed conditions
def SobolCornRainfed(df, problem_dict, year):
    # weather data
    x = df  # make it generic
    x = x[x['year']== year]  # filter for yr

    wdf = x.drop(['year'], axis=1) # drop year variable

    # aquacrop set up constant conditions
    sim_start = f'{year}/01/01'#'2021/01
    sim_end = f'{year}/12/31'
    initWC = InitialWaterContent(value=['FC'])
        
    # total runs = 2N(p+1)
    param_values_sobol = saltelli.sample(problem_dict, 1024, calc_second_order=False, skip_values=2048)#1024, calc_second_order=False, skip_values=2048
    param_values_sobol = pd.DataFrame(param_values_sobol)
    param_values_sobol.columns = problem_dict['names']
    
    # figure out how to rename cols
    
    new_names = {
        'tb': 'Tbase', 
        'tu': 'Tupp',
        'ccs': 'SeedSize',
        'den': 'PlantPop',
        'eme': 'Emergence',
        'cgc':'CGC',
        'ccx': 'CCx',
        'sen': 'Senescence',
        'cdc': 'CDC',
        'mat': 'Maturity',
        'rtm': 'Zmin',
        'flolen': 'Flowering',
        'rtx': 'Zmax',
        'rtshp': 'fshape_r',
        'root': 'MaxRooting',
        'rtexup': 'SxTopQ',
        'rtexlw': 'SxBotQ',
         #Crop Transpiration
        'kc': 'Kcb',
        'kcdcl': 'fage',
         #Biomass and Yield
        'wp': 'WP',
        'wpy': 'WPy',
        'hi': 'HI0',
        'hipsflo': 'dHI_pre',
        'exc': 'exc',
        'hipsveg': 'a_HI',
        'hingsto': 'b_HI',
        'hinc': 'dHI0',
        'hilen': 'YldForm',
         #Water and Temperature Stress
        'polmn': 'Tmin_up',
        'polmx': 'Tmax_up',
        'pexup': 'p_up',
        'pexlw': 'p_lo',
        'pexshp': 'fshape_w',
        'smt': 'SMT'
        }

    param_values_sobol = param_values_sobol.rename(columns=new_names)
    
    
    sobol_list_yield = []
    sobol_list_irrig = []
    model_list = []

    # Loop through the rows of the dataframe and extract each row into a new dataframe
    for i in range(0,len(param_values_sobol)):
        # Create an empty list to store the ith row
        ith_row = []
        
        # Loop through the columns of the dataframe and extract the ith value
        for col_name in param_values_sobol.columns:
            ith_value = param_values_sobol[col_name][i]
            ith_row.append(ith_value)
        
        # Create a new dataframe with data from the ith row
        new_df = pd.DataFrame([ith_row], columns=param_values_sobol.columns)
        new_df_melt = new_df.melt(ignore_index=True).reset_index()
        
        crop = Crop("Maize", planting_date='05/01')
        irr_mngt = IrrigationManagement(irrigation_method=0)

        for index, row in new_df_melt.iterrows():
            if hasattr(crop, row['variable']):
               setattr(crop, row['variable'], row['value'])
            
            
            model = AquaCropModel(sim_start,sim_end,wdf,custom,crop,initWC, irr_mngt)
                #model_irrig.append(model)
            model.run_model(till_termination=True) # run model till the end
            model_df = model._outputs.final_stats
                #print(model_df)
               # model_df = model_df.reset_index()
                #model_irrig.append(model_df)
                
                
                # Append the new dataframe to the list of new dataframes
        model_list.append(model_df)
        
    model_df_full = pd.concat(model_list)
                
    # yield analysis  
    yield_vals = np.array(model_df_full[['Yield (tonne/ha)']]).ravel() # select yield column and tranform to array (x,)
          

    Si_sobol_yield = sobol.analyze( # returns dictionary
            problem_dict, yield_vals, calc_second_order=False, conf_level=0.95, print_to_console=True
            )
    
    # save as dataframe
    Si_sobol_ydf = pd.DataFrame(Si_sobol_yield)
    Si_sobol_ydf['names'] = problem_dict['names']
    
    sobol_list_yield.append(Si_sobol_ydf)
    
    return(sobol_list_yield)



# function inputs 

# treatments and years
sim_years = [2002, 2019, 2021]
weather = [sher_gridMET]


# test 
#dsa2 = [item[0] for item in list(map(SobolCornRainfed, weather*2, yield_list_rainfed[1:], sim_years[1:]))] # take the second dictionary from each tuple in list

# run sobol (N = 1024) and return dfs 
# list(map()) creates a nested list - list 1 has the sobol_yield and sobol irrig, 2nd list is empty (could find an alternative to list(map))
# for the yield params, use the 1st dataframe in the first list since the function returns both the yield and irrig sobol dataframes
# for the irrig params use the 2nd dataframe in the first list
yield_irrig_sobol_n1024_df = [item[0][0] for item in list(map(SobolCornIrrigated, weather*3, yield_list_irrig, sim_years))] # take the first dataframe from t
irrig_sobol_n1024_df = [item[0][1] for item in list(map(SobolCornIrrigated, weather*3, irrig_list_irrig, sim_years))] # take the second dictionary from each tuple in list


# returns a nested list of dataframes - dataframe for each year saved in a list. For loop used to remove each dataframe from list
yield_rainfed_sobol_n1024_df = [item[0] for item in list(map(SobolCornRainfed, weather*2, yield_list_rainfed[1:], sim_years[1:]))] # yield dictionary for 2002/dry is empty so, use 2019 and 2021 only for function to work 


# save results for calibration

# irrigation
irrig_yield_cal = pd.concat(yield_irrig_sobol_n1024_df)
irrig_yield_cal = irrig_yield_cal[irrig_yield_cal['ST'] > irrig_yield_cal.ST.max()*0.1]

irrigation_cal = pd.concat(irrig_sobol_n1024_df)
irrigation_cal = irrigation_cal[irrigation_cal['ST'] > irrigation_cal.ST.max()*0.1]

irrig_cal = pd.concat([irrig_yield_cal, irrigation_cal], ignore_index=True)
irrig_cal = irrig_cal.names.unique()


# rainfed
rain_cal = pd.concat(yield_rainfed_sobol_n1024_df)
rain_cal = rain_cal[rain_cal['ST'] > rain_cal.ST.max()*0.1]
rain_cal = pd.DataFrame(rain_cal.names.unique())


irrig_cal.to_csv(r'./data/irrigated_corn_calibration_params.txt', header=None, index=None, sep=' ', mode='a')

rain_cal.to_csv(r'./data/rainfed_corn_calibration_params.txt', header=None, index=None, sep=' ', mode='a')



################# FOR SAVING SA RESULTS ##############################
with open(wd+'/data/analysis_results/sensitivity_analysis_runs/ks_rainfed_cornyield_soboldf_v2_N1024.pickle', 'rb') as crsdf: 
    yield_rainfed_sobol_n1024_df = pickle.load(crsdf)


with open(wd+'/data/analysis_results/sensitivity_analysis_runs/ks_irrigated_cornyield_soboldf_v2_N1024.pickle', 'rb') as xy: 
    yield_irrig_sobol_n1024_df = pickle.load(xy)


with open(wd+'/data/analysis_results/sensitivity_analysis_runs/ks_irrigation_corn_soboldf_v2_N1024.pickle', 'rb') as yz: 
    irrig_sobol_n1024_df = pickle.load(yz)

#####################################################################


################# IGNORE IGNORE IGNORE ##############################
sad = irrig_sobol_n1024_df[0]

conditions = [
    sad['names'].isin(['tb',
                       'tu',
                       'ccs',
                        'den',
                        'eme',
                        'cgc',
                        'ccx',
                        'sen',
                        'cdc',
                        'mat',
                        'rtm',
                        'flolen',
                        'rtx',
                        'rtshp',
                        'root',
                        'rtexup',
                        'rtexlw',
                         'kc',
                         'kcdcl']),
    sad['names'].isin(['wp',
                       'wpy',
                       'hi',
                       'hipsflo',
                       'exc',
                       'hipsveg',
                       'hingsto',
                        'hinc',
                        'hilen']),
    sad['names'].isin(['smt'])
]


choices = ['crop dvpt', 'biomass', 'mngt']
sad['C'] = np.select(conditions, choices, default=np.nan)

sobol_df = sad
sobol_df = sobol_df.sort_values('ST', ascending = False)

colors_top = {'crop dvpt': '#185918', 'biomass': '#8D5524', 'mngt': '#002375'} #peru
colors_bottom = {'crop dvpt': '#377B2B', 'biomass': '#C68642', 'mngt': '#113a9b'} #peachpuff   #blue
# #FDBB2F 113a9b
# #F47A1F
  #185918 #7AC142
fig, ax = plt.subplots(figsize=(10, 7))
ax.bar(sobol_df['names'], sobol_df['ST'], width=0.7 , yerr = sobol_df['ST_conf'], color = [colors_top[f] for f in sobol_df['C']], edgecolor = 'black', 
            error_kw=dict(lw=1.5, capsize=3, capthick=1))
ax.bar(sobol_df['names'], sobol_df['S1'], width=0.7, color = [colors_bottom[f] for f in sobol_df['C']])
plt.xticks(fontsize=30, rotation = 45, ha='center', weight = 'bold')
plt.yticks(fontsize=30)
plt.ylim(0, 1) #rainfed corn
    #plt.legend(labels=['Total Effect - First Order SI', 'First Order SI'], fontsize = 20)
plt.ylabel('Sobol Sensitivity Index',  fontsize=30, weight = 'bold')


fruits = ['apple', 'banana', 'orange', 'grape', 'watermelon']
y = np.array([12, 18, 15, 22, 10])
colors = {'apple': 'red', 'banana': 'yellow', 'orange': 'orange', 'grape': 'purple', 'watermelon': 'green'}

plt.bar(fruits, y, color=[colors[f] for f in fruits])
plt.show()

###################################################################



# visuals function - check the y max for each graph combination (rainfed and irrigated) to make them easier to compare
def sobol_plots(df):
    
    conditions = [
        df['names'].isin(['tb',
                           'tu',
                           'ccs',
                            'den',
                            'eme',
                            'cgc',
                            'ccx',
                            'sen',
                            'cdc',
                            'mat',
                            'rtm',
                            'flolen',
                            'rtx',
                            'rtshp',
                            'root',
                            'rtexup',
                            'rtexlw',
                             'kc',
                             'kcdcl']),
        df['names'].isin(['wp',
                           'wpy',
                           'hi',
                           'hipsflo',
                           'exc',
                           'hipsveg',
                           'hingsto',
                            'hinc',
                            'hilen']),
        df['names'].isin(['smt'])
    ]


    choices = ['crop dvpt', 'biomass', 'mngt']
    df['group'] = np.select(conditions, choices, default=np.nan)

    
    sobol_df = df
    sobol_df = sobol_df.sort_values('ST', ascending = False)
    
    colors_top = {'crop dvpt': '#185918', 'biomass': '#8D5524', 'mngt': '#002375'} #peru
    colors_bottom = {'crop dvpt': '#377B2B', 'biomass': '#C68642', 'mngt': '#113a9b'} #peachpuff   #blue
    # #FDBB2F
    # #F47A1F
      
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.bar(sobol_df['names'], sobol_df['ST'], width=0.7 , yerr = sobol_df['ST_conf'], color = 'white', edgecolor = 'black', hatch='x',
                error_kw=dict(lw=1.5, capsize=3, capthick=1))
    ax.bar(sobol_df['names'], sobol_df['S1'], width=0.7, color = [colors_bottom[f] for f in sobol_df['group']], edgecolor = 'black',)
    plt.xticks(fontsize=35, rotation = 45, ha='center')
    plt.yticks(fontsize=30)
    plt.ylim(0, 1) #rainfed corn
        #plt.legend(labels=['Total Effect - First Order SI', 'First Order SI'], fontsize = 20)
    plt.ylabel('Sobol Sensitivity Index',  fontsize=32, weight = 'bold')
    return fig


# get legend
sobol_plots(yield_irrig_sobol_n1024_df[0])
plt.savefig('results/visuals/sobol_corn_yield_kansas_legend.png', format='png', dpi=600)

# generate visuals
# yield
yield_irr2002, yield_irr2019, yield_irr2021 = list(map(sobol_plots, yield_irrig_sobol_n1024_df)) # irrigated yield
yield_rain2019, yield_rain2021 = list(map(sobol_plots, yield_rainfed_sobol_n1024_df)) # rainfed yield

# irrigation
irrigation_2002, irrigation_2019, irrigation_2021 = list(map(sobol_plots, irrig_sobol_n1024_df))


# make big plot
# yield
fig7, ax7 = plt.subplots(nrows=3, ncols=2, figsize=(15,15))
ax7[0,0].imshow(yield_irr2002.canvas.renderer.buffer_rgba())
ax7[1,0].imshow(yield_irr2021.canvas.renderer.buffer_rgba())
ax7[2,0].imshow(yield_irr2019.canvas.renderer.buffer_rgba())
#ax7[1,0].imshow(yield_rain2002.canvas.renderer.buffer_rgba())
ax7[1,1].imshow(yield_rain2021.canvas.renderer.buffer_rgba())
ax7[2,1].imshow(yield_rain2019.canvas.renderer.buffer_rgba())
#ax5[0,0].set_title('Dry-Irrigated', fontweight ="bold", size = 17, pad = 8)
trans = mtransforms.ScaledTranslation(10/72, -5/72, fig7.dpi_scale_trans)
ax7[0,0].text(0.56, 0.9, s = 'Dry-Irrigated', transform=ax7[0,0].transAxes + trans,#size = 20,
            fontsize=16, verticalalignment='top', weight = 'bold',
            bbox=dict(facecolor='white', edgecolor='white', pad=3.0))
ax7[1,0].text(0.47, 0.9, s = 'Normal-Irrigated', transform=ax7[1,0].transAxes + trans,#size = 20,
            fontsize=16, verticalalignment='top', weight = 'bold',
            bbox=dict(facecolor='white', edgecolor='white', pad=3.0))
ax7[2,0].text(0.56, 0.9, s = 'Wet-Irrigated', transform=ax7[2,0].transAxes + trans,#size = 20,
            fontsize=16, verticalalignment='top', weight = 'bold',
            bbox=dict(facecolor='white', edgecolor='white', pad=3.0))
#ax7[1,0].text(0.63, 0.9, s = '', transform=ax7[1,0].transAxes + trans,#size = 20,
            #fontsize=15, verticalalignment='top', 
            #bbox=dict(facecolor='white', edgecolor='white', pad=3.0))
ax7[1,1].text(0.50, 0.9, s = 'Normal-Rainfed', transform=ax7[1,1].transAxes + trans,#size = 20,
            fontsize=16, verticalalignment='top', weight = 'bold',
            bbox=dict(facecolor='white', edgecolor='white', pad=3.0))
ax7[2,1].text(0.58, 0.9, s = 'Wet-Rainfed', transform=ax7[2,1].transAxes + trans,#size = 20,
            fontsize=16, verticalalignment='top', weight = 'bold',
            bbox=dict(facecolor='white', edgecolor='white', pad=3.0))
ax7[0,0].axis('off')
ax7[1,0].axis('off')
ax7[2,0].axis('off')
ax7[0,1].axis('off')
ax7[1,1].axis('off')
ax7[2,1].axis('off')
fig7.subplots_adjust(hspace=0.009, wspace=-0.00005)
plt.savefig('results/visuals/sobol_corn_yield_kansas.png', format='png',dpi = 1200)

############ for class
fig7, ax7 = plt.subplots(nrows=3, ncols=2, figsize=(15,15))
ax7[0,0].imshow(yield_irr2002.canvas.renderer.buffer_rgba())
ax7[1,0].imshow(yield_irr2021.canvas.renderer.buffer_rgba())
ax7[2,0].imshow(yield_irr2019.canvas.renderer.buffer_rgba())
#ax7[1,0].imshow(rain2002.canvas.renderer.buffer_rgba())
ax7[1,1].imshow(yield_rain2021.canvas.renderer.buffer_rgba())
ax7[2,1].imshow(yield_rain2019.canvas.renderer.buffer_rgba())
#ax5[0,0].set_title('Dry-Irrigated', fontweight ="bold", size = 17, pad = 8)
trans = mtransforms.ScaledTranslation(10/72, -5/72, fig7.dpi_scale_trans)
ax7[0,0].text(0.56, 0.9, s = 'Dry-Irrigated', transform=ax7[0,0].transAxes + trans,#size = 20,
            fontsize=13, verticalalignment='top', weight = 'bold',
            bbox=dict(facecolor='white', edgecolor='white', pad=3.0))
ax7[1,0].text(0.47, 0.9, s = 'Normal-Irrigated', transform=ax7[1,0].transAxes + trans,#size = 20,
            fontsize=13, verticalalignment='top', weight = 'bold',
            bbox=dict(facecolor='white', edgecolor='white', pad=3.0))
ax7[2,0].text(0.56, 0.9, s = 'Wet-Irrigated', transform=ax7[2,0].transAxes + trans,#size = 20,
            fontsize=13, verticalalignment='top', weight = 'bold',
            bbox=dict(facecolor='white', edgecolor='white', pad=3.0))
#ax7[1,0].text(0.63, 0.9, s = 'Dry-Rainfed', transform=ax7[1,0].transAxes + trans,#size = 20,
            #fontsize=15, verticalalignment='top', 
            #bbox=dict(facecolor='white', edgecolor='white', pad=3.0))
ax7[1,1].text(0.50, 0.9, s = 'Normal-Rainfed', transform=ax7[1,1].transAxes + trans,#size = 20,
            fontsize=16, verticalalignment='top', weight = 'bold',
            bbox=dict(facecolor='white', edgecolor='white', pad=3.0))
ax7[2,1].text(0.58, 0.9, s = 'Wet-Rainfed', transform=ax7[2,1].transAxes + trans,#size = 20,
            fontsize=16, verticalalignment='top', weight = 'bold',
            bbox=dict(facecolor='white', edgecolor='white', pad=3.0))
ax7[0,0].axis('off')
ax7[1,0].axis('off')
ax7[2,0].axis('off')
ax7[0,1].axis('off')
ax7[1,1].axis('off')
ax7[2,1].axis('off')
fig7.subplots_adjust(hspace=0.009, wspace=-0.00005)
plt.savefig('results/visuals/sobol_corn_yield_kansas.png', format='png',dpi = 1200)







# irrigation
fig8, ax8 = plt.subplots(nrows=3, ncols=1, figsize=(4,9))
ax8[0].imshow(irrigation_2002.canvas.renderer.buffer_rgba())
ax8[1].imshow(irrigation_2021.canvas.renderer.buffer_rgba())
ax8[2].imshow(irrigation_2019.canvas.renderer.buffer_rgba())
trans = mtransforms.ScaledTranslation(10/72, -5/72, fig8.dpi_scale_trans)
ax8[0].text(0.8, 0.9, s = 'Dry', transform=ax8[0].transAxes + trans,#size = 20,
            fontsize=11, verticalalignment='top', weight = 'bold',
            bbox=dict(facecolor='white', edgecolor='white', pad=3.0))
ax8[1].text(0.69, 0.9, s = 'Normal', transform=ax8[1].transAxes + trans,#size = 20,
            fontsize=11, verticalalignment='top', weight = 'bold',
            bbox=dict(facecolor='white', edgecolor='white', pad=3.0))
ax8[2].text(0.8, 0.9, s = 'Wet', transform=ax8[2].transAxes + trans,#size = 20,
            fontsize=11, verticalalignment='top', weight = 'bold',
            bbox=dict(facecolor='white', edgecolor='white', pad=3.0))
ax8[0].axis('off')
ax8[1].axis('off')
ax8[2].axis('off')
#ax8[2].legend(labels=['Total Effect-Frst Order SI', 'First Order SI'])
fig8.subplots_adjust(hspace=0.009)
plt.savefig('results/visuals/sobol_corn_irrigation_kansas.png',format='png', dpi=1200)


# v2 after lowering the morris thresholds for rainfed conditions
with open(r'./data/analysis_results/sensitivity_analysis_runs/ks_rainfed_cornyield_soboldf_v2_N1024.pickle', 'wb') as crsdf: 
    pickle.dump(yield_rainfed_sobol_n1024_df, crsdf) 

with open(r'./data/analysis_results/sensitivity_analysis_runs/ks_irrigated_cornyield_soboldf_v2_N1024.pickle', 'wb') as ciysdf: 
    pickle.dump(yield_irrig_sobol_n1024_df, ciysdf) 


with open(r'./data/analysis_results/sensitivity_analysis_runs/ks_irrigation_corn_soboldf_v2_N1024.pickle', 'wb') as cisdf: 
    pickle.dump(irrig_sobol_n1024_df, cisdf) 




















####***************************************** second run

# run sobol (N = 1024)
yield_irrig_sobol_n1024 = list(map(SobolCornIrrigated, weather*3, yield_list_irrig, sim_years)) # take the first dictionary from each tuple in list
irrig_sobol_n1024 = list(map(SobolCornIrrigated, weather*3, irrig_list_irrig, sim_years)) # take the second dictionary from each tuple in list


yield_rainfed_sobol_n1024 = list(map(SobolCornRainfed, weather*2, yield_list_rainfed[1:], sim_years[1:])) # yield dictionary for 2002/dry is empty so, use 2019 and 2021 only for function to work 

# save this



###########************************************************ first run

# run sobol (N = 128)
yield_irrig_sobol = list(map(SobolCornIrrigated, weather*3, yield_list_irrig, sim_years)) # take the first dictionary from each tuple in list
irrig_sobol = list(map(SobolCornIrrigated, weather*3, irrig_list_irrig, sim_years)) # take the second dictionary from each tuple in list


yield_rainfed_sobol = list(map(SobolCornRainfed, weather*2, yield_list_rainfed[1:], sim_years[1:])) # yield dictionary for 2002/dry is empty so, use 2019 and 2021 only for function to work 


# create new nest with the correct results for for irrigated simulations 
yield_irrig_sobol_fn = [item[0] for item in yield_irrig_sobol]
irrig_sobol_fn = [item[1] for item in irrig_sobol]


# save results to pickle
with open(r'./data/analysis_results/sensitivity_analysis_runs/ks_rainfed_cornyield_sobol.pickle', 'wb') as crs: 
    pickle.dump(yield_rainfed_sobol, crs) 

with open(r'./data/analysis_results/sensitivity_analysis_runs/ks_irrigated_cornyield_sobol.pickle', 'wb') as ciys: 
    pickle.dump(yield_irrig_sobol_fn, ciys) 


with open(r'./data/analysis_results/sensitivity_analysis_runs/ks_irrigation_corn_sobol.pickle', 'wb') as cis: 
    pickle.dump(irrig_sobol_fn, cis) 





##################3

problem = {
 'num_vars': 8,
  'names': ['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8'],
  'groups': None,
  'bounds': [[0.0, 1.0],
             [0.0, 1.0],
           [0.0, 1.0],
            [0.0, 1.0],
             [0.0, 1.0],
             [0.0, 1.0],
             [0.0, 1.0],
             [0.0, 1.0]]}


param_values = saltelli.sample(problem, 128, calc_second_order=False, skip_values=256) # A recommendation adopted here is that both skip_values and N be a power of 2, where N is 
#the desired number of samples (see [2] and discussion in [5] for further context). It is also suggested therein that skip_values >= N.

Y = Ishigami.evaluate(param_values)

# Perform the sensitivity analysis using the model output
# Specify which column of the output file to analyze (zero-indexed)
Si = sobol.analyze(
    problem, Y, calc_second_order=False, conf_level=0.95, print_to_console=True
)

sidf = pd.DataFrame(Si)
sidf['parz'] = problem['names']




fg3 = sidf.explode(['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8'], ignore_index=True)



