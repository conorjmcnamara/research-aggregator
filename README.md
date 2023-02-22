# NLP Research Aggregator

from flask import Flask, make_response, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, jwt_required,
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies, get_jwt_identity
)
from cache import LRUCache
from utils import users_db, papers_db, topics
import datetime
import hashlib

# configuration
app = Flask(__name__)
lru_cache = LRUCache(10)
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = "7f377d4f0562a66c09c7e79697288133"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
#app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

# enable cookie-based authentication sent over HTTPS only
app.config["JWT_TOKEN_LOCATION"] = "cookies"
app.config["JWT_COOKIE_SECURE"] = True
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
# app.config['JWT_CSRF_CHECK_FORM'] = True

# signup
@app.route("/api/signup", methods=["POST"])
def signup():
    user = request.get_json()
    user["password"] = hashlib.sha256(user["password"].encode("utf-8")).hexdigest()
    doc = users_db.find_one({"email": user["email"]})
    
    # check if the user exists in the database
    if not doc:
        users_db.insert_one(user)
        return jsonify({"signup": "successful"}), 201
    return jsonify({"signup": "unsuccessful"}), 409

# login
@app.route("/api/login", methods=["POST"])
def login():
    credentials = request.get_json()
    user = users_db.find_one({"email": credentials["email"]})
    
    # check if the user exists in the database
    if user:
        encrypted_password = hashlib.sha256(credentials["password"].encode("utf-8")).hexdigest()
        if encrypted_password == user["password"]:
            # create tokens to send back to the user
            access_token = create_access_token(identity=user["email"])
            refresh_token = create_refresh_token(identity=user["email"])

            # use double submit protection cookies to avoid CSRF attacks
            response = jsonify({"login": "successful"})
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response, 200
    return jsonify({"login": "user not found"}), 401

# logout
@app.route("/api/logout", methods=["POST"])
def logout():
    response = jsonify({"logout": "successful"})
    unset_jwt_cookies(response)
    return response, 200

# secured bookmarks endpoint
@app.route("/api/bookmarks", methods=["GET"])
@jwt_required()
def bookmarks():
    credentials = get_jwt_identity()
    user = users_db.find_one({"email": credentials})
    return jsonify({"email": user["email"]}), 200

# refresh JWT token if a request returned to frontend as 401 due to expired
# a new request is made to refresh
@app.route("/api/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    # create a new access token
    user = get_jwt_identity()
    access_token = create_access_token(identity=user)
    response = jsonify({"refresh": "successful"})
    set_access_cookies(response, access_token)
    return response, 200

@app.route("/api/topic/<string:id>", methods=["GET"])
def topic_query(id: str):
    # check for a valid topic ID
    if id not in topics:
        return make_response({"invalid topic ID: ": id}, 404)

    # cache hit
    if lru_cache.get(id):
        return make_response(lru_cache.get(id), 200)
    # cache miss
    response = papers_db.find({"topic": id}).limit(10)
    topic_data = []

    for paper in response:
        # remove the database document ID
        paper.pop("_id", None)
        topic_data.append(paper)
    lru_cache.put(id, topic_data)
    return make_response(topic_data, 200)

@app.route("/api/search/<string:query>", methods=["GET"])
def search_query(query: str):
    # search for research papers with the passed query
    pipeline = [{
        "$search": {
            "index": "papers_index",
            "text": {
                "query": query,
                "path": ["title", "abstract"]
            }
        }
    }, {"$limit": 10}]

    if pipeline:
        search_data = []
        for paper in papers_db.aggregate(pipeline):
            paper.pop("_id", None)
            search_data.append(paper)
        return make_response(search_data, 200)
    return make_response({"failed to make a search query with:": query}, 404)

if __name__ == "__main__":
    app.run(debug=False)