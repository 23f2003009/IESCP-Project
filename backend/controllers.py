from flask import Flask, render_template, request
from flask import current_app as app
from .models import *

@app.route('/')
def home():
    return render_template('welcome_page.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        # checking if credentials match a sponsor
        sponsor = Sponsor.query.filter_by(username=username, password=password).first()
        if sponsor:
            return render_template('/templates/sponsor_dashboard.html')
        
        # checking if credentials match a influencer
        influencer = Influencer.query.filter_by(username=username, password=password).first()
        if influencer:
            return render_template('/templates/influencer_dashboard.html')
        
        # credentials do not match, show error msg and redirect to login
        return render_template('user_login.html', error="Invalid credentials!")
    
    return render_template('user_login.html', error='')


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin = Admin.query.filter_by(username=username, password=password)
        if admin:
            return render_template('admin_dashboard.html')
        return render_template('admin_dashboard.html',error='Invalid credentials!')
    return render_template('admin_login.html')

@app.route('/influencer_signup', methods=['GET', 'POST'])
def influencer_signup():
    return render_template('influencer_registration.html', error='')

@app.route('/sponsor_signup', methods=['GET', 'POST'])
def sponsor_signup():
    return render_template('sponsor_registration.html')