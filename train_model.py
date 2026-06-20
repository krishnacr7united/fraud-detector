import pandas as pd
import numpy as np
import pickle
import warnings
warnings.filterwarnings('ignore')
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

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