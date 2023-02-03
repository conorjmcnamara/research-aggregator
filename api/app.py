from flask import Flask, jsonify, make_response
from cache import LRUCache
from dbparser import db, topic_id

# configuration
app = Flask(__name__)
lru_cache = LRUCache(10)

@app.route("/query/<string:id>")
def query(id):
    # check for a valid topic ID
    if id not in topic_id:
        return make_response({"Invalid ID": id}, 404)
    else:
        # cache hit
        if lru_cache.get(id):
            return make_response(jsonify(lru_cache.get(id)), 200)
        # cache miss
        else:
            # request data from MongoDB Atlas
            topic_data = db.find_one({"topic": id})
            
            # remove the database document ID
            topic_data.pop("_id", None)
            lru_cache.put(id, topic_data)
            return make_response(jsonify(topic_data), 200)

if __name__ == "__main__":
    app.run(debug=False)