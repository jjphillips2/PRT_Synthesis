#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baseline Linear Modeling
"""

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import datetime as datetime
import numpy as np
from sklearn.model_selection import train_test_split
import statsmodels.api as sm


# read in data, keep only necessary vars
path = '/Users/sumati/Documents/CMU/Academics/Spring2023/Capstone/code/data/'
summerchargeData = pd.read_csv(path+'ChargingDataJuly.csv')
winterchargeData = pd.read_csv(path+'WinterChargingData.csv')
winterchargeData = winterchargeData[~pd.isna(winterchargeData.Duration)]

keep_vars = ['Date', 'Duration', 'Distance', 'Battery Change']

#chargeData = pd.concat([summerchargeData[keep_vars], winterchargeData[keep_vars]]).reset_index(drop = True)
chargeData = winterchargeData.copy()
chargeData = chargeData[keep_vars]
chargeData.rename(columns = {'Battery Change': 'BatteryChange'}, inplace = True)
chargeData['Distance'] = chargeData.Distance.apply(lambda x: float(x)) # adjust data type

# EDA on vars of interest
sns.scatterplot(x = chargeData.Distance, y = chargeData.BatteryChange)

    # linear negative linear trend, some outliers along longer tirps 

# format duration to also plot
start_time0 = datetime.datetime.strptime('00:00:00', '%H:%M:%S')

for i in range(len(chargeData)):
    current_duration = datetime.datetime.strptime(chargeData.loc[i, 'Duration'], '%H:%M:%S')
    chargeData.loc[i, 'timeDelta_seconds'] = (current_duration - start_time0).total_seconds()
    chargeData.loc[i, 'timeDelta_minutes'] = chargeData.loc[i, 'timeDelta_seconds'] / 60
    
chargeData.head()

sns.scatterplot(x = chargeData.timeDelta_seconds, y = chargeData.BatteryChange)
sns.scatterplot(x = chargeData.timeDelta_minutes, y = chargeData.BatteryChange)


# looks like trends between duration and distance are similar, so in terms of scale i'd rather do distance

# baseline regression 

X = chargeData[['Distance']].values
y = chargeData[['BatteryChange']].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = .2)

X_train = sm.add_constant(X_train)
model = sm.OLS(y_train, X_train)
results = model.fit()
print(results.summary())

train_preds = results.predict()

# check predictions/residuals
plt.scatter(y_train, train_preds)

residuals = (y_train.reshape(len(y_train)) - train_preds)
plt.scatter(x = y_train, y = residuals)
plt.axhline(y = 0, color = 'red')






