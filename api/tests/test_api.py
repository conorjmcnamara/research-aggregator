import hashlib
import sys
sys.path.append("..")
from app import app, users_db, papers_db, lru_cache
from tests.db_mocks import db_papers, parsed_papers

SERVER = app.test_client()

def test_topic_query_route(mocker):
    response = SERVER.get("/api/topic/test")
    assert response.status_code == 404
    
    # mock cache miss
    mocker.patch.object(lru_cache, "get")
    mocker.patch.object(papers_db, "find")
    lru_cache.get.return_value = None

    query_cursor = mocker.MagicMock()
    query_cursor.limit.return_value = db_papers
    papers_db.find.return_value = query_cursor
    id = "AI"

    response = SERVER.get(f"api/topic/{id}")
    assert response.status_code == 200
    assert response.json == parsed_papers
    lru_cache.get.assert_called_once_with(id)
    papers_db.find.assert_called_once_with({"topics": [id]})

    # mock cache hit
    lru_cache.get.reset_mock()
    papers_db.find.reset_mock()
    lru_cache.get.return_value = parsed_papers
    
    response = SERVER.get(f"api/topic/{id}")
    assert response.status_code == 200
    lru_cache.get.assert_called_once_with(id)
    papers_db.find.assert_not_called()

def test_search_query_route(mocker):
    # mock query with empty response
    mocker.patch.object(papers_db, "aggregate")
    papers_db.aggregate.return_value = []
    response = SERVER.get("/api/search/test")
    assert response.status_code == 404

    # mock query with response
    papers_db.aggregate.reset_mock()
    papers_db.aggregate.return_value = db_papers
    response = SERVER.get("/api/search/AI")
    assert response.status_code == 200
    assert response.json == parsed_papers

def test_signup_route(mocker):
    # mock signup with new credentials
    mocker.patch.object(users_db, "find_one")
    mocker.patch.object(users_db, "insert_one")
    users_db.find_one.return_value = None
    credentials = {"email": "test@example.com", "password": "test123"}
    response = SERVER.post("/api/signup", json=credentials)

    assert response.status_code == 201
    users_db.find_one.assert_called_once_with({"email": credentials["email"]})
    users_db.insert_one.assert_called_once_with({
        "email": "test@example.com",
        "password": hashlib.sha256(credentials["password"].encode("utf-8")).hexdigest(),
        "bookmarks": []
    })

    # mock signup with existing credentials
    users_db.find_one.reset_mock()
    users_db.insert_one.reset_mock()
    users_db.find_one.return_value = {"email": credentials["email"]}
    response = SERVER.post("/api/signup", json=credentials)

    assert response.status_code == 409
    users_db.find_one.assert_called_with({"email": credentials["email"]})
    users_db.insert_one.assert_not_called()