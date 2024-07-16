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
        username = request.form.get('admin_username')
        password = request.form.get('admin_password')

        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            return render_template('admin_dashboard.html')
        return render_template('admin_login.html',error='Invalid credentials!')
    
    return render_template('admin_login.html', error='')


@app.route('/influencer_signup', methods=['GET', 'POST'])
def influencer_signup():
    if request.method == 'POST':
        # collecting inputs from form
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        age = request.form.get('age')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        # checking if an influencer with the same username already exists; if not, adding the influencer in the database
        user = Influencer.query.filter_by(username=username).first()
        if user:
            return render_template('influencer_registration.html', error='A user with this username already exists!')
        
        # collecting the reach(social media accounts)
        if 'instagram' in request.form:
            followers = request.form.get('instagramFollowers')
            profile_link = request.form.get('instagramProfile')
            reach = Reach(influencer_id='#', platform='Instagram', followers=followers, profile_link=profile_link)

        if 'twitter' in request.form:
            followers = request.form.get('twitterFollowers')
            profile_link = request.form.get('twitterProfile')
            reach = Reach(influencer_id='#', platform='Twitter', followers=followers, profile_link=profile_link)

        if 'youtube' in request.form:
            followers = request.form.get('youtubeFollowers')
            profile_link = request.form.get('youtubeProfile')
            reach = Reach(influencer_id='#', platform='Youtube', followers=followers, profile_link=profile_link)

        if 'linkedin' in request.form:
            followers = request.form.get('linkedinFollowers')
            profile_link = request.form.get('linkedinProfile')
            reach = Reach(influencer_id='#', platform='Linkedin', followers=followers, profile_link=profile_link)

        # collecting niche info
        niches = request.form.getlist('niches')
        for niche_name in niches:
            pass
        
        user = Influencer(first_name=first_name, last_name=last_name, age=age, email=email, username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return render_template('influencer_registration', error='')

    return render_template('influencer_registration.html', error='')


@app.route('/sponsor_signup', methods=['GET', 'POST'])
def sponsor_signup():
    if request.method == 'POST':
        # collecting inputs form form
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        industry = request.form.get('industry')
        budget = request.form.get('budget')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        type = request.form.get('type')

        # checking if a sponsor with the same username already exists; if not, adding the influencer in the database
        user = Sponsor.query.filter_by(username=username).first()
        if user:
            return render_template('sponsor_registration.html', error='A user with this username already exists!')
        
        user = Sponsor(first_name=first_name, last_name=last_name, email=email, username=username, password=password, industry=industry, budget=budget, type=type)
        db.session.add(user)
        db.session.commit()
        return render_template('sponsor_registration', error='')
    
    return render_template('sponsor_registration.html')