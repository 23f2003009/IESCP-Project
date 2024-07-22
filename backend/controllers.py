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
                                       pending_ad_requests=fetch_pending_ad_requests_for_sponsor(sponsor.id))
            else:
                return render_template('user_login', error='You have been flagged! Can\'t login.')
        
        # checking if credentials match a influencer
        influencer = Influencer.query.filter_by(username=username, password=password).first()
        if influencer:
            if not influencer.flagged:
                return render_template('influencer_dashboard.html', influencer_id=influencer.id, influencer_info=fetch_influencer_details(influencer.id),
                                       active_ads=fetch_active_ads(influencer.id), pending_ads=fetch_pending_ad_requests_for_influencer(influencer.id))
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
            return render_template('admin_dashboard.html', active_campaigns=fetch_active_campaigns(), flagged_campaigns=fetch_flagged_campaigns(), 
                                   flagged_influencers=fetch_flagged_influencers(), flagged_sponsors=fetch_flagged_sponsors())
        return render_template('admin_login.html',error='Invalid credentials!')
    
    return render_template('admin_login.html', error='')


@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    return render_template('admin_dashboard.html', active_campaigns=fetch_active_campaigns(), flagged_campaigns=fetch_flagged_campaigns(), 
                           flagged_influencers=fetch_flagged_influencers(), flagged_sponsors=fetch_flagged_sponsors())


@app.route('/admin_find', methods=['GET', 'POST'])
def admin_find():
    return render_template('admin_find.html', active_campaigns=fetch_active_campaigns(), completed_campaigns=fetch_completed_campaigns(), 
                           all_influencers=fetch_all_influencers(), all_sponsors=fetch_all_sponsors())

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
        influencer = Influencer.query.filter_by(username=username).first()
        if influencer:
            return render_template('influencer_registration.html', error='An influencer with this username already exists!')
        
        influencer = Influencer(first_name=first_name, last_name=last_name, age=age, email=email, username=username, password=password)
        db.session.add(influencer)
        db.session.commit()
        
        # retieving the reach information (social media accounts)
        influencer_id = influencer.id            # getting the ID of the newly added influencer
        social_accounts = request.form.getlist('social_accounts')
        for platform in social_accounts:
            followers = request.form.get(f'{platform}Followers')
            profile_link = request.form.get(f'{platform}Profile')
            reach = Reach(influencer_id=influencer_id, platform=platform, followers=followers, profile_link=profile_link)
            db.session.add(reach)
            db.session.commit()

        # collecting niche information
        niches = request.form.getlist('niches')
        for niche_name in niches:
            niche = Niche.query.filter_by(name=niche_name).first()
            if not niche:
                niche = Niche(name=niche_name)
                db.session.add(niche)
                db.session.commit()
                
            influencer_niche = Influencer_Niche(influencer_id=influencer_id, niche_id=niche.id)
            db.session.add(influencer_niche)
            db.session.commit()
        
        return render_template('user_login.html', error='')

    return render_template('influencer_registration.html', error='')


@app.route('/influencer_dashboard/<int:influencer_id>', methods=['GET', 'POST'])
def influencer_dashboard(influencer_id):
    influencer = Influencer.query.filter_by(id=influencer_id).first()
    return render_template('influencer_dashboard.html', influencer_id=influencer_id, influencer_info=fetch_influencer_details(influencer_id),
                        active_ads=fetch_active_ads(influencer_id), pending_ads=fetch_pending_ad_requests_for_influencer(influencer_id),
                        fname=influencer.first_name, lname=influencer.last_name)


@app.route('/influencer_find/<int:influencer_id>', methods=['GET', 'POST'])
def influencer_find(influencer_id):
    influencer = Influencer.query.filter_by(id=influencer_id).first()
    return render_template('influencer_find.html', fname=influencer.first_name, lname=influencer.last_name, influencer_id=influencer_id, all_influencers=fetch_influencer_details_for_sponsor())


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

        # checking if a sponsor with the same username already exists; if not, adding the sponsor in the database
        sponsor = Sponsor.query.filter_by(username=username).first()
        if sponsor:
            return render_template('sponsor_registration.html', error='A sponsor with this username already exists!')
        
        sponsor = Sponsor(first_name=first_name, last_name=last_name, email=email, username=username, password=password, industry=industry, budget=budget, type=type)
        db.session.add(sponsor)
        db.session.commit()
        return render_template('user_login.html', error='')
    
    return render_template('sponsor_registration.html')


@app.route('/sponsor_dashboard/<int:sponsor_id>', methods=['GET', 'POST'])
def sponsor_dashboard(sponsor_id):
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    return render_template('sponsor_dashboard.html', sponsor_id=sponsor_id, first_name=sponsor.first_name, last_name=sponsor.last_name,
                           active_campaigns=fetch_active_campaigns(sponsor_id), 
                           pending_ad_requests=fetch_pending_ad_requests_for_sponsor(sponsor_id))


@app.route('/sponsor_find/<int:sponsor_id>', methods=['GET', 'POST'])
def sponsor_find(sponsor_id):
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    return render_template('sponsor_find.html', first_name=sponsor.first_name, last_name=sponsor.last_name, sponsor_id=sponsor_id, all_influencers=fetch_influencer_details_for_sponsor())


