import hashlib
import pytest_mock
import sys
sys.path.append("..")
from app import app, users_db, papers_db, lru_cache
from tests.mocks.db_mocks import db_papers, parsed_papers

SERVER = app.test_client()

def test_topic_query(mocker: pytest_mock.MockFixture):
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

def test_search_query(mocker: pytest_mock.MockFixture):
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

def test_signup(mocker: pytest_mock.MockFixture):
    # mock signup with new credentials
    mocker.patch.object(users_db, "find_one")
    mocker.patch.object(users_db, "insert_one")
    users_db.find_one.return_value = None
    credentials = {"email": "test@example.com", "password": "test123"}
    response = SERVER.post("/api/signup", json=credentials)

    assert response.status_code == 201
    users_db.find_one.assert_called_once_with({"email": credentials["email"]})
    users_db.insert_one.assert_called_once_with({
        "email": credentials["email"],
        "password": hashlib.sha256(credentials["password"].encode("utf-8")).hexdigest(),
        "bookmarks": []
    })

    # mock signup with existing credentials
    users_db.find_one.reset_mock()
    users_db.insert_one.reset_mock()
    users_db.find_one.return_value = {
        "email": credentials["email"],
        "password": hashlib.sha256(credentials["password"].encode("utf-8")).hexdigest(),
        "bookmarks": []
    }
    response = SERVER.post("/api/signup", json=credentials)
    assert response.status_code == 409
    users_db.insert_one.assert_not_called()

def test_login(mocker: pytest_mock.MockerFixture):
    # mock user not found
    mocker.patch.object(users_db, "find_one")
    users_db.find_one.return_value = None
    credentials = {"email": "test@example.com", "password": "test123"}
    response = SERVER.post("/api/login", json=credentials)
    assert response.status_code == 401
    users_db.find_one.assert_called_once_with({"email": credentials["email"]})

    # mock invalid password
    users_db.find_one.reset_mock()
    users_db.find_one.return_value = {
        "email": credentials["email"],
        "password": hashlib.sha256("existing_password".encode("utf-8")).hexdigest(),
        "bookmarks": []
    }
    response = SERVER.post("/api/login", json=credentials)
    assert response.status_code == 401

    # mock successful login
    users_db.find_one.reset_mock()
    users_db.find_one.return_value = {
        "email": credentials["email"],
        "password": hashlib.sha256(credentials["password"].encode("utf-8")).hexdigest(),
        "bookmarks": []
    }
    response = SERVER.post("/api/login", json=credentials)
    assert response.status_code == 200
    cookies = response.headers.getlist("Set-Cookie")
    assert len(cookies) == 2
    csrf_token_cookie_found = False
    access_token_cookie_found = False
    for cookie in cookies:
        if cookie.startswith("csrf_access_token=") and not cookie.endswith("="):
            csrf_token_cookie_found = True
        elif "access_token_cookie=" in cookie and "HttpOnly" in cookie:
            # verify the JWT header
            access_token = cookie.split(";")[0].split("=")[1]
            assert access_token.startswith("eyJ")
            access_token_cookie_found = True
    assert csrf_token_cookie_found
    assert access_token_cookie_found

def test_logout():
    # Flask test client handles cookie generation in this context
    response = SERVER.post("/api/logout")
    assert response.status_code == 200
    cookies = response.headers.getlist("Set-Cookie")
    csrf_token_cookie_found = False
    access_token_cookie_found = False
    for cookie in cookies:
        if cookie.startswith("csrf_access_token=") and cookie.endswith("="):
            csrf_token_cookie_found = True
        elif cookie.startswith("access_token_cookie=") and cookie.endswith("="):
            access_token_cookie_found = True
    assert not access_token_cookie_found
    assert not csrf_token_cookie_found