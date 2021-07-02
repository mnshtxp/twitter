from flask import Blueprint, render_template, jsonify
from twitter.models import Users, parse_records

main_routes = Blueprint('main_routes', __name__)

# '/' : homepage
@main_routes.route('/')
def index():
    return render_template("index.html")


# '/user.json' : view jason file
@main_routes.route('/user.json/')
def json_data():
    raw_data = Users.query.all()
    parsed_data = parse_records(raw_data)
    
    return jsonify(parsed_data)


# '/users/' : see all the users
@main_routes.route('/users/')
def users():
    data = Users.query.all()
    return render_template("user.html", data = data)