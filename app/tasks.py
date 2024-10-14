# tasks.py
from celery import shared_task
import time
from .celery_app import celery_app
import pandas as pd 
import os
from scipy.stats import chi2_contingency
from typing import Dict
import io

@celery_app.task
def data_analysis_task(data:str,sensitive_attr:str,outcome:str)->Dict[str,Dict[str,int]]:
    df=pd.read_csv(io.StringIO(data))
    contingency_table = pd.crosstab(df[outcome], df[sensitive_attr])
    result:Dict[str,Dict[str,int]]={}
    d:Dict[str,Dict[str,int]]=contingency_table.to_dict()
    result['contingency_table']=d
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
    result['chi2']=chi2
    result['p_value']=p_value
    return result
    



