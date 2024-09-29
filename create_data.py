import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer


education_levels = ['High School', 'Associate', 'Bachelor\'s', 'Master\'s', 'PhD']
skills_pool = ['Python', 'SQL', 'Data Analysis', 'Machine Learning', 'AI']

# Introduce bias in the 'Hired' column (biased towards males)
def decide_hiring(row):
    if row['Gender'] == 'Male':
        return np.random.choice(['Yes', 'No'], p=[0.9, 0.1])
    else:
        return np.random.choice(['Yes', 'No'], p=[0.2, 0.8])

def generate_imbalanced_data(num_samples=1000):
    # Set random seed for reproducibility
    np.random.seed(42)

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

def data_preprocessing(df):
    # Encode categorical variables
    le_gender = LabelEncoder()
    df['Gender'] = le_gender.fit_transform(df['Gender'])  # Male: 1, Female: 0
    # One-hot encoding for Education Level
    ct = ColumnTransformer([('education', OneHotEncoder(), ['Education Level'])], remainder='passthrough')
    X = ct.fit_transform(df.drop(columns=['Applicant ID', 'Hired', 'Skills']))  # Drop ID, Hired, Skills (Skills for simplicity)
    # Label encoding for target variable
    le_hired = LabelEncoder()
    y = le_hired.fit_transform(df['Hired'])
    return X, y

# df = generate_imbalanced_data()
# X, y = data_preprocessing(df)
# # Split the data
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# # Train the model
# model = LogisticRegression()
# model.fit(X_train, y_train)

# # Predict on the test set
# y_pred = model.predict(X_test)
# # Evaluate the model
# report = classification_report(y_test, y_pred, target_names=['Not Hired', 'Hired'])
# print(report)
# # Check the predictions based on gender
#
# print (X,y)
# df_hired = df[df['Hired'] == 'Yes']
# df_hired['Gender'].value_counts().plot(kind='bar', color=['blue', 'pink'])
# plt.title('Number of Hires by Gender')
# plt.xlabel('Gender')
# plt.ylabel('Number of Hires')
# plt.xticks(rotation=0)
# plt.savefig('hires_by.png')





