from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Sponsor(db.Model):
    __tablename__ = 'sponsor'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    industry = db.Column(db.String, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    type = db.Column(db.Enum('Company', 'Individual'), nullable=False)
    flagged = db.Column(db.Boolean, deafult=False)

class Influencer(db.Model):
    __tablename__ = 'influencer'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    age = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    earning = db.Column(db.Integer, default=0)
    profile_pic = db.Column(db.String)
    flagged = db.Column(db.Boolean, deafult=False)

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

class Reach(db.Model):
    __tablename__ = 'reach'
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    platform = db.Column(db.Enum('Instagram', 'Twitter', 'Youtube', 'Linkedin'), nullable=False)
    followers = db.Column(db.Integer, nullable=False)
    profile_link = db.Column(db.String, nullable=False)

class Niche(db.Model):
    __tablename__ = 'niche'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

class Influencer_Niche(db.Model):
    __tablename__ = 'influencer_niche'
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), primary_key=True, nullable=False)
    niche_id = db.Column(db.Integer, db.ForeignKey('niche.id'), primary_key=True, nullable=False)

class Campaign(db.Model):
    __tablename__ = 'campaign'
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    visibility = db.Column(db.Enum('Private', 'Public'), default='Public', nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    goal = db.Column(db.String)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    flagged = db.Column(db.Boolean, deafult=False)

class Ad_Request(db.Model):
    __tablename__ = 'ad_request'
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    status = db.Column(db.Enum('Pending', 'Accepted', 'Rejected'), default='Pending')
    payment_amount = db.Column(db.Float, nullable=False)
    requirement = db.Column(db.String, nullable=False)
    niche_id = db.Column(db.Integer, db.ForeignKey('niche.id'), nullable=False)
    niche = db.relationship('Niche', backref='ads')