#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 08:11:18 2022

@author: wayne
"""

! pip install statsmodels

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from sklearn.metrics import * 
from sklearn.linear_model import LinearRegression
from math import *
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import datetime
wd=getcwd() # set working directory
chdir(wd)

# read in df
et_means_test = pd.read_csv(wd + '/data/analysis_results/et_df_test.csv', index_col=0)
yield_df_test = pd.read_csv(wd + '/data/analysis_results/yield_df_test.csv', index_col=0)
irrig_df_test = pd.read_csv(wd + '/data/analysis_results/irrig_df_test.csv', index_col =0)


et_means_test = et_means_test[['time', 'disalexi', 
                     'ensemble', 'geesebal', 
                     'ptjpl', 'sims', 'ssebop', 'Et']]

et_means_test = et_means_test.rename(columns={'Et': 'aquacrop'})

et_means_test['year'] = pd.to_datetime(et_means_test['time']).dt.strftime('%Y')

# make dfs pivoted longer
et_pivot1 = pd.melt(et_means_test, id_vars=['time', 'year'],
                  var_name='model_name', value_name='values')

et_pivot2 = pd.melt(et_means_test, id_vars=['time', 'year', 'aquacrop'],
                  var_name='model_name', value_name='values')


# irrig pivoted longer
irrig_df_test = irrig_df_test.rename(columns={'Seasonal irrigation (mm)': 'Aquacrop',
                                              'irrig_wimas': 'WIMAS'})

irrig_long = pd.melt(irrig_df_test, id_vars = ['UID', 'Year'],
                     var_name = 'model',
                     value_name = 'values')

## yield pivoted_longer
yield_df_test = yield_df_test.rename(columns={'Yield (tonne/ha)': 'Aquacrop',
                                              'YieldUSDA': 'USDA-NASS'})

yield_long = pd.melt(yield_df_test, id_vars = ['Year'],
                     var_name = 'model',
                     value_name = 'values')


# plot showing ET, Irrig and Yield models
#etPal = ["#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"] #D55E00
etPal = ["#000000", "#999933", "#56B4E9", "grey", "#44AA99", "#0072B2", "#FFA500", "#CC79A7"]


sns.set(font_scale = 1.8)
sns.set_style("ticks")
fig, axs = plt.subplots(ncols=2, nrows = 3, figsize=(19,20))
fig.subplots_adjust(hspace=.3)
sns.scatterplot(x='Year',y='values', data=yield_long, ax=axs[1,1], hue = 'model', palette = ['#11823b', "#FFA500"], s=90, legend = False) 
sns.lineplot(x='Year',y='values', data=yield_long, ax=axs[1,1], hue = 'model', palette = ['#11823b', "#FFA500"]) 
sns.scatterplot(y='Aquacrop',x='USDA-NASS', data=yield_df_test, ax=axs[1,0], color = 'black', s=90) 
sns.scatterplot(x='Year',y='values', data=irrig_long, ax=axs[0,1], hue = 'model', palette = ['#344b5b', "#FFA500"], s=90, legend = False) 
sns.lineplot(x='Year',y='values', data=irrig_long, ax=axs[0,1], hue = 'model', palette = ['#344b5b', "#FFA500"]) 
sns.scatterplot(y='Aquacrop',x='WIMAS', data=irrig_df_test, ax=axs[0,0], color = 'black', s=90)
sns.lineplot(x='time', y='values', data=et_pivot1, ax=axs[2,1], hue = 'model_name', palette = sns.color_palette(etPal), alpha = .2) 
sns.lineplot(x='time', y='aquacrop', data=et_means_test, ax=axs[2,1],  color = "#FFA500") 
sns.scatterplot(y='aquacrop', x='values', data=et_pivot2, ax=axs[2,0], hue = 'model_name', palette = sns.color_palette(etPal), alpha = .5, s=60) 
ax=axs[1,1].set_ylabel("Yield (t/ha)", size = 22, weight='bold')
ax=axs[1,1].set_xlabel("")
ax=axs[0,1].set_ylabel('Irrigation (mm)', size = 22, weight='bold')
ax=axs[0,1].set_xlabel('')
ax=axs[2,1].set_ylabel('ET (mm)', size = 22, weight='bold')
ax=axs[2,1].set_xlabel('')
ax=axs[2,0].axline((0, 0), slope=1, color = "grey")
ax=axs[0,0].axline((250, 250), slope=1, color = "grey")
ax=axs[1,0].axline((10, 10), slope=1, color = "grey")
ax=axs[0,0].set(ylim=(250, 800), xlim=(250,800))
ax=axs[0,1].set(ylim=(250, 800))
ax=axs[1,0].set(ylim=(9.5, 15), xlim=(9.5,15))
ax=axs[1,1].set(ylim=(9.5, 15))
ax=axs[2,0].set(ylim=(-10, 280), xlim=(-10,280))
ax=axs[2,1].tick_params(axis='x', rotation=70)
ax=axs[2,1].xaxis.set_major_locator(plt.MaxNLocator(10))
ax=axs[1,1].xaxis.set_major_locator(plt.MaxNLocator(8))
ax=axs[0,1].xaxis.set_major_locator(plt.MaxNLocator(8))
ax=axs[2,1].legend().set_title('') # remove legend titles
ax=axs[2,0].get_legend().remove()
ax=axs[0,0].legend().set_title('')
ax=axs[1,1].legend().set_title('')
ax=axs[0,1].legend().set_title('')
ax=axs[1,0].set_xlabel('USDA Yield (t/ha)', size = 22, weight='bold')
ax=axs[1,0].set_ylabel('AquaCrop Yield (t/ha)', size = 22, weight='bold')
ax=axs[0,0].set_xlabel('WIMAS Irrigation (mm)', size = 22, weight='bold')
ax=axs[0,0].set_ylabel('AquaCrop Irrigation (mm)', size = 22, weight='bold')
ax=axs[2,0].set_xlabel('OpenET (mm)', size = 22, weight='bold')
ax=axs[2,0].set_ylabel('AquaCrop ET (mm)', size = 22, weight='bold')
ax=axs[1,1].legend(bbox_to_anchor=(1.3, 0.4), loc='lower right', fontsize=14)
ax=axs[0,1].legend(bbox_to_anchor=(1.25, 0.4), loc='lower right', fontsize=14)
ax=axs[2,1].legend(bbox_to_anchor=(1.25, 0.2), loc='lower right', fontsize=14)
#ax=axs[1,1].axvspan(2013, 2014, color='grey', alpha=0.2)
ax=axs[0,1].axvline(2013, 0,15, ls='--', color='black', alpha = .5)
ax=axs[1,1].axvline(2013, 0,15, ls='--', color='grey', alpha = .5)
#fig.subplots_adjust(hspace=.9)
fig.savefig('results/visuals/model_comparison_plot_yieldIrrigationET_irrig_triggered_when_SMT<80%.png', format='png', dpi=600)





### ROOT GROWTH

# see if there are differences in root growth vals
crp_grwth =  model_df_crp_grwth
crp_grwth = crp_grwth[crp_grwth['z_root'] > 0] # filter for z root values > 0
crp_grwth['yearmon'] = pd.to_datetime(crp_grwth['Date']).dt.strftime('%Y-%m')
crp_grwth['year'] = pd.to_datetime(crp_grwth['Date']).dt.strftime('%Y')


# boxplots for the root growth vals
g = sns.FacetGrid(crp_grwth, col="year", col_wrap=3)
g.map_dataframe(sns.boxplot, x = 'yearmon', y = 'z_root')
g.set_xticklabels(['5',
                   '6', '7', '8', '9'])
g.set_xlabels(label = "Month")
g.set_ylabels(label = "Z-root (m)")


### CROP GROWTH
# see if there are differences between biomass and biomass_no stress
# pivot the biomass and biomass_ns longer
crp_grwth_pivot  = crp_grwth[['year', 'yearmon', 'biomass', 'biomass_ns']]

crp_grwth_pivot = crp_grwth_pivot[crp_grwth_pivot['biomass'] > 0] #filter for instances where biomass is >0

crp_grwth_pivot = pd.melt(crp_grwth_pivot, id_vars=['year', 'yearmon'],
                  var_name='type', value_name='values')



# faceted boxplots
g = sns.FacetGrid(crp_grwth_pivot, col="year", col_wrap=3)
g.map_dataframe(sns.boxplot, x = 'yearmon', y = 'values', hue = 'type', )
#g.set_xticklabels(rotation=30)
g.set_xticklabels(['5',
                   '6', '7', '8', '9'])
g.set_xlabels(label = "Month")
g.set_ylabels(label = "Biomass (kg/ha)")
g.add_legend()
g.fig.subplots_adjust(top=0.95)
g.fig.suptitle('Rainfed', fontsize=16)


## graph show soil moisture through time in the upper layer
water_storage = model_df_water_storage[model_df_water_storage['Date'].between('2000-01-01','2003/12/31')]
p = sns.lineplot(x = 'Date', y= 'th1', data = water_storage)
#p.label(x = '')
p.tick_params(axis='x', rotation=90)
p.set(title='Soil-water content (th1)', xlabel = '')



# calculate the min and max temperatures for each month
monthly_temp_min = wdf_v2.groupby(['yearmon'])[['MinTemp', 'MaxTemp']].min().reset_index()
monthly_temp_min = monthly_temp_min.rename(columns={
                   'MinTemp': 'min_mintemp',
                   'MaxTemp': 'min_maxtemp'})

monthly_temp_max = wdf_v2.groupby(['yearmon'])[['MinTemp', 'MaxTemp']].max().reset_index()
monthly_temp_max = monthly_temp_max.rename(columns={
                   'MinTemp': 'max_mintemp',
                   'MaxTemp': 'max_maxtemp'})

monthly_temp_max = monthly_temp_max.drop(columns=['yearmon'])

monthly_temp = pd.concat([monthly_temp_min, monthly_temp_max], axis=1)




fig, ax = plt.subplots(figsize=(10,6))

sns.scatterplot(x = 'yearmon', y = 'min_mintemp', data = monthly_temp, color = 'blue')
sns.lineplot(x = 'yearmon', y = 'min_mintemp', data = monthly_temp, color = 'blue', size =.5)
sns.scatterplot(x = 'yearmon', y = 'min_maxtemp', data = monthly_temp, color = 'orange')
sns.lineplot(x = 'yearmon', y = 'min_maxtemp', data = monthly_temp, color = 'orange', size = .5)
sns.scatterplot(x = 'yearmon', y = 'max_mintemp', data = monthly_temp, color = 'green')
sns.lineplot(x = 'yearmon', y = 'max_mintemp', data = monthly_temp, color = 'green', size = .5)
sns.scatterplot(x = 'yearmon', y = 'max_maxtemp', data = monthly_temp, color = 'red')
sns.lineplot(x = 'yearmon', y = 'max_maxtemp', data = monthly_temp, color = 'red', size = .5)
plt.xticks(rotation=90, size = 8)


xaxis.set_major_locator(plt.MaxNLocator(12))

np.nanmax(wdf_pivot.iloc[:, 1].values)


