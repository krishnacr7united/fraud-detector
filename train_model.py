import os
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Download dataset from Kaggle if not present
if not os.path.exists('creditcard.csv'):
    print("Downloading dataset from Kaggle...")
    os.system('pip install kaggle --quiet')
    
    kaggle_dir = os.path.expanduser('~/.kaggle')
    os.makedirs(kaggle_dir, exist_ok=True)
    
    username = os.environ.get('KAGGLE_USERNAME', '')
    key = os.environ.get('KAGGLE_KEY', '')
    
    with open(os.path.join(kaggle_dir, 'kaggle.json'), 'w') as f:
        f.write(f'{{"username":"{username}","key":"{key}"}}')
    
    os.system(f'chmod 600 {kaggle_dir}/kaggle.json')
    os.system('kaggle datasets download -d mlg-ulb/creditcardfraud --unzip -p .')
    print("Dataset downloaded!")

if not os.path.exists('creditcard.csv'):
    raise FileNotFoundError("creditcard.csv not found! Check Kaggle credentials.")

df = pd.read_csv('creditcard.csv')

legit = df[df.Class == 0].sample(n=492, random_state=42)
fraud = df[df.Class == 1]
balanced = pd.concat([legit, fraud], axis=0)

X = balanced.drop('Class', axis=1)
Y = balanced['Class']

X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, stratify=Y, random_state=2
)

model = LogisticRegression(max_iter=10000, solver='lbfgs')
model.fit(X_train, Y_train)

pickle.dump(model, open('fraud_model.pkl', 'wb'))
print("Model saved as fraud_model.pkl")