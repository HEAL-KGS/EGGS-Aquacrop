# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 22:17:13 2022

@author: w610n091
"""

!pip install aquacrop==2.2
!pip install numba==0.55
from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, IrrigationManagement
from aquacrop.utils import prepare_weather, get_filepath
#from aquacrop.entities import IrrigationManagement
from os import chdir, getcwd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime



## Aquacrop Model
wd=getcwd() # set working directory
chdir(wd)

soils_df_full = pd.read_csv(wd + '/data/agricLand/soils/Soil_FieldsAroundSD6KS_POLARIS_AGrinstead_20220706.csv')
soils_df = soils_df_full[soils_df_full['UID'] == 1381151] # filter for one site
soils_df = soils_df[soils_df['depth_cm'] == '0-5']


soils = pd.DataFrame(soils_df_full)
soils = soils[soils['depth_cm'] == '0-5'] # use upper 0.5cm
soils = soils.assign(om = (10**(soils['logOm_%'])),
                     Ksat_cmHr = (10**(soils['logKsat_cmHr'])))
soils = soils[['UID', 'depth_cm', 'silt_prc', 'sand_prc',
               'clay_prc', 'thetaS_m3m3', 'thetaR_m3m3',
               'Ksat_cmHr', 'lambda', 'logHB_kPa', 'n',
               'logAlpha_kPa1', 'om']]
#soils = soils.head(1)

# creating custom soil profile for all soils (run only for full model)
id_list = []
custom_soil = []
for i in range(0, len(soils)): # full model replace with soils
    ids = soils['UID'][i] #create df with UID from the soils file used - fix this
    id_list.append(ids)
    pred_thWP = ((-0.024*((soils['sand_prc'][i])/100))) + ((0.487*((soils['clay_prc'][i])/100))) + ((0.006*((soils['om'][i])/100))) + ((0.005*((soils['sand_prc'][i])/100))*((soils['om'][i])/100))- ((0.013*((soils['clay_prc'][i])/100))*((soils['om'][i])/100))+ ((0.068*((soils['sand_prc'][i])/100))*((soils['clay_prc'][i])/100))+ 0.031
    wp = pred_thWP + (0.14 * pred_thWP) - 0.02
    pred_thFC = ((-0.251*((soils['sand_prc'][i])/100))) + ((0.195*((soils['clay_prc'][i])/100)))+ ((0.011*((soils['om'][i])/100))) + ((0.006*((soils['sand_prc'][i])/100))*((soils['om'][i])/100))- ((0.027*((soils['clay_prc'][i])/100))*((soils['om'][i])/100))+ ((0.452*((soils['sand_prc'][i])/100))*((soils['clay_prc'][i])/100))+ 0.299
    fc = pred_thFC + (1.283 * (np.power(pred_thFC, 2))) - (0.374 * pred_thFC) - 0.015
    #fc = pred_thFC + (1.283 * (pred_thFC*pred_thFC)) - (0.374 * pred_thFC) - 0.015
    ts =soils["thetaS_m3m3"][i]
    ks=(soils['Ksat_cmHr'][i])*240
    #tp = soils['thetaR_m3m3'][i]
    custom = Soil('custom', dz=[0.1]*30)
    custom.add_layer(thickness=custom.zSoil,thS=ts, # assuming soil properties are the same in the upper 0.1m
                     Ksat=ks,thWP =wp , 
                     thFC = fc, penetrability = 100.0)
    custom_soil.append(custom)



# make dictionary with id as key and custom soils properties as value
soil_dict=dict(zip(id_list,custom_soil))


# test to see if the dictionaries are working
#print(list(soil_dict.keys())[2])   
#print(list(soil_dict.values())[2])

# filter for dictionary with 1381151 test site
test_site = {k: v for k, v in soil_dict.items() if k == 1381151}  # filter for given site number
test_site = list(test_site.values())


path = get_filepath(wd + '/data/hydrometeorology/gridMET/gridMET_1381151.txt') #replace folder name from folder name with file path
wdf = prepare_weather(path)
sim_start = '2000/01/01' #dates to match crop data
sim_end = '2020/12/31'
custom = test_site[0] # use custom layer for 1 site
crop = Crop('Maize', planting_date='05/01') 
initWC = InitialWaterContent(value=['FC'])
irr_mngt = IrrigationManagement(irrigation_method=1,SMT=[80]*4)



# get date variable from the wdf
wdf_date = wdf[["Date"]]
wdf_date = wdf_date[wdf_date['Date'] > '2015/12/31']
wdf_date = wdf_date.reset_index() # reset index to start from 0
wdf_date = wdf_date[['Date']] # select date variable and drop second index column

# run aquacrop water flux model
model = AquaCropModel(sim_start,sim_end,wdf,custom,crop,initWC, irr_mngt)
model.run_model(till_termination=True)
#model_results = model2.get_simulation_results().head()
model_results = model._outputs.water_flux

# add the date variable and jon by index
model_results = model_results.join(wdf_date)

# calculate monthly average ET value
model_results['yearmon'] = pd.to_datetime(model_results['Date']).dt.strftime('%Y-%m') # create yearmonth variable
model_results = model_results.assign(Et = model_results['Es'] + model_results['Tr'])
ave_et = model_results.groupby('yearmon')['Et'].sum()
#ave_et = ave_et.rename(columns={'Es':'aquacrop'}) not working



## add ET data from online models
disalexi = pd.read_csv(wd + '/data/hydrometeorology/openET/ET_monthly_disalexi_FieldsAroundSD6KS_20220708.csv')
eemetric = pd.read_csv(wd + "/data/hydrometeorology/openET/ET_monthly_eemetric_FieldsAroundSD6KS_20220708.csv")
enseble = pd.read_csv(wd + "/data/hydrometeorology/openET/ET_monthly_ensemble_FieldsAroundSD6KS_20220708.csv")
geesebal = pd.read_csv(wd + "/data/hydrometeorology/openET/ET_monthly_geesebal_FieldsAroundSD6KS_20220708.csv")
ptjpl = pd.read_csv(wd + "/data/hydrometeorology/openET/ET_monthly_ptjpl_FieldsAroundSD6KS_20220708.csv")
sims = pd.read_csv(wd + "/data/hydrometeorology/openET/ET_monthly_sims_FieldsAroundSD6KS_20220708.csv")
ssebop = pd.read_csv(wd + "/data/hydrometeorology/openET/ET_monthly_ssebop_FieldsAroundSD6KS_20220708.csv")

# filter for site 1381151
disalexi = disalexi[disalexi['UID'] == 1381151]
eemetric = eemetric[eemetric['UID'] == 1381151]
enseble = enseble[enseble['UID'] == 1381151]
geesebal = geesebal[geesebal['UID'] == 1381151]
ptjpl = ptjpl[ptjpl['UID'] == 1381151]
sims = sims[sims['UID'] == 1381151]
ssebop = ssebop[ssebop['UID'] == 1381151]

# set time as index to allow for joining dfs later
disalexi = disalexi.set_index('time')
eemetric = eemetric.set_index('time')
enseble = enseble.set_index('time')
geesebal = geesebal.set_index('time')
ptjpl = ptjpl.set_index('time')
sims = sims.set_index('time')
ssebop = ssebop.set_index('time')

# add method identifier to every column
disalexi.columns = [str(col) + '_disalexi' for col in disalexi.columns]
enseble.columns = [str(col) + '_ensemble' for col in enseble.columns]
eemetric.columns = [str(col) + '_eemetric' for col in eemetric.columns]
geesebal.columns = [str(col) + '_geesebal' for col in geesebal.columns]
ptjpl.columns = [str(col) + '_ptjpl' for col in ptjpl.columns]
ssebop.columns = [str(col) + '_ssebop' for col in ssebop.columns]
sims.columns = [str(col) + '_sims' for col in sims.columns]


fullET = pd.concat([disalexi, enseble, eemetric, geesebal, ptjpl, sims, ssebop], axis=1)
fullET.reset_index(inplace=True) # make time a column
fullET['date'] = pd.to_datetime(fullET['time'])
fullET['yearmon'] = pd.to_datetime(fullET['date']).dt.strftime('%Y-%m') # create year mon


# create df with aquacrop mean ET and other online models 
et_means = fullET[['time', 
                   'yearmon',
                   'et_mean_disalexi',
                   'et_mean_ensemble',
                   'et_mean_eemetric',
                   'et_mean_geesebal',
                   'et_mean_ptjpl',
                   'et_mean_sims',
                   'et_mean_ssebop']] # select mean ETs 

# rename colums
et_means = et_means.rename(columns={
                   'et_mean_disalexi': 'disalexi',
                   'et_mean_ensemble': 'ensemble',
                   'et_mean_eemetric': 'eemetric',
                   'et_mean_geesebal': 'geesebal',
                   'et_mean_ptjpl': 'ptjpl',
                   'et_mean_sims': 'sims',
                   'et_mean_ssebop': 'ssebop'}) 


et_means = et_means.merge(ave_et, left_on = 'yearmon', right_on = "yearmon")
et_means = et_means[['time', 'disalexi', 
                     'ensemble', 'geesebal', 
                     'ptjpl', 'sims', 'ssebop', 'Et']]



#et_means.to_csv(r'./data/analysis_results/et_df_1381151.csv', sep=',', encoding='utf-8', header='true')
                         

                      