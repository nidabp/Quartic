
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import math
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.stats import *

import re
get_ipython().run_line_magic('matplotlib', 'inline')


# In[2]:


filepath = 'Assignment/'
df_train = pd.read_csv(filepath + 'data_train.csv')
df_test = pd.read_csv(filepath + 'data_test.csv')
df_train.shape


# In[3]:


df_test.shape


# In[4]:


df_train.describe(include='all')


# In[5]:


df_test.describe(include='all')


# In[6]:


for i in range(1,15):
        name = 'cat' + str(i)
        df_train[name] = pd.Categorical(df_train[name])
        df_test[name] = pd.Categorical(df_test[name])       


# In[7]:


def display_all(df):
    with pd.option_context("display.max_rows",1000):
        with pd.option_context("display.max_columns",1000):
            display(df)
        


# In[8]:


display_all(df_train.head().T)


# In[9]:


df_train.info(verbose=True, null_counts=True)


# In[10]:


null_columns=df_train.columns[df_train.isnull().any()]
df_train[null_columns].isnull().sum()


# In[11]:


def is_numeric_dtype(col):
    if col.dtype == 'int64' or col.dtype == 'float64' or col.dtype == 'bool':
        return 1
    else :
        return 0

def preprocesstrain(df):
    meddict =  {}
#     for i in range(1,20):
#         name = 'der' + str(i)
#         df = df.drop(columns=name)
    
    for n,c in df.items():
        if is_numeric_dtype(c):
            med = c.median()
            if pd.isnull(c).sum(): 
                df[n] = c.fillna(med)
            meddict[n] = med
                
    return df,meddict

def preprocesstest(df,meddict):
    
#     for i in range(1,20):
#         name = 'der' + str(i)
#         df = df.drop(columns=name)
        
    for n,c in df.items():
        if is_numeric_dtype(c):
            if pd.isnull(c).sum():
                med = meddict[n]
                df[n] = c.fillna(med)
                
    return df

def numericalize(df):
    for n,c in df.items():
        if not is_numeric_dtype(c):
            df[n] = df[n].cat.codes+1
    return df
        
def OneHotEncode(df_train,df_test,max_cat_length) :
    
    len_train = df_train.shape[0]
    len_test = df_test.shape[0]
    
    df = pd.concat([df_train,df_test])
    for n,c in df.items():
        if not is_numeric_dtype(c):
            if len(c.unique()) < max_cat_length : 
                df = pd.get_dummies(df,columns=[n])
            
    df_train = df.iloc[0:len_train,:]
    df_test = df.iloc[len_train:,:]
    
    return df_train, df_test
        
        
def split_vals(a,n): return a[:n].copy(), a[n:].copy()   


# In[12]:


def GetPCA(df,var):
    scaler = StandardScaler()
    scaler.fit(df)
    df_img = scaler.transform(df)
    pca = PCA(var)
    pca.fit(df_img)
    return pca


# In[13]:


def GetTrainData(df_raw):
    
    median_dict = {}
    
    df = df_raw.copy()
    y = df['target'].values
    df.drop(['target'],axis=1,inplace=True)
    df.head().T
    
    df,median_dict = preprocesstrain(df)
    
    df = numericalize(df)
        
    return df,y,median_dict

def GetTrainValid(df,y,n_valid):
   
    n_train = len(df) - n_valid
    X_train, X_valid = split_vals(df,n_train)
    y_train, y_valid = split_vals(y,n_train)
    
    return X_train,y_train,X_valid,y_valid

def ReadyTestData(df_test,median_dict) :
    
    predmat = np.zeros((df_test.shape[0],2))
    
    df = df_test.copy()
    ids = df['id'].values
    #df.drop(['id'],axis=1,inplace=True)
    
    df = preprocesstest(df,median_dict)
    
    df = numericalize(df)
        
    return df,ids


# In[14]:


mediandict = {}
df,y,mediandict = GetTrainData(df_train)
X_test,ids = ReadyTestData(df_test,mediandict)
df,X_test = OneHotEncode(df,X_test,7)


# In[15]:


print(X_test.shape)


# In[16]:


display_all(df.head().T)


# In[17]:


X_train,y_train,X_valid,y_valid = GetTrainValid(df,y,25000)


# In[18]:


corrdata = df.iloc[:,0:42]
corrdata.apply(lambda x : pd.factorize(x)[0]).corr(method='pearson', min_periods=1)


