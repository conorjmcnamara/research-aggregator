import os
import hashlib
import datetime
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt,
    set_access_cookies, unset_jwt_cookies, get_jwt_identity
)
from dotenv import load_dotenv
from bson.objectid import ObjectId
from api.utils import get_db_connection, LRUCache, topics

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

# app.config['JWT_AUTH_USERNAME_KEY'] = 'email'

@app.route("/api/signup", methods=["POST"])
def signup():
    credentials = request.get_json()
    credentials["password"] = hashlib.sha256(credentials["password"].encode("utf-8")).hexdigest()
    user = users_db.find_one({"email": credentials["email"]})
    
    # check if the user exists in the database
    if not user:
        credentials["bookmarks"] = []
        users_db.insert_one(credentials)
        return jsonify({"data": "signup successful"}), 201
    return jsonify({"data": "signup unsuccessful, user already exists"}), 409

@app.route("/api/login", methods=["POST"])
def login():
    credentials = request.get_json()
    encrypted_password = hashlib.sha256(credentials["password"].encode("utf-8")).hexdigest()
    user = users_db.find_one({"email": credentials["email"]})
    
    # check if the user is new
    if user and encrypted_password == user["password"]:
        # create double submit protection cookies to prevent CSRF attacks
        access_token = create_access_token(identity=user["email"])
        response = jsonify({"data": "login successful"})
        set_access_cookies(response, access_token)
        return response, 200
    return jsonify({"data": "login unsuccessful, user not found"}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    response = jsonify({"data": "logout successful"})
    unset_jwt_cookies(response)
    return response, 200

# secured user account endpoint
@app.route("/api/user", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def user():
    credentials = get_jwt_identity()

    # get email
    if request.method == "GET":
        return jsonify(credentials), 200

    elif request.method == "PUT":
        new_credentials = request.get_json()
        user = users_db.find_one({"email": credentials})

        # update email
        if "newEmail" in new_credentials:
            users_db.update_one({"email": credentials}, {"$set": {"email": new_credentials["newEmail"]}})
            access_token = create_access_token(identity=new_credentials["newEmail"])
            response = jsonify({"data": "email update successful"})
            set_access_cookies(response, access_token)
            return response, 200

        # update password
        elif "newPassword" in new_credentials:
            encrypted_password = hashlib.sha256(new_credentials["newPassword"].encode("utf-8")).hexdigest()
            if encrypted_password == user["password"]:
                return jsonify({"data": "password update unsuccessful"}), 409
            users_db.update_one({"email": credentials}, {"$set": {"password": encrypted_password}})
            return jsonify({"data": "password update successful"}), 200
    
    # delete account
    else:
        users_db.delete_one({"email": credentials})
        response = jsonify({"account deletion": "successful"})
        unset_jwt_cookies(response)
        return response, 200

# secured bookmarks endpoint
@app.route("/api/bookmarks", methods=["GET", "POST", "DELETE"])
@jwt_required()
def bookmarks():
    credentials = get_jwt_identity()
    user = users_db.find_one({"email": credentials})
    bookmarks = user["bookmarks"]

    # get all bookmarked papers
    if request.method == "GET":
        response = papers_db.find({"_id": {"$in": [ObjectId(paper_id) for paper_id in bookmarks]}})
        bookmark_data = {}
        for paper in response:
            paper["_id"] = str(paper["_id"])
            bookmark_data[paper["_id"]] = paper
        return jsonify(bookmark_data), 200
    
    # add a paper to the bookmarks list
    elif request.method == "POST":
        paper_uid = request.get_json()["uid"]
        users_db.update_one({"email": user["email"]}, {"$addToSet": {"bookmarks": paper_uid}})
        return jsonify({"data": "bookmark addition successful"}), 201
    
    # delete a paper from the bookmarks list
    else:
        paper_uid = request.get_json()["uid"]
        users_db.update_one({"email": user["email"]}, {"$pull": {"bookmarks": paper_uid}})
        return jsonify({"data": "bookmark deletion successful"}), 200

@app.after_request
def refresh_expiring_jwts(response):
    try:
        expiry = get_jwt()["exp"]
        now = datetime.datetime.now(datetime.timezone.utc)
        buffer = datetime.datetime.timestamp(now + datetime.timedelta(minutes=10))
        
        if buffer > expiry:
            user = get_jwt_identity()
            access_token = create_access_token(identity=user)
            response = jsonify({"data": "JWT refresh successful"})
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response

@app.route("/api/topic/<string:id>", methods=["GET"])
def topic_query(id: str):
    if id not in topics:
        return jsonify({"data": "invalid topic ID: " + id}), 404

    cache_hit = lru_cache.get(id)
    if cache_hit:
        return jsonify(lru_cache.get(id)), 200
    
    response = papers_db.find({"topic": id}).limit(10)
    topic_data = {}
    for paper in response:
        paper["_id"] = str(paper["_id"])
        topic_data[paper["_id"]] = paper
    lru_cache.put(id, topic_data)
    return jsonify(topic_data), 200

@app.route("/api/search/<string:query>", methods=["GET"])
def search_query(query: str):
    response = [{
        "$search": {
            "index": "papers_index",
            "text": {
                "query": query,
                "path": ["title", "abstract"]
            }
        }
    }, {"$limit": 10}]

    if response:
        search_data = {}
        for paper in papers_db.aggregate(response):
            paper["_id"] = str(paper["_id"])
            search_data[paper["_id"]] = paper
        return jsonify(search_data), 200
    return jsonify({"data:": f"empty search with query: {query}"}), 404

if __name__ == "__main__":
    app.run(debug=False)