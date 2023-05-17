import sys
sys.path.append("..")
from app import app

SERVER = app.test_client()
FIELDS = ["title", "date", "abstract", "url", "source", "authors", "topics"]

def test_topic_query_route():
    response = SERVER.get("/api/topic/ZZZZZ")
    assert response.status_code == 404
    assert response.json["data"] == "invalid topic ID: ZZZZZ"

    response = SERVER.get("/api/topic/AI")
    assert response.status_code == 200
    papers = list(response.json.values())
    for field in FIELDS:
        assert field in papers[0]

def test_search_query_route():
    response = SERVER.get("/api/search/ZZZZZ")
    assert response.status_code == 404
    assert response.json["data"] == "empty search result with query: ZZZZZ"

    response = SERVER.get("/api/search/python")
    assert response.status_code == 200
    papers = list(response.json.values())
    for field in FIELDS:
        assert field in papers[0]