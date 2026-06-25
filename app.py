from flask import Flask, request, render_template, redirect, url_for, session
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'frauddetector2026'

model = pickle.load(open('fraud_model.pkl', 'rb'))
df = pd.read_csv('creditcard.csv')
feature_means = df.drop('Class', axis=1).mean()

USERS = {
    'RAHUL': {'password': 'RAHUL', 'name': 'RAHUL KUMAR', 'card': '**** **** **** 4291', 'balance': 5420.75}
}

merchants = ['Amazon', 'Walmart', 'Netflix', 'Uber', 'Starbucks', 'Apple Store', 'Steam', 'Zomato', 'Flipkart', 'PayPal']

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username]['password'] == password:
            session['user'] = username
            session['history'] = [
    {'merchant': 'Amazon', 'amount': 149.62, 'time': 406, 'prediction': 0, 'confidence': 94.5, 'risk_score': 5.5, 'timestamp': '20 Jun 2026, 09:15 AM', 'reasons': ['Transaction amount is within normal range', 'Merchant is verified and trusted', 'No suspicious patterns detected', 'Transaction time matches your usual activity']},
    {'merchant': 'Steam', 'amount': 892.00, 'time': 1200, 'prediction': 1, 'confidence': 91.2, 'risk_score': 88.3, 'timestamp': '20 Jun 2026, 10:02 AM', 'reasons': ['Unusual transaction amount for this account', 'Transaction pattern does not match your history', 'High-risk merchant category detected', 'Suspicious transaction time detected']},
    {'merchant': 'Starbucks', 'amount': 12.50, 'time': 3600, 'prediction': 0, 'confidence': 97.1, 'risk_score': 2.9, 'timestamp': '20 Jun 2026, 10:45 AM', 'reasons': ['Transaction amount is within normal range', 'Merchant is verified and trusted', 'No suspicious patterns detected', 'Transaction time matches your usual activity']},
    {'merchant': 'PayPal', 'amount': 2300.00, 'time': 500, 'prediction': 1, 'confidence': 88.7, 'risk_score': 91.2, 'timestamp': '20 Jun 2026, 11:00 AM', 'reasons': ['Unusual transaction amount for this account', 'Suspicious transaction time detected', 'High-risk merchant category detected', 'Transaction pattern does not match your history']},
    {'merchant': 'Uber', 'amount': 23.75, 'time': 7200, 'prediction': 0, 'confidence': 95.3, 'risk_score': 4.7, 'timestamp': '20 Jun 2026, 11:30 AM', 'reasons': ['Transaction amount is within normal range', 'Merchant is verified and trusted', 'No suspicious patterns detected', 'Transaction time matches your usual activity']},
]
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = USERS[session['user']]
    result = None
    success = False
    if request.method == 'POST':
        amount = float(request.form['amount'])
        recipient = request.form['recipient']
        merchant = request.form['merchant']
        time_val = float(request.form.get('time', 3600))

        features = feature_means.copy()
        features['Amount'] = amount
        features['Time'] = time_val

        input_array = np.array([features.values])
        prediction = model.predict(input_array)[0]
        probability = model.predict_proba(input_array)[0]
        confidence = round(max(probability) * 100, 2)
        risk_score = round(probability[1] * 100, 2)

        if prediction == 1:
            reasons = [
                'Transaction amount is unusually high for this account',
                'This merchant has been flagged in suspicious activity patterns',
                'Transaction time does not match your usual activity hours',
                'Rapid sequential transactions detected — possible card skimming',
            ]
        else:
            reasons = ['Transaction amount is within normal range',
                       'Merchant is verified and trusted',
                       'Transaction time matches your usual activity',
                       'No suspicious patterns detected']

        if request.form.get('confirmed') == 'yes':
            history = session.get('history', [])
            history.insert(0, {
                'merchant': merchant,
                'amount': amount,
                'time': time_val,
                'prediction': int(prediction),
                'confidence': confidence,
                'risk_score': risk_score,
                'timestamp': datetime.now().strftime('%d %b %Y, %I:%M %p'),
                'reasons': reasons,
                'recipient': recipient,
                'status': 'Proceeded by user' if prediction == 1 else 'Completed'
            })
            session['history'] = history
            session.modified = True
            return render_template('payment.html', user=user,
                                   success=True, amount=amount,
                                   recipient=recipient, merchant=merchant,
                                   was_fraud=int(prediction), result=None)

        result = {
            'prediction': int(prediction),
            'confidence': confidence,
            'risk_score': risk_score,
            'amount': amount,
            'recipient': recipient,
            'merchant': merchant,
            'time': time_val,
            'reasons': reasons,
            'timestamp': datetime.now().strftime('%d %b %Y, %I:%M %p'),
        }

        if prediction == 0:
            history = session.get('history', [])
            history.insert(0, {**result, 'status': 'Completed'})
            session['history'] = history
            session.modified = True

    return render_template('payment.html', user=user, result=result, success=success)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = USERS[session['user']]
    history = session.get('history', [])
    total = len(history)
    fraud_count = sum(1 for t in history if t['prediction'] == 1)
    legit_count = total - fraud_count
    return render_template('dashboard.html', user=user, total=total, fraud_count=fraud_count, legit_count=legit_count, history=history[:5])

@app.route('/check', methods=['GET', 'POST'])
def check():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = USERS[session['user']]
    result = None
    if request.method == 'POST':
        amount = float(request.form['amount'])
        time_val = float(request.form['time'])
        merchant = request.form['merchant']

        features = feature_means.copy()
        features['Amount'] = amount
        features['Time'] = time_val

        input_array = np.array([features.values])
        prediction = model.predict(input_array)[0]
        probability = model.predict_proba(input_array)[0]
        confidence = round(max(probability) * 100, 2)
        risk_score = round(probability[1] * 100, 2)

        if prediction == 1:
            reasons = [
                'Unusual transaction amount for this account',
                'Transaction pattern does not match your history',
                'High-risk merchant category detected',
                'Suspicious transaction time detected'
            ]
        else:
            reasons = [
                'Transaction amount is within normal range',
                'Merchant is verified and trusted',
                'Transaction time matches your usual activity',
                'No suspicious patterns detected'
            ]

        result = {
            'prediction': int(prediction),
            'confidence': confidence,
            'risk_score': risk_score,
            'amount': amount,
            'time': time_val,
            'merchant': merchant,
            'reasons': reasons,
            'timestamp': datetime.now().strftime('%d %b %Y, %I:%M %p')
        }

        history = session.get('history', [])
        history.insert(0, result)
        session['history'] = history
        session.modified = True

    return render_template('check.html', user=user, result=result, merchants=merchants)

@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = USERS[session['user']]
    history = session.get('history', [])
    return render_template('history.html', user=user, history=history)

if __name__ == '__main__':
    app.run(debug=True)