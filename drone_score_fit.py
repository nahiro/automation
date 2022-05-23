#!/usr/bin/env python
import numpy as np
import pandas as pd
from itertools import combinations
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from optparse import OptionParser,IndentedHelpFormatter

# Constants
PARAMS = ['Sb','Sg','Sr','Se','Sn','Nb','Ng','Nr','Ne','Nn','NDVI','GNDVI','RGI','NRGI']
OBJECTS = ['BLB','Blast','StemBorer','Rat','Hopper','Drought']
CRITERIAS = ['R2_Score','R2','RMSE','AIC','BIC']

# Default values
OUT_FNAM = 'drone_score_fit.csv'
X_PARAM = ['Nb','Ng','Nr','Ne','Nn','NDVI','GNDVI','NRGI']
X_PRIORITY = ['NDVI','GNDVI','NRGI','Nn','Ne','Nr','Ng','Nb','RGI','Sn','Se','Sr','Sg','Sb']
Y_PARAM = ['BLB']
VMAX = 5.0
NMAX = 2
CRITERIA = 'R2_Score'
N_CROSS = 10

# Read options
parser = OptionParser(formatter=IndentedHelpFormatter(max_help_position=200,width=200))
parser.add_option('-I','--inp_fnam',default=None,action='append',help='Input file name (%default)')
parser.add_option('-O','--out_fnam',default=OUT_FNAM,help='Output file name (%default)')
parser.add_option('-x','--x_param',default=None,action='append',help='Candidate explanatory variable ({})'.format(X_PARAM))
parser.add_option('--x_priority',default=None,action='append',help='Priority of explanatory variable ({})'.format(X_PRIORITY))
parser.add_option('-y','--y_param',default=None,action='append',help='Objective variable ({})'.format(Y_PARAM))
parser.add_option('-V','--vmax',default=VMAX,type='float',help='Max variance inflation factor (%default)')
parser.add_option('-N','--nmax',default=NMAX,type='int',help='Max number of explanatory variable in a formula (%default)')
parser.add_option('-C','--criteria',default=CRITERIA,help='Selection criteria (%default)')
parser.add_option('-n','--n_cross',default=N_CROSS,type='int',help='Number of cross validation (%default)')
(opts,args) = parser.parse_args()
if opts.inp_fnam is None:
    raise ValueError('Error, opts.inp_fnam={}'.format(opts.inp_fnam))
if not opts.criteria in CRITERIAS:
    raise ValueError('Error, unsupported criteria >>> {}'.format(opts.criteria))
if opts.x_param is None:
    opts.x_param = X_PARAM
if opts.y_param is None:
    opts.y_param = Y_PARAM
if opts.x_priority is None:
    opts.x_priority = X_PRIORITY
for param in opts.x_priority:
    if not param in PARAMS:
        raise ValueError('Error, unknown explanatory variable >>> {}'.format(param))
for param in opts.y_param:
    if not param in OBJECTS:
        raise ValueError('Error, unknown objective variable >>> {}'.format(param))
for param in opts.x_param:
    if not param in opts.x_priority:
        raise ValueError('Error, priority of {} is not given.'.format(param))
indx_param = [opts.x_priority.index(param) for param in opts.x_param]
x_param = [opts.x_param[indx] for indx in np.argsort(indx_param)]
nx = len(x_param)

# Read data
X = {}
Y = {}
for param in opts.x_param:
    X[param] = []
for param in opts.y_param:
    Y[param] = []
for fnam in opts.inp_fnam:
    df = pd.read_csv(fnam,comment='#')
    df.columns = df.columns.str.strip()
    for param in opts.x_param:
        if not param in df.columns:
            raise ValueError('Error in finding column for {} >>> {}'.format(param,fnam))
        X[param].extend(list(df[param]))
    for param in opts.y_param:
        if not param in df.columns:
            raise ValueError('Error in finding column for {} >>> {}'.format(param,fnam))
        Y[param].extend(list(df[param]))