@app.route('/campaign_details/<int:sponsor_id>/<int:camp_id>', methods=['GET', 'POST'])
def particular_campaign_details_for_sponsor(sponsor_id, camp_id):
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    return render_template('sponsor_campaign_details.html', sponsor_id=sponsor_id, campaign_info=fetch_campaign_details(camp_id),
                           first_name=sponsor.first_name, last_name=sponsor.last_name)


@app.route('/sponsor_all_campaigns/<int:sponsor_id>', methods=['GET', 'POST'])
def sponsor_all_campaigns(sponsor_id):
    sponsor = Sponsor.query.filter_by(id=sponsor_id).first()
    return render_template('sponsor_all_campaigns.html', active_campaigns=fetch_active_campaigns(sponsor_id), sponsor_id=sponsor_id, 
                           first_name=sponsor.first_name, last_name=sponsor.last_name, completed_campaigns=fetch_completed_campaigns(sponsor_id))


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
def fetch_pending_ad_requests_for_sponsor(id):
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
        
'''function for retrieving influencer details for influencer_dashboard'''
def fetch_influencer_details(influencer_id):
    influencer = Influencer.query.filter_by(id=influencer_id).first()
    influencer_info = {influencer.id: {}}
    influencer_info[influencer.id] = {'fname': influencer.first_name, 'lname': influencer.last_name, 'username': influencer.username,
                                      'email': influencer.email, 'profile_pic': influencer.profile_pic, 'earning':influencer.earning,
                                      'social_accounts':social_accounts(influencer_id)}
    return influencer_info

'''function for retrieving social accounts of an influencer'''
def social_accounts(influencer_id):
    tuples = (db.session.query(Influencer.id, Reach.platform, Reach.followers, Reach.profile_link)
                  .join(Reach, Reach.influencer_id==influencer_id).all())
    social_accounts = {}
    for tuple in tuples:
        if tuple.platform not in social_accounts.keys():
            social_accounts[tuple.platform] = {'followers': tuple.followers, 'profile_link': tuple.profile_link}
    return social_accounts

'''function for retrieving active ad_requests' details for influencer_dashboard'''
def fetch_active_ads(influencer_id):
    current_date = datetime.now().date()
    ads = (db.session.query(Ad_Request.id, Ad_Request.title.label('ad_title'), Ad_Request.payment_amount, Ad_Request.requirement,
                            Campaign.title.label('campaign_title'), Campaign.description, Campaign.goal, Campaign.start_date, Campaign.end_date,
                            Sponsor.first_name, Sponsor.last_name, Sponsor.type, Niche.name.label('niche_name'))
                            .join(Campaign, Campaign.id==Ad_Request.campaign_id)
                            .join(Sponsor, Campaign.sponsor_id==Sponsor.id)
                            .join(Niche, Ad_Request.niche_id==Niche.id)
                            .filter(Campaign.start_date <= current_date, Campaign.end_date >= current_date,
                                    Ad_Request.influencer_id==influencer_id, Campaign.flagged==False, Ad_Request.status=='accepted').all())
    active_ads = {}
    for ad in ads:
        if ad.id not in active_ads.keys():
            active_ads[ad.id] = {'ad_title':ad.ad_title, 'payment_amount': ad.payment_amount, 'ad_requirement': ad.requirement, 
                                 'campaign_title': ad.campaign_title, 'campaign_description': ad.description, 'sdate': ad.start_date, 'edate': ad.end_date,
                                 'sponsor_fname': ad.first_name, 'sponsor_lname': ad.last_name, 'sponsor_type': ad.type, 'niche': ad.niche_name}
    return active_ads

'''function for retreiving pending ad_requests for influencer_dashboard'''
def fetch_pending_ad_requests_for_influencer(influencer_id):
    current_date = datetime.now().date()
    ads = (db.session.query(Ad_Request.id, Ad_Request.title.label('ad_title'), Ad_Request.payment_amount, Ad_Request.requirement,
                            Campaign.title.label('campaign_title'), Campaign.description, Campaign.goal, Campaign.start_date, Campaign.end_date,
                            Sponsor.first_name, Sponsor.last_name, Sponsor.type, Niche.name.label('niche_name'))
                            .join(Campaign, Campaign.id==Ad_Request.campaign_id)
                            .join(Sponsor, Campaign.sponsor_id==Sponsor.id)
                            .join(Niche, Ad_Request.niche_id==Niche.id)
                            .filter(Ad_Request.influencer_id==influencer_id, Campaign.flagged==False, Ad_Request.status=='pending').all())
    pending_ads = {}
    for ad in ads:
        if ad.id not in pending_ads.keys():
            pending_ads[ad.id] = {'ad_title':ad.ad_title, 'payment_amount': ad.payment_amount, 'ad_requirement': ad.requirement, 
                                 'campaign_titile': ad.campaign_title, 'campaign_description': ad.description, 'sdate': ad.start_date, 'edate': ad.end_date,
                                 'sponsor_fname': ad.first_name, 'sponsor_lname': ad.last_name, 'sponsor_type': ad.type, 'niche': ad.niche_name}
    return pending_ads

'''function for retreiving the ad requests of all public campaigns and those private campaigns that have matching niche with influencer and are active'''
def fetch_all_ads():
    pass

'''function for retreiving all public active campaigns'''