import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import statsmodels.api as sm
from optparse import OptionParser,IndentedHelpFormatter

# Constants
PARAMS = ['Sb','Sg','Sr','Se','Sn','Nb','Ng','Nr','Ne','Nn','NDVI','GNDVI','RGI']

# Default values
X_PARAM = ['Nb','Ng','Nr','Ne','Nn','NDVI','GNDVI','RGI']
X_PRIORITY = ['NDVI','GNDVI','RGI','Nn','Ne','Nr','Ng','Nb','Sn','Se','Sr','Sg','Sb']
Y_PARAM = 'DamagedByBLB'

# Read options
parser = OptionParser(formatter=IndentedHelpFormatter(max_help_position=200,width=200))
parser.add_option('-I','--inp_fnam',default=None,action='append',help='Input file name (%default)')
parser.add_option('-x','--x_param',default=None,action='append',help='Candidate explanatory variable ({})'.format(X_PARAM))
parser.add_option('--x_priority',default=None,action='append',help='Priority of explanatory variable ({})'.format(X_PRIORITY))
parser.add_option('-y','--y_param',default=Y_PARAM,help='Objective variable (%default)')
(opts,args) = parser.parse_args()
if opts.inp_fnam is None:
    raise ValueError('Error, opts.inp_fnam={}'.format(opts.inp_fnam))
if opts.x_param is None:
    opts.x_param = X_PARAM
if opts.x_priority is None:
    opts.x_priority = X_PRIORITY
for param in opts.x_param:
    if not param in opts.x_priority:
        raise ValueError('Error, priority of {} is not given.'.format(param))

X = {}
Y = {}
for param in opts.x_param:
    X[param] = []
Y[opts.y_param] = []
for fnam in opts.inp_fnam:
    df = pd.read_csv(fnam,comment='#')
    df.columns = df.columns.str.strip()
    if not opts.y_param in df.columns:
        raise ValueError('Error in finding column for {} >>> {}'.format(opts.y_param,fnam))
    Y[opts.y_param].extend(list(df[opts.y_param]))
    for param in opts.x_param:
        if not param in df.columns:
            raise ValueError('Error in finding column for {} >>> {}'.format(param,fnam))
        X[param].extend(list(df[param]))
X = pd.DataFrame(X)
Y = pd.DataFrame(Y)

"""
df = pd.DataFrame(Stock_Market,columns=['Year','Month','Interest_Rate','Unemployment_Rate','Stock_Index_Price'])

X = df[['Interest_Rate','Unemployment_Rate']] # here we have 2 variables for multiple regression. If you just want to use one variable for simple linear regression, then use X = df['Interest_Rate'] for example.Alternatively, you may add additional variables within the brackets
Y = df['Stock_Index_Price']
 
# with sklearn
regr = linear_model.LinearRegression()
regr.fit(X, Y)

print('Intercept: \n', regr.intercept_)
print('Coefficients: \n', regr.coef_)

# prediction with sklearn
New_Interest_Rate = 2.75
New_Unemployment_Rate = 5.3
print ('Predicted Stock Index Price: \n', regr.predict([[New_Interest_Rate ,New_Unemployment_Rate]]))

# with statsmodels
X_org = X.copy()
X = sm.add_constant(X) # adding a constant
 
model = sm.OLS(Y, X).fit()
predictions = model.predict(X) 
 
print_model = model.summary()
print(print_model)

for i in range(10):
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.1)
    model = sm.OLS(y_train, X_train).fit()
    predictions = model.predict(X_train) 
     
    print_model = model.summary()
    print(print_model)
"""