X = pd.DataFrame(X)
Y = pd.DataFrame(Y)

# Eliminate multicollinearity
for indx in reversed(range(1,nx)):
    vif = variance_inflation_factor(X[x_param].values,indx)
    if vif > opts.vmax:
        del x_param[indx]
nx = len(x_param)
X_all = X[x_param]

# Make formulas
model_xs = []
model_r2_scores = []
model_r2s = []
model_rmses = []
model_aics = []
model_bics = []
model_fs = []
coef_values = []
coef_errors = []
coef_ps = []
coef_ts = []
for n in range(1,min(opts.nmax,nx)+1):
    for c in combinations(x_param,n):
        x_list = list(c)
        X = sm.add_constant(X_all[x_list]) # adding a constant
        x_all = list(X.columns)
        model = sm.OLS(Y,X).fit()
        model_xs.append(x_all)
        model_r2s.append(model.rsquared_adj)
        model_rmses.append(np.sqrt(model.mse_resid)) # adjusted for df_resid
        model_aics.append(model.aic)
        model_bics.append(model.bic)
        model_fs.append(model.f_pvalue)
        coef_values.append(model.params)
        scores = []
        values = {}
        errors = {}
        for param in x_all:
            values[param] = []
        kf = KFold(n_splits=opts.n_cross,random_state=None,shuffle=False)
        for train_index,test_index in kf.split(X):
            X_train,X_test = X.iloc[train_index],X.iloc[test_index]
            Y_train,Y_test = Y.iloc[train_index],Y.iloc[test_index]
            model = sm.OLS(Y_train,X_train).fit()
            predictions = model.predict(X_test)
            scores.append(r2_score(Y_test,predictions))
            for param in x_all:
                values[param].append(model.params[param])
        for param in x_all:
            errors[param] = np.std(values[param])
        coef_errors.append(errors)
        model_r2_scores.append(np.mean(scores))
        coef_ps.append(model.pvalues)
        coef_ts.append(model.tvalues)

# Sort formulas
if opts.criteria == 'R2_Score':
    model_indx = np.argsort(model_r2_scores)[::-1]
elif opts.criteria == 'R2':
    model_indx = np.argsort(model_r2s)[::-1]
elif opts.criteria == 'RMSE':
    model_indx = np.argsort(model_rmses)
elif opts.criteria == 'AIC':
    model_indx = np.argsort(model_aics)
elif opts.criteria == 'BIC':
    model_indx = np.argsort(model_bics)
else:
    raise ValueError('Error, unsupported criteria >>> {}'.format(opts.criteria))

# Output results
with open(opts.out_fnam,'w') as fp:
    for v in CRITERIAS:
        fp.write('{:>13s},'.format(v))
    fp.write('{:>13s},{:>2s}'.format('P','N'))
    for n in range(min(opts.nmax,nx)+1):
        fp.write(',{:>13s},{:>13s},{:>13s},{:>13s},{:>13s}'.format('P{}_param'.format(n),'P{}_value'.format(n),'P{}_error'.format(n),'P{}_p'.format(n),'P{}_t'.format(n)))
    fp.write('\n')
    for indx in model_indx:
        fp.write('{:13.6e},{:13.6e},{:13.6e},{:13.6e},{:13.6e},{:13.6e},{:2d}'.format(model_r2_scores[indx],model_r2s[indx],model_rmses[indx],model_aics[indx],model_bics[indx],model_fs[indx],len(model_xs[indx])))
        for param in model_xs[indx]:
            fp.write(',{:>13s},{:13.6e},{:13.6e},{:13.6e},{:13.6e}'.format(param,coef_values[indx][param],coef_errors[indx][param],coef_ps[indx][param],coef_ts[indx][param]))
        for n in range(len(model_xs[indx]),min(opts.nmax,nx)+1):
            fp.write(',{:>13s},{:13.6e},{:13.6e},{:13.6e},{:13.6e}'.format('None',np.nan,np.nan,np.nan,np.nan))
        fp.write('\n')
