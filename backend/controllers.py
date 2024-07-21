from flask import Flask, render_template, request
from flask import current_app as app
from .models import *
from datetime import datetime

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
                return render_template('sponsor_dashboard.html', first_name=sponsor.first_name, last_name=sponsor.last_name, 
                                       sponsor_id=sponsor.id,
                                       active_campaigns=fetch_active_campaigns(sponsor.id), 
                                       pending_ad_requests=fetch_pending_ad_requests(sponsor.id))
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
    return render_template('admin_find.html', active_campaigns=fetch_active_campaigns(), completed_campaigns=fetch_completed_campaigns(), all_influencers=fetch_all_influencers(), all_sponsors=fetch_all_sponsors())

@app.route('/campaign_details/<int:camp_id>', methods=['GET', 'POST'])
def particular_campaign_details(camp_id):
    return render_template('admin_campaign_details.html', campaign_info=fetch_campaign_details(camp_id))


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


@app.route('/sponsor_dashboard/<int:sponsor_id>', methods=['GET', 'POST'])
def sponsor_dashboard(sponsor_id):
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    return render_template('sponsor_dashboard.html', first_name=sponsor.first_name, last_name=sponsor.last_name, sponsor_id=sponsor_id,
                           active_campaigns=fetch_active_campaigns(sponsor_id), 
                           pending_ad_requests=fetch_pending_ad_requests(sponsor_id))


@app.route('/sponsor_find/<int:sponsor_id>', methods=['GET', 'POST'])
def sponsor_find(sponsor_id):
    sponsor = Sponsor.query.filter_by(id=sponsor_id)
    return render_template('sponsor_find.html', first_name=sponsor.first_name, last_name=sponsor.last_name, sponsor_id=sponsor_id, all_influencers=fetch_influencer_details_for_sponsor())


@app.route('/campaign_details/<int:sponsor_id>/<int:camp_id>', methods=['GET', 'POST'])
def particular_campaign_details(sponsor_id, camp_id):
    return render_template('sponsor_campaign_details.html', sponsor_id=sponsor_id, campaign_info=fetch_campaign_details(camp_id))


@app.route('/sponsor_all_campaigns/<int:sponsor_id>', methods=['GET', 'POST'])
def sponsor_all_campaigns(sponsor_id):
    return render_template('sponsor_all_campaigns.html', active_campaigns=fetch_active_campaigns(sponsor_id), 
                           sponsor_id=sponsor_id, completed_campaigns=fetch_completed_campaigns(sponsor_id))


# more routes


# ---------------------------------------------------------- USER DEFINED FUNCTIONS ---------------------------------------------------------- #

'''function for retrieving all (unflagged) active campaigns'''
def fetch_active_campaigns(sponsor_id=None):
    current_date = datetime.now().date()

    if sponsor_id:
        # Logic for fetching active campaigns for a specific sponsor
        campaigns = (db.session.query(Campaign)
                    .filter(Campaign.start_date <= current_date, Campaign.end_date >= current_date, 
                            Campaign.sponsor_id==sponsor_id, Campaign.flagged==False).all())
    else:
        # Logic for fetching active campaigns for admin
        campaigns = (db.session.query(Campaign)
                    .filter(Campaign.start_date <= current_date, Campaign.end_date >= current_date, Campaign.flagged==False)
                    .all())
        
    active_campaigns = {}
    for campaign in campaigns:
        if campaign.id not in active_campaigns.keys():
            active_campaigns[campaign.id] = {'title': campaign.title, 'description': campaign.description,'goal': campaign.goal,
                                            'start_date': campaign.start_date, 'end_date': campaign.end_date}
    return active_campaigns

'''function for retrieving all flagged campaigns for admin dashboard'''
def fetch_flagged_campaigns():
    campaigns = Campaign.query.filter_by(flagged=True).all()
    flagged_campaigns = {}
    for campaign in campaigns:
        if campaign.id not in flagged_campaigns.keys():
            flagged_campaigns[campaign.id] = {'title': campaign.title, 'description': campaign.description}
    return flagged_campaigns

'''function for retrieving all flagged influencers for admin dashboard'''
def fetch_flagged_influencers():
    influencers = Influencer.query.filter_by(flagged=True).all()
    flagged_influencers = {}
    for influencer in influencers:
        if influencer.id not in flagged_influencers.keys():
            flagged_influencers[influencer.id] = {'fname': influencer.first_name, 'lname': influencer.last_name, 'username': influencer.username}
    return flagged_influencers

'''function for retrieving all flagged sponsors for admin dashboard'''
def fetch_flagged_sponsors():
    sponsors = Sponsor.query.filter_by(flagged=True).all()
    flagged_sponsors = {}
    for sponsor in sponsors:
        if sponsor.id not in flagged_sponsors.keys():
            flagged_sponsors[sponsor.id] = {'fname': sponsor.first_name, 'lname': sponsor.last_name, 'username': sponsor.username}
    return flagged_sponsors

'''function for retrieving all (unflagged) influencers' data for admin find page'''
def fetch_all_influencers():
    influencers = Influencer.query.filter_by(flagged=False).all()
    all_influencers = {}
    for influencer in influencers:
        if influencer.id not in all_influencers.keys():
            all_influencers[influencer.id] = {'fname': influencer.first_name, 'lname': influencer.last_name, 'username': influencer.username}
    return all_influencers

