from abc import ABC, abstractmethod
import pandas as pd 
import os
from scipy.stats import chi2_contingency
from typing import Dict

class FairnessMetric(ABC):
    @abstractmethod
    def calculate(self, y_true, sensitive_attribute):
        pass

class DemographicParity(FairnessMetric):
    def calculate(self, df, outcome, sensitive_attribute):
        
        pass

class RepresentationParity(FairnessMetric):
    def calculate(self, y_true,sensitive_attribute):
        # Implementation for Equalized Odds
        pass


if __name__ == "__main__":
    # Load the dataset
    sensitive_attr='Gender'
    outcome='Hired'
    file_path = os.path.join(os.path.dirname(__file__), "test_data.csv")
    data = pd.read_csv(file_path)
    contingency_table = pd.crosstab(data[outcome], data[sensitive_attr])
    d:Dict[str,Dict[str,int]]=contingency_table.to_dict()
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
    print(f"Chi-Square Statistic: {chi2}, P-value: {p_value}")

  
    


