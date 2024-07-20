from flask import Flask, render_template, request
from flask import current_app as app
from .models import *


# ---------------------------------------------------------- ROUTES ---------------------------------------------------------- #
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
            if not sponsor.flagged:
                return render_template('sponsor_dashboard.html')
            else:
                return render_template('user_login', error='You have been flagged! Can\'t login.')
        
        # checking if credentials match a influencer
        influencer = Influencer.query.filter_by(username=username, password=password).first()
        if influencer:
            if not influencer.flagged:
                return render_template('influencer_dashboard.html')
            else:
                return render_template('user_login.html', error='You have been flagged! Can\'t login.')
        
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
            return render_template('admin_dashboard.html', active_campaigns=fetch_active_campaigns(), flagged_campaigns=fetch_flagged_campaigns(), flagged_influencers=fetch_flagged_influencers(), flagged_sponsors=fetch_flagged_sponsors())
        return render_template('admin_login.html',error='Invalid credentials!')
    
    return render_template('admin_login.html', error='')


@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    return render_template('admin_dashboard.html', active_campaigns=fetch_active_campaigns(), flagged_campaigns=fetch_flagged_campaigns(), flagged_influencers=fetch_flagged_influencers(), flagged_sponsors=fetch_flagged_sponsors())


@app.route('/admin_find', methods=['GET', 'POST'])
def admin_find():
    return render_template('admin_find.html', all_campaigns=fetch_all_campaigns(), all_influencers=fetch_all_influencers(), all_sponsors=fetch_all_sponsors())


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
        return render_template('influencer_login.html', error='')

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
        return render_template('sponsor_login.html', error='')
    
    return render_template('sponsor_registration.html')

# more routes


# ---------------------------------------------------------- USER DEFINED FUNCTIONS ---------------------------------------------------------- #

'''function for retrieving all active campaigns for admin dashboard'''
def fetch_active_campaigns():
    # Query to find all campaigns that have at least one accepted ad as those are the active campaigns
    campaigns = db.session.query(Campaign).join(Ad_Request).filter(Ad_Request.status == 'Accepted').distinct().all()
    active_campaigns = {}
    for campaign in campaigns:
        if campaign.id not in active_campaigns.keys():
            active_campaigns[campaign.id] = [campaign.title, campaign.description]
    return active_campaigns

'''function for retrieving all flagged campaigns for admin dashboard'''
def fetch_flagged_campaigns():
    campaigns = Campaign.query.filter_by(flagged=True).all()
    flagged_campaigns = {}
    for campaign in campaigns:
        if campaign.id not in flagged_campaigns.keys():
            flagged_campaigns[campaign.id] = [campaign.title, campaign.description]
    return flagged_campaigns

'''function for retrieving all flagged influencers for admin dashboard'''
def fetch_flagged_influencers():
    influencers = Influencer.query.filter_by(flagged=True).all()
    flagged_influencers = {}
    for influencer in influencers:
        if influencer.id not in flagged_influencers.keys():
            flagged_influencers[influencer.id] = [influencer.first_name, influencer.last_name, influencer.username]
    return flagged_influencers

'''function for retrieving all flagged sponsors for admin dashboard'''
def fetch_flagged_sponsors():
    sponsors = Sponsor.query.filter_by(flagged=True).all()
    flagged_sponsors = {}
    for sponsor in sponsors:
        if sponsor.id not in flagged_sponsors.keys():
            flagged_sponsors[sponsor.id] = [sponsor.first_name, sponsor.last_name, sponsor.username]
    return flagged_sponsors

'''function for retrieving all (unflagged) campaigns' data for admin find page'''
def fetch_all_campaigns():
    campaigns = Campaign.query.filter_by(flagged=False).all()
    all_campaigns = {}
    for campaign in campaigns:
        if campaign.id not in all_campaigns.keys():
            all_campaigns[campaign.id] = [campaign.title, campaign.description]
    return all_campaigns

'''function for retrieving all (unflagged) influencers' data for admin find page'''
def fetch_all_influencers():
    influencers = Influencer.query.filter_by(flagged=False).all()
    all_influencers = {}
    for influencer in influencers:
        if influencer.id not in all_influencers.keys():
            all_influencers[influencer.id] = [influencer.first_name, influencer.last_name, influencer.username]
    return all_influencers

'''function for retrieving all (unflagged) sponsors' data for admin find page'''
def fetch_all_sponsors():
    sponsors = Sponsor.query.filter_by(flagged=False).all()
    all_sponsors = {}
    for sponsor in sponsors:
        if sponsor.id not in all_sponsors.keys():
            all_sponsors[sponsor.id] = [sponsor.first_name, sponsor.last_name, sponsor.username]
    return all_sponsors