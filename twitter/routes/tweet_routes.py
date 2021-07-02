import numpy as np
import pickle
import os
from flask import Blueprint, render_template, request
from twitter.models import db, Users, Tweet
from twitter.services.twitter_api import api
from embedding_as_service_client import EmbeddingClient
from sklearn.linear_model import LogisticRegression


# Model File
FILEPATH = './model.pkl'


# Encoding Server
en = EmbeddingClient(host = '54.180.124.154', port = 8989)
tweet_routes = Blueprint('tweet_routes', __name__)


# GET : Add Users
@tweet_routes.route('/<username>/add')
def add(username=None):
	username = username

	# Tweepy 정보 가져오기
	new = api.get_user(screen_name = username)
	tweets = api.user_timeline(screen_name = username, tweet_mode ="extend")
	tmp = [{'text':tweet.text, 'user_id':tweet.user.id} for tweet in tweets]


	# Insert into Users table
	user = Users.query.get(new.id) or Users(id = new.id)
	user.username = new.screen_name.casefold()
	user.full_name = new.name
	user.followers = new.followers_count

	db.session.add(user)

	# Insert into Tweet table
	for data in tweets:
		tweet = Tweet.query.get(data.id) or Tweet(id = data.id)
		tweet.text = data.text
		tweet.embedding = en.encode(texts = [data.text])
		tweet.user_id = data.user.id
		db.session.add(tweet)

	
	db.session.commit()

	return render_template('add.html', data = new)


# 'GET' : Pritn Tweets
@tweet_routes.route('/<username>/get/')
def get(username = None):
    username = username
    id = Users.query.with_entities(Users.id).filter(Users.username == username).first()
    print(id)
    data = Tweet.query.filter(Tweet.user_id == id[0]).all()
    for tweet in data:
        print(tweet.text)
    return render_template("get.html", data = data)


# 'GET' : Delete Users
@tweet_routes.route('/<username>/delete/')
def delete(username = None):
	username = username
	id = Users.query.with_entities(Users.id).filter(Users.username == username).first()
	print(id)
	Tweet.query.filter_by(user_id = id[0]).delete() 
	Users.query.filter_by(id = id[0]).delete() 

	db.session.commit()
	
	return render_template("delete.html")


# Update names of the users
@tweet_routes.route('/update/', methods=["GET", "POST"])
def update():
	if request.method == "POST":
		print(dict(request.form))
		result = request.form
		if result['name_type'] == '1':
			db.session.query(Users).filter(Users.username == result['username']).update({'username': result['change_name']})
			db.session.commit()
		elif result['name_type'] == '2':
			db.session.query(Users).filter(Users.username == result['username']).update({'full_name': result['change_name']})
			db.session.commit()
	
	return render_template('update.html')


# Predict the user by the tweet
@tweet_routes.route('/compare/', methods=["GET", "POST"])
def compare():
	users = Users.query.all()
	text = []
	id = []
	prediction = 0
	if request.method == "POST":
		print(dict(request.form))
		result = request.form

		# import all datas from the table
		for user in users:
			tweets = Tweet.query.with_entities(Tweet.embedding).filter(Tweet.user_id == user.id).all()
			for tweet in tweets:
				append_to_with_label(text, tweet, id, user.id)
			
		# 3D array to 2D array
		text_array = np.array(text)
		nsamples, nx, ny = text_array.shape
		text_2d = text_array.reshape(nsamples, nx * ny)

		# Model import
		if os.path.isfile(FILEPATH):
			model = pickle.load(open('model.pkl', 'rb'))
			pred_id = model.predict(en.encode(texts = [result['text']]))
			prediction = int(pred_id[0])

		else:
			model = LogisticRegression(warm_start=True)
			model.fit(text_2d, id)
			pred_id = model.predict(en.encode(texts = [result['text']]))
			prediction = int(pred_id[0])
			pickle.dump(model, open('model.pkl', 'wb'))
		
	# Predction result
	pred_res = Users.query.filter(Users.id == prediction).first()


	return render_template('compare.html', data = pred_res)


# Add users with a page.
@tweet_routes.route('/addusers/', methods=["GET", "POST"])
def addusers():
	if request.method == "POST":
		print(dict(request.form))
		result = request.form
		# breakpoint()
		new = api.get_user(screen_name = result['username'])
		tweets = api.user_timeline(screen_name = result['username'], tweet_mode ="extend")
		tmp = [{'text':tweet.text, 'user_id':tweet.user.id} for tweet in tweets]

		# Insert into Users
		user = Users.query.get(new.id) or Users(id = new.id)
		user.username = new.screen_name.casefold()
		user.full_name = new.name
		user.followers = new.followers_count

		db.session.add(user)

		# Insert into Tweets
		for data in tweets:
			tweet = Tweet.query.get(data.id) or Tweet(id = data.id)
			tweet.text = data.text
			tweet.embedding = en.encode(texts = [data.text])
			tweet.user_id = data.user.id
			db.session.add(tweet)

			## 2nd 방법
			# db.session.add(Tweet(
			# 	text = tweet.text,
			# 	user_id = tweet.user.id
			# ))
		
		db.session.commit()

		# Pre-trained model
		text = []
		id = []
		users = Users.query.all()
		for user in users:
			tweets = Tweet.query.with_entities(Tweet.embedding).filter(Tweet.user_id == user.id).all()
			for tweet in tweets:
				append_to_with_label(text, tweet, id, user.id)
			
		# 3D to 2D dimension
		text_array = np.array(text)

		nsamples, nx, ny = text_array.shape

		text_2d = text_array.reshape(nsamples, nx * ny)

		# model import
		model = pickle.load(open('model.pkl', 'rb'))

		try:
			model.fit(text_2d, id)
		except:
			print('At least you have two users in your dataset')

		# updated model and save
		pickle.dump(model, open('model.pkl', 'wb'))
		print("model updated")


	return render_template('addusers.html')


# View tweets page
@tweet_routes.route('/gettweets/', methods=["GET", "POST"])
def gettweets():
	tweets = []
	if request.method == "POST":
		print(dict(request.form))
		result = request.form

		id = Users.query.with_entities(Users.id).filter(Users.username == result['username']).first()
		print(id)
		data = Tweet.query.filter(Tweet.user_id == id[0]).all()
		for tweet in data:
    			tweets.append(tweet.text)
	
	return render_template("gettweets.html", data = tweets)

def append_to_with_label(to_arr, from_arr, label_arr, label):
    """
    from_arr 리스트에 있는 항목들을 to_arr 리스트에 append하고
    레이블도 같이 추가해주는 함수
    """

    for item in from_arr:
        to_arr.append(item)
        label_arr.append(label)