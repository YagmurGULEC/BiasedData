import numpy as np
import pandas as pd
import random
from functools import lru_cache


education_levels = ['High School', 'Associate', 'Bachelor\'s', 'Master\'s', 'PhD']
skills_pool = ['Python', 'SQL', 'Data Analysis', 'Machine Learning', 'AI']

# Introduce bias in the 'Hired' column (biased towards males)
def decide_hiring(row: pd.Series):
    if row['Gender'] == 'Male':
        return np.random.choice(['Yes', 'No'], p=[0.9, 0.1])
    else:
        return np.random.choice(['Yes', 'No'], p=[0.2, 0.8])


def generate_imbalanced_data(num_samples:int =1000)->pd.DataFrame:
    # Set random seed for reproducibility
    np.random.seed(42)
    print ("Generating data")
    # Parameters
    num_samples = 1000
    education_levels = ['High School', 'Associate', 'Bachelor\'s', 'Master\'s', 'PhD']
    skills_pool = ['Python', 'SQL', 'Data Analysis', 'Machine Learning', 'AI']
    genders = ['Male', 'Female']

    # Generate synthetic data
    data = {
    'Applicant ID': range(1, num_samples + 1),
    'Education Level': np.random.choice(education_levels, num_samples, p=[0.1, 0.15, 0.4, 0.25, 0.1]),
    'Years of Experience': np.random.randint(1, 20, num_samples),
    # 'Skills': [', '.join(random.sample(skills_pool, k=np.random.randint(1, 4))) for _ in range(num_samples)],
    'Gender': np.random.choice(genders, num_samples, p=[0.6, 0.4])  # Slight bias in male population
    }
    # Create DataFrame
    df = pd.DataFrame(data)
    df['Hired'] = df.apply(decide_hiring, axis=1)
    return df


if __name__ == "__main__":
    df = generate_imbalanced_data()
    print (df.head())
    df.to_csv("test_data.csv",index=False)






