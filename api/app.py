from flask import Flask, make_response
from cache import LRUCache
from dbparser import db, topic_id

# configuration
app = Flask(__name__)
lru_cache = LRUCache(10)

@app.route("/topic-query/<string:id>")
def topic_query(id: str):
    # check for a valid topic ID
    if id not in topic_id:
        return make_response({"Invalid topic ID: ": id}, 404)

    # cache hit
    if lru_cache.get(id):
        return make_response(lru_cache.get(id), 200)
    # cache miss
    req = db.find({"topic": id}).limit(10)
    topic_data = []

    # remove the database document ID
    for json_obj in req:
        json_obj.pop("_id", None)
        topic_data.append(json_obj)
    lru_cache.put(id, topic_data)
    return make_response(topic_data, 200)

@app.route("/search-query/<string:query>")
def search_query(query: str):
    # search for research papers with the passed query
    pipeline = [{
        "$search": {
            "index": "papers_index",
            "text": {
                "query": query,
                "path": ["title", "summary"]
            }
        }
    }, {"$limit": 10}]

    if pipeline:
        search_data = []
        for paper in db.aggregate(pipeline):
            paper.pop("_id", None)
            search_data.append(paper)
        return make_response(search_data, 200)
    return make_response({"Failed to make a search query with:": query}, 404)

if __name__ == "__main__":
    app.run(debug=False)