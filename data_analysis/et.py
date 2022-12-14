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
path = get_filepath(wd + '/data/hydrometeorology/gridMET/gridMET_1381151.txt') #replace folder name from folder name with file path
wdf = prepare_weather(path)
sim_start = '2016/01/01' #dates to match crop data
sim_end = '2021/12/01'
soil= Soil('SiltLoam')
crop = Crop('Maize',planting_date='05/01')
initWC = InitialWaterContent(value=['FC'])
irr_mngt = IrrigationManagement(irrigation_method=1,SMT=[80]*4)


# get date variable from the wdf
wdf_date = wdf[["Date"]]
wdf_date = wdf_date[wdf_date['Date'] > '2015/12/31']
wdf_date = wdf_date.reset_index() # reset index to start from 0
wdf_date = wdf_date[['Date']] # select date variable and drop second index column

# run aquacrop water flux model
model = AquaCropModel(sim_start,sim_end,wdf,soil,crop,initWC, irr_mngt)
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
                     'ptjpl', 'sims', 'ssebop', 'Es']]



#et_means.to_csv(r'./data/analysis_results/et_df_1381151.csv', sep=',', encoding='utf-8', header='true')
                         

                      