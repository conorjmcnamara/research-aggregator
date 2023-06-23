import hashlib
import datetime
import flask_jwt_extended
from flask import Flask, request, jsonify
from bson.objectid import ObjectId
from api.utils import get_env_var, get_db_connection, LRUCache, topics

app = Flask(__name__)
jwt = flask_jwt_extended.JWTManager(app)
lru_cache = LRUCache(10)

username, password, jwt_key = get_env_var(get_jwt_key=True)
papers_db = get_db_connection(username, password, "papers")
users_db = get_db_connection(username, password, "users")

# JWT cookie-based authentication
app.config["JWT_SECRET_KEY"] = jwt_key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)
app.config["JWT_TOKEN_LOCATION"] = "cookies"
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_COOKIE_CSRF_PROTECT"] = True

@app.route("/api/topic/<string:id>", methods=["GET"])
def topic_query(id: str):
    if id not in topics:
        return jsonify({"data": f"Invalid topic ID: {id}"}), 404

    cache_hit = lru_cache.get(id)
    if cache_hit:
        return jsonify(cache_hit), 200
    
    response = papers_db.find({"topics": [id]}).limit(10)
    topic_data = {}
    for paper in response:
        paper["_id"] = str(paper["_id"])
        topic_data[paper["_id"]] = paper
    lru_cache.put(id, topic_data)
    return jsonify(topic_data), 200

@app.route("/api/search/<string:query>", methods=["GET"])
def search_query(query: str):
    response_pipeline = list(papers_db.aggregate([{
        "$search": {
            "index": "papers_index",
            "text": {
                "query": query,
                "path": ["title", "abstract"]
            }
        }
    }, {"$limit": 10}]))

    if not response_pipeline:
        return jsonify({"data": f"Empty search result with query: {query}"}), 404
    search_data = {}
    for paper in response_pipeline:
        paper["_id"] = str(paper["_id"])
        search_data[paper["_id"]] = paper
    return jsonify(search_data), 200

@app.route("/api/signup", methods=["POST"])
def signup():
    credentials = request.get_json()
    credentials["password"] = hashlib.sha256(credentials["password"].encode("utf-8")).hexdigest()
    user = users_db.find_one({"email": credentials["email"]})

    if not user:
        credentials["bookmarks"] = []
        users_db.insert_one(credentials)
        return jsonify({"data": "Signup successful"}), 201
    return jsonify({"data": "Signup unsuccessful, user already exists"}), 409

@app.route("/api/login", methods=["POST"])
def login():
    credentials = request.get_json()
    encrypted_password = hashlib.sha256(credentials["password"].encode("utf-8")).hexdigest()
    user = users_db.find_one({"email": credentials["email"]})
    
    if user and encrypted_password == user["password"]:
        # create double submit protection cookies to prevent CSRF attacks
        access_token = flask_jwt_extended.create_access_token(identity=user["email"])
        response = jsonify({"data": "Login successful"})
        flask_jwt_extended.set_access_cookies(response, access_token)
        return response, 200
    return jsonify({"data": "Login unsuccessful, user not found"}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    response = jsonify({"data": "Logout successful"})
    flask_jwt_extended.unset_jwt_cookies(response)
    return response, 200

@app.route("/api/user", methods=["GET", "PUT", "DELETE"])
@flask_jwt_extended.jwt_required()
def user():
    credentials = flask_jwt_extended.get_jwt_identity()

    # get email
    if request.method == "GET":
        return jsonify(credentials), 200

    elif request.method == "PUT":
        user = users_db.find_one({"email": credentials})
        new_credentials = request.get_json()

        # update email
        if "email" in new_credentials:
            if new_credentials["email"] == user["email"]:
                return jsonify({"data": "Email update unsuccessful"}), 409
            users_db.update_one({"email": credentials}, {"$set": {"email": new_credentials["email"]}})
            access_token = flask_jwt_extended.create_access_token(identity=new_credentials["email"])
            response = jsonify({"data": "Email update successful"})
            flask_jwt_extended.set_access_cookies(response, access_token)
            return response, 200

        # update password
        elif "password" in new_credentials:
            encrypted_password = hashlib.sha256(new_credentials["password"].encode("utf-8")).hexdigest()
            if encrypted_password == user["password"]:
                return jsonify({"data": "Password update unsuccessful"}), 409
            users_db.update_one({"email": credentials}, {"$set": {"password": encrypted_password}})
            return jsonify({"data": "Password update successful"}), 200

        else:
            return jsonify({"data": "PUT request JSON must contain an \'email\' or \'password\' key"}), 409
    
    # delete account
    else:
        users_db.delete_one({"email": credentials})
        response = jsonify({"data": "Account deletion successful"})
        flask_jwt_extended.unset_jwt_cookies(response)
        return response, 200

@app.route("/api/bookmarks", methods=["GET", "POST", "DELETE"])
@flask_jwt_extended.jwt_required()
def bookmarks():
    credentials = flask_jwt_extended.get_jwt_identity()
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
        return jsonify({"data": "Bookmark addition successful"}), 201
    
    # delete a paper from the bookmarks list
    else:
        paper_uid = request.get_json()["uid"]
        users_db.update_one({"email": user["email"]}, {"$pull": {"bookmarks": paper_uid}})
        return jsonify({"data": "Bookmark deletion successful"}), 200

@app.after_request
def refresh_expiring_jwts(response):
    try:
        expiry = flask_jwt_extended.get_jwt()["exp"]
        now = datetime.datetime.now(datetime.timezone.utc)
        ten_mins_from_now = datetime.datetime.timestamp(now + datetime.timedelta(minutes=10))

        if expiry < ten_mins_from_now:
            user = flask_jwt_extended.get_jwt_identity()
            access_token = flask_jwt_extended.create_access_token(identity=user)
            response = jsonify({"data": "JWT refresh successful"})
            flask_jwt_extended.set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response

if __name__ == "__main__":
    app.run(debug=False)