# In[19]:


i = 9
h = df.iloc[:,i]
h = np.sort(h)
hmean = np.mean(h)
hstd = np.std(h)
pdf = norm.pdf(h, hmean, hstd)
plt.plot(h, pdf)


# In[43]:


h = df.iloc[:,43]
h.value_counts().plot(kind='bar')


# In[40]:


chitestmat = list()
for i in range(42,47) :
    ind_chi_test = chisquare(df.iloc[:,i])
    chitestmat.append(ind_chi_test[1])
np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})
display_all(chitestmat)


# In[42]:


colcount = len(df.columns)
ttestmat = np.zeros((5,5))
for i in range(42,47) :
    for j in range(42,47) :
        if i != j :
            ind_t_test = ttest_ind(df.iloc[:,i],df.iloc[:,j])
            ttestmat[i-42][j-42] = ind_t_test[1]
np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})
display_all(ttestmat)


# In[23]:


h = pd.Series(y.tolist())
h.value_counts().plot(kind='bar')


# In[24]:


def TrainRandomForest(X_train,y_train,X_valid,y_valid):

    m = RandomForestClassifier(n_estimators=40,n_jobs=-1,oob_score=True)
    get_ipython().run_line_magic('time', 'm.fit(X_train,y_train)')
    res = [m.score(X_train,y_train),m.score(X_valid,y_valid)]
    if hasattr(m,'oob_score_'): res.append(m.oob_score_)
    print(res)
    
    return m


# In[25]:


def TrainLogisticRegression(X_train,y_train,X_valid,y_valid):
    m = LogisticRegression()
    get_ipython().run_line_magic('time', 'm.fit(X_train, y_train)')
    res = [m.score(X_train,y_train),m.score(X_valid,y_valid)]
    print(res)
    
    return m


# In[26]:


def PredictTestSet(X_test, ids, predicted_model):
          
    y = predicted_model.predict(X_test)
    predmat = np.column_stack((ids,y)) 
    
    return predmat

def GetImportances(predictedmodel,df) :
    importances = predictedmodel.feature_importances_
    indices = np.argsort(importances)[::-1]
    df_imp = pd.DataFrame(columns=['cols','imp'])
    j = 0
    for f in range(df.shape[1]):
        df_imp.loc[j] = [df.columns[indices[f]],importances[indices[f]]]
        j = j + 1
    return df_imp
    


# In[27]:


# pca = GetPCA(X_train,0.95)
# X_train = pca.transform(X_train)
# X_valid = pca.transform(X_valid)


# In[28]:


predictedmodel = TrainRandomForest(X_train,y_train,X_valid,y_valid)


# In[29]:


yvalid_predict = predictedmodel.predict(X_valid)
print(classification_report(y_valid, yvalid_predict))


# In[30]:


# X_test = pca.transform(X_test)
predmat = PredictTestSet(X_test, ids, predictedmodel)
df_print = pd.DataFrame(predmat,columns=["id","target"])
df_print.to_csv("C:\\Users\\Admin\\Downloads\\QuarticPred.csv",index=False)


# In[31]:


get_ipython().run_line_magic('time', 'preds = np.stack([t.predict(X_valid) for t in predictedmodel.estimators_])')
np.mean(preds[:,0]),np.std(preds[:,0])


# In[32]:


df_imp = GetImportances(predictedmodel,df); df_imp[:10]


# In[33]:


df_imp.plot('cols','imp',figsize=(10,6),legend=False)


# In[34]:


to_keep = df_imp[df_imp.imp > 0.02].cols;len(to_keep)


# In[35]:


mediandict = {}
df,y,mediandict = GetTrainData(df_train)
df_keep = df[to_keep].copy()
X_train_new,y_train_new,X_valid_new,y_valid_new = GetTrainValid(df_keep,y,250000)
newmodel = TrainRandomForest(X_train_new,y_train_new,X_valid_new,y_valid_new)


# In[36]:


fi = GetImportances(newmodel,df_keep); fi[:]


# In[37]:


fi.plot('cols','imp','barh',figsize=(12,7),legend=False)


# In[38]:


predictedmodel = TrainLogisticRegression(X_train,y_train,X_valid,y_valid)


# In[39]:


yvalid_predict = predictedmodel.predict(X_valid)
print(classification_report(y_valid, yvalid_predict))

