from os import chdir, getcwd
wd=getcwd() # set working directory
chdir(wd)


# wrangle the gridMET data and filter for site 1381151
import pandas as pd
import os
import glob
from datetime import datetime


gridMET = pd.read_csv(wd + '/data/hydrometeorology/gridMET/gridMET_400m_2000_21.csv')

# recalculate t0c in celcius and create ymd variables
gridMET = gridMET.assign(Tmin = gridMET.tmmn-273.15,
                    Tmax = gridMET.tmmx-273.15,
                    date = pd.to_datetime(gridMET['date_ymd'], format='%Y%m%d'))


# separiting date
gridMET = gridMET.assign(day =  gridMET['date'].dt.day,
                         month = gridMET['date'].dt.month,
                         year = gridMET['date'].dt.year)

# filter for UID 1381151 and specified columns
#final_df = gridMET[gridMET['UID'] == 1381151]
final_df = gridMET[["day", "month", "year", "Tmin", "Tmax", "pr", "eto"]]
#final_df = final_df[["UID", "day", "month", "year", "Tmin", "Tmax", "pr", "eto"]]

 
# download gridMET final_df as txt
final_df.to_csv('gridMET_1381151.txt', sep=' ', index=False, header=True)              

gridMET_list = []
for i in gridMET:
    df = pd.DataFrame(gridMET['UID'][i])
    gridMET_list.append(df)           
    
   
def gridmet(x):
    u = [] 
    for i in range(0, len(x)):
        df = x[x['UID'] == i]
        df = pd.DataFrame(df)
        u.append(df)
        return(u)

h = gridmet(gridMET)
        
        
        
        
        
        
        