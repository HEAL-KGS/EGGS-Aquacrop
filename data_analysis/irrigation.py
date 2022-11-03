!pip install aquacrop==2.2
from os import chdir, getcwd
from aquacrop.classes import    *
from aquacrop.core import       *
import pandas as pd
import sys
import seaborn as sns
import os
import glob
_=[sys.path.append(i) for i in ['.', '..']]
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



## Aquacrop Model

labels=[]
outputs=[]
for smt in range(0,110,20):
    crop.Name = str(smt) # add helpfull label
    labels.append(str(smt))
    irr_mngt = IrrigationManagement(irrigation_method=1,SMT=[smt]*4) # specify irrigation management [40,60,70,30]*4
    model = AquaCropModel(sim_start,sim_end,wdf,custom,crop,initWC,irr_mngt) # create model
    model.run_model(till_termination=True) # run model till the end
    outputs.append(model._outputs.final_stats) # save results
all_outputs = pd.concat(outputs)


## get irrigation values from Aquacrop
irrig_aqc = all_outputs.assign(Year =  all_outputs['Harvest Date (YYYY/MM/DD)'].dt.year)
irrig_aqc = irrig_aqc.pivot(index= 'Year', # show irrigation vals for each year horizontally
                             columns='crop Type', 
                             values='Seasonal irrigation (mm)')
irrig_aqc.reset_index(inplace=True)       # make year a column 
                                                                 

irrig_aqc = irrig_aqc[irrig_aqc['Year'] >= 2006] # filter for yrs>2006 to match WIMAS


## Water Rights WIMAS
wr_groups = pd.read_csv(wd + "/data/water/WRgroups_FieldByYear.csv")
water_use = pd.read_csv(wd + "/data/water/WRgroups_UseByWRG.csv")

# merge water right groups and water use
irrig_wimas = pd.merge(wr_groups, water_use, on=["WR_GROUP", "Year"]) # 
irrig_wimas = irrig_wimas[irrig_wimas['UID'] == 	1381151] # filter for field
irrig_wimas = irrig_wimas[irrig_wimas['Year'] <= 	2015]
irrig_wimas = irrig_wimas.assign(irrig_wimas = (irrig_wimas['Irrigation_m3']/(irrig_wimas['TRGT_ACRES']*4046.86))*1000)

# WIMAS and Aquacrop irrigation df
irrig_df = pd.merge(irrig_wimas, irrig_aqc, on=["Year", "Year"])
irrig_df  = irrig_df[['UID', 'Year', 'Irrigation_m3', 'irrig_wimas', '0', '20', '40', '60', '80', '100']]
#yield_df.to_csv(r'./data/analysis_results/yield_df_1381151.csv', sep=',', encoding='utf-8', header='true')

# Yield Data
# yield data from usda nass https://quickstats.nass.usda.gov/#D93A3218-8B77-31A6-B57C-5A5D97A157D8
yield_Irrig = pd.read_csv(wd + "/data/agricLand/yield/sheridanYield_Irrig.csv") #CORN, GRAIN, YIELD, MEASURED IN BU / ACRE
#yield_noIrrig = pd.read_csv(wd.replace('code',"data/agricLand/gridMET/sheridanYield_noIrrig.csv")) #CORN, GRAIN, IRRIGATED - YIELD, MEASURED IN BU / ACRE

# Select year and irrigation value
yield_Irrig = yield_Irrig[['Year', 'Value']]

# df with USDS NASS yield and Aquacrop yield
yield_df = all_outputs.assign(Year =  all_outputs['Harvest Date (YYYY/MM/DD)'].dt.year)
yield_df = yield_df.pivot(index= 'Year', # show irrigation vals for each year horizontally
                             columns='crop Type', 
                             values='Yield (tonne/ha)')
yield_df = pd.merge(yield_df, yield_Irrig, on=["Year", "Year"])
yield_df = yield_df.assign(YieldUSDA = yield_df['Value']*0.0673) # convert yield from bushels/acre to tonne/ha


#yield_df.to_csv(r'./data/analysis_results/yield_df_1381151.csv', sep=',', encoding='utf-8', header='true')
                         