'''function for retrieving all (unflagged) sponsors' data for admin find page'''
def fetch_all_sponsors():
    sponsors = Sponsor.query.filter_by(flagged=False).all()
    all_sponsors = {}
    for sponsor in sponsors:
        if sponsor.id not in all_sponsors.keys():
            all_sponsors[sponsor.id] = {'fname': sponsor.first_name, 'lname': sponsor.last_name, 'username': sponsor.username}
    return all_sponsors

'''function for retrieving all completed campaigns for sponsor_all_campaigns page and admin_find page'''
def fetch_completed_campaigns(sponsor_id=None):
    current_date = datetime.now().date()

    if sponsor_id:
        # Logic for finding out completed campaigns for a particular sponsor
        campaigns = (db.session.query(Campaign)
                .filter(Campaign.end_date < current_date, Campaign.sponsor_id==sponsor_id).all())
    else:
        # Logic for finding out all completed campaigns for admin
        campaigns = (db.session.query(Campaign)
                .filter(Campaign.end_date < current_date).all())

    completed_campaigns = {}
    for campaign in campaigns:
        if campaign.id not in completed_campaigns.keys():
            completed_campaigns[campaign.id] = {'title': campaign.title, 'description': campaign.description, 'goal': campaign.goal, 'budget': campaign.budget}
    return completed_campaigns

'''function for retrieving pending ad requests for sponsor dashboard'''
def fetch_pending_ad_requests(id):
    ad_requests = (db.session.query(
                   Ad_Request.id, Ad_Request.title.label('ad_title'),
                   Campaign.title.label('campaign_title'),
                   Influencer.first_name, Influencer.last_name)
                   .join(Campaign, Ad_Request.campaign_id==Campaign.id)
                   .join(Influencer, Ad_Request.influencer_id==Influencer.id)
                   .filter(Campaign.sponsor_id==id, Ad_Request.status=='pending').all())
    pending_ad_requests = {}
    for ad in ad_requests:
        if ad.id not in pending_ad_requests.keys():
            pending_ad_requests[ad.id] = {'ad_title':ad.ad_title, 'campaign_title':ad.campaign_title, 
                                          'influencer_fname': ad.first_name, 'influencer_lname': ad.last_name}
    return pending_ad_requests

'''function for retrieving all (unflagged) influencer details for sponsor find page'''
def fetch_influencer_details_for_sponsor():
    influencers = (db.session.query(Influencer.id, Influencer.first_name, Influencer.last_name,
                                   Niche.name.label('niche_name'),
                                   Reach.platform, Reach.profile_link, Reach.followers)
                                   .join(Influencer_Niche, Influencer_Niche.influencer_id==Influencer.id)
                                   .join(Niche, Niche.id==Influencer_Niche.niche_id)
                                   .join(Reach, Reach.influencer_id==Influencer.id)
                                   .filter(Influencer.flagged==False).all())
    all_influencers = {}
    for influencer in influencers:
        if influencer.id not in all_influencers.keys():
            all_influencers[influencer.id] = {'fname': influencer.first_name, 'lname': influencer.last_name, 
                                              'social_accounts': {}, 'niches': []}
        
        if influencer.niche_name not in all_influencers[influencer.id]['niches']:
            all_influencers[influencer.id]['niches'].append(influencer.niche_name)

        if influencer.platform not in all_influencers[influencer.id]['social_accounts'].keys():
            all_influencers[influencer.id]['social_accounts'][influencer.platform] = {'followers': influencer.followers, 'url': influencer.profile_link}
    return all_influencers

'''function for retrieving the details of a particular campaign and its associated ad_requests for sponsor_campaign_details and admin_campaign_details page'''
def fetch_campaign_details(camp_id):
    campaigns = (db.session.query(Campaign.id.label('campaign_id'), Campaign.title.label('campaign_title'), Campaign.description, Campaign.flagged,
                                Campaign.start_date, Campaign.end_date, Campaign.visibility, Campaign.budget, Campaign.goal,
                                Ad_Request.id.label('ad_id'), Ad_Request.title.label('ad_title'), Ad_Request.requirement,
                                Ad_Request.payment_amount, Ad_Request.status,
                                Niche.name.label('niche_name'),
                                Influencer.first_name, Influencer.last_name)
                                .join(Ad_Request, Ad_Request.campaign_id==Campaign.id)
                                .join(Niche, Niche.id==Ad_Request.niche_id)
                                .join(Influencer, Influencer.id==Ad_Request.influencer_id)
                                .filter(Campaign.id==camp_id).all())
    campaign_info = {}
    for campaign in campaigns:
        if campaign.flagged:
            return None
        
        else:
            if campaign.id not in campaign_info.keys():
                campaign_info[campaign.id] = {'title':campaign.campaign_title, 'description': campaign.description, 'goal': campaign.goal, 'start_date': campaign.start_date, 
                                            'end_date': campaign.end_date,'visibility': campaign.visibility, 'budget': campaign.budget, 'ads': {}}
            
            if campaign.ad_id not in campaign_info[campaign.id]['ads'].keys():
                campaign_info[campaign.id]['ads'][campaign.ad_id] = {'title': campaign.ad_title, 'requirements': campaign.requirement, 
                                                                'payment_amount': campaign.payment_amount, 'influencer_fname': campaign.first_name, 
                                                                'influencer_lname': campaign.last_name, 'status': campaign.status, 'niche': campaign.niche_name}
            return campaign_info