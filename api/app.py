import datetime
import hashlib
import os
from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt,
    set_access_cookies, unset_jwt_cookies, get_jwt_identity
)
from dotenv import load_dotenv
from utils import get_db_connection, LRUCache, topics

# configuration
app = Flask(__name__)
jwt = JWTManager(app)
lru_cache = LRUCache(10)

load_dotenv()
user = os.getenv("USER")
password = os.getenv("PASSWORD")
papers_db = get_db_connection(user, password, "papers")
users_db = get_db_connection(user, password, "users")

# JWT cookie-based authentication
app.config["JWT_SECRET_KEY"] = os.getenv("JWT")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)
app.config["JWT_TOKEN_LOCATION"] = "cookies"
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_COOKIE_CSRF_PROTECT"] = True

@app.route("/api/signup", methods=["POST"])
def signup():
    user = request.get_json()
    user["password"] = hashlib.sha256(user["password"].encode("utf-8")).hexdigest()
    exists = users_db.find_one({"email": user["email"]})
    
    # check if the user exists in the database
    if not exists:
        users_db.insert_one(user)
        return jsonify({"signup": "successful"}), 201
    return jsonify({"signup": "unsuccessful"}), 409

@app.route("/api/login", methods=["POST"])
def login():
    credentials = request.get_json()
    user = users_db.find_one({"email": credentials["email"]})
    
    # check if the user exists in the database
    if user:
        encrypted_password = hashlib.sha256(credentials["password"].encode("utf-8")).hexdigest()
        if encrypted_password == user["password"]:
            # create double submit protection cookies to avoid CSRF attacks
            access_token = create_access_token(identity=user["email"])
            response = jsonify({"login": "successful"})
            set_access_cookies(response, access_token)
            return response, 200
    return jsonify({"login": "unsuccessful, user not found"}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    response = jsonify({"logout": "successful"})
    unset_jwt_cookies(response)
    return response, 200

# secured bookmarks endpoint
@app.route("/api/bookmarks", methods=["GET"])
@jwt_required()
def bookmarks():
    user = get_jwt_identity()
    user = users_db.find_one({"email": user})
    return jsonify({"data": user["email"]}), 200

@app.after_request
def refresh_expiring_jwts(response):
    try:
        expiry = get_jwt()["exp"]
        now = datetime.datetime.now(datetime.timezone.utc)
        buffer = datetime.datetime.timestamp(now + datetime.timedelta(minutes=10))
      
        if buffer > expiry:
            user = get_jwt_identity()
            access_token = create_access_token(identity=user)
            response = jsonify({"refresh": "successful"})
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # return the original response
        return response

@app.route("/api/topic/<string:id>", methods=["GET"])
def topic_query(id: str):
    if id not in topics:
        return make_response({"invalid topic ID: ": id}, 404)

    cache_hit = lru_cache.get(id)
    if cache_hit:
        return make_response(lru_cache.get(id), 200)
    
    response = papers_db.find({"topic": id}).limit(10)
    topic_data = []
    for paper in response:
        paper.pop("_id", None)
        topic_data.append(paper)
    lru_cache.put(id, topic_data)
    return make_response(topic_data, 200)

@app.route("/api/search/<string:query>", methods=["GET"])
def search_query(query: str):
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
    return make_response({"search query:": f"failed with query: {query}"}, 404)

if __name__ == "__main__":
    app.run(debug=False)