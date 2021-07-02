from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from twitter.services.twitter_api import api


db = SQLAlchemy()
migrate = Migrate()

# 파이썬에서 DB TABLE 만들기
# User
class Users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String)
    full_name = db.Column(db.String)
    followers = db.Column(db.Integer)

    def __repr__(self):
        return "< User {} {} >".format(self.id, self.username)

# Tweet
class Tweet(db.Model):
    __tablename__ = 'Tweet'
    id = db.Column(db.BigInteger, primary_key=True)
    text = db.Column(db.String(1000000))
    embedding = db.Column(db.PickleType)
    user_id = db.Column(db.BigInteger, db.ForeignKey("Users.id"))

    user=db.relationship("Users", foreign_keys=user_id)

    def __repr__(self):
        return "< Tweet {} >".format(self.id)

    

def parse_records(db_records):
    parsed_list = []
    for record in db_records:
        parsed_record = record.__dict__
        print(parsed_record)
        del parsed_record["_sa_instance_state"]
        parsed_list.append(parsed_record)
    return parsed_list
