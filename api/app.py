from flask import Flask, make_response
from cache import LRUCache
from utils import db, topics

# configuration
app = Flask(__name__)
lru_cache = LRUCache(10)

@app.route("/topic-query/<string:id>")
def topic_query(id: str):
    # check for a valid topic ID
    if id not in topics:
        return make_response({"Invalid topic ID: ": id}, 404)

    # cache hit
    if lru_cache.get(id):
        return make_response(lru_cache.get(id), 200)
    # cache miss
    response = db.find({"topic": id}).limit(10)
    topic_data = []

    for paper in response:
        # remove the database document ID
        paper.pop("_id", None)
        topic_data.append(paper)
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
                "path": ["title", "abstract"]
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