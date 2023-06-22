import hashlib
import pytest_mock
import sys
sys.path.append("..")
from typing import Dict, Any
from app import app, users_db, papers_db, lru_cache, ObjectId
from tests.mocks.db_mocks import db_papers_response, parsed_db_papers_response

SERVER = app.test_client()
CREDENTIALS = {"email": "text@example.com", "password": "test123"}
VALID_USERS_DB_ENTRY = {
    "email": CREDENTIALS["email"],
    "password": hashlib.sha256(CREDENTIALS["password"].encode("utf-8")).hexdigest(),
    "bookmarks": ["645cfd573007dd700aa1fe7d", "645cfd573007dd700aa1fe80"]
}

def login_helper(mocker: pytest_mock.MockFixture, mock_users_db_return_value: Dict[Any, Any]):
    mocker.patch.object(users_db, "find_one")
    users_db.find_one.return_value = mock_users_db_return_value
    return SERVER.post("/api/login", json=CREDENTIALS)

def extract_csrf_token_helper(headers: str) -> str:
    cookies = headers.getlist("Set-Cookie")
    cookie_of_interest = "csrf_access_token="
    for cookie in cookies:
        if cookie.startswith(cookie_of_interest):
            start_csrf_cookie = cookie.find(cookie_of_interest) + len(cookie_of_interest)
            end_csrf_cookie = cookie.find(";", start_csrf_cookie)
            return cookie[start_csrf_cookie:end_csrf_cookie]
    return ""

def test_topic_query_invalid_topic_id():
    invalid_topic_id = "test"
    response = SERVER.get(f"/api/topic/{invalid_topic_id}")
    assert response.status_code == 404

def test_topic_query_cache_miss(mocker: pytest_mock.MockFixture):
    mocker.patch.object(lru_cache, "get", return_value=None)
    query_cursor = mocker.MagicMock()
    query_cursor.limit.return_value = db_papers_response
    mocker.patch.object(papers_db, "find", return_value=query_cursor)
    valid_topic_id = "AI"

    response = SERVER.get(f"api/topic/{valid_topic_id}")
    assert response.status_code == 200
    assert response.json == parsed_db_papers_response
    lru_cache.get.assert_called_once_with(valid_topic_id)
    papers_db.find.assert_called_once_with({"topics": [valid_topic_id]})

def test_topic_query_cache_hit(mocker: pytest_mock.MockFixture):
    mocker.patch.object(lru_cache, "get", return_value=parsed_db_papers_response)
    mocker.patch.object(papers_db, "find")
    valid_topic_id = "AI"

    response = SERVER.get(f"api/topic/{valid_topic_id}")
    assert response.status_code == 200
    lru_cache.get.assert_called_once_with(valid_topic_id)
    papers_db.find.assert_not_called()

def test_search_query_empty_response(mocker: pytest_mock.MockFixture):
    mocker.patch.object(papers_db, "aggregate", return_value=[])
    response = SERVER.get("/api/search/test")
    assert response.status_code == 404

def test_search_query_with_response(mocker: pytest_mock.MockerFixture):
    mocker.patch.object(papers_db, "aggregate", return_value=db_papers_response)
    response = SERVER.get("/api/search/AI")
    assert response.status_code == 200
    assert response.json == parsed_db_papers_response

def test_signup_exisiting_credentials(mocker: pytest_mock.MockFixture):
    mocker.patch.object(users_db, "find_one", return_value=VALID_USERS_DB_ENTRY)
    mocker.patch.object(users_db, "insert_one")
    response = SERVER.post("/api/signup", json=CREDENTIALS)
    assert response.status_code == 409
    users_db.insert_one.assert_not_called()

def test_signup_new_credentials(mocker: pytest_mock.MockerFixture):
    mocker.patch.object(users_db, "find_one", return_value=None)
    mocker.patch.object(users_db, "insert_one")
    response = SERVER.post("/api/signup", json=CREDENTIALS)
    assert response.status_code == 201
    users_db.find_one.assert_called_once_with({"email": CREDENTIALS["email"]})
    valid_users_db_entry_no_bookmarks = VALID_USERS_DB_ENTRY.copy()
    valid_users_db_entry_no_bookmarks["bookmarks"] = []
    users_db.insert_one.assert_called_once_with(valid_users_db_entry_no_bookmarks)

def test_login_not_found(mocker: pytest_mock.MockerFixture):
    response = login_helper(mocker, None)
    assert response.status_code == 401

def test_login_invalid_password(mocker: pytest_mock.MockerFixture):
    invalid_users_db_entry = VALID_USERS_DB_ENTRY.copy()
    invalid_users_db_entry["password"] = CREDENTIALS["password"] + "test"
    response = login_helper(mocker, invalid_users_db_entry)
    assert response.status_code == 401

def test_login_valid(mocker: pytest_mock.MockerFixture):
    response = login_helper(mocker, VALID_USERS_DB_ENTRY)
    assert response.status_code == 200
    cookies = response.headers.getlist("Set-Cookie")
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

def test_user_no_access_tokens():
    response = SERVER.get("/api/user")
    assert response.status_code == 401

def test_user_get(mocker: pytest_mock.MockerFixture):
    login_helper(mocker, VALID_USERS_DB_ENTRY)
    response = SERVER.get("/api/user")
    assert response.status_code == 200

def test_user_put_invalid(mocker: pytest_mock.MockerFixture):
    login_response = login_helper(mocker, VALID_USERS_DB_ENTRY)
    headers = {"Content-Type": "application/json", "X-CSRF-TOKEN": extract_csrf_token_helper(login_response.headers)}
    json = {"email": CREDENTIALS["email"]} 
    mocker.patch.object(users_db, "find_one", return_value=VALID_USERS_DB_ENTRY)
    mocker.patch.object(users_db, "update_one")

    # same email as in user's account
    response = SERVER.put("/api/user", json=json, headers=headers)
    assert response.status_code == 409

    # same password as in user's account
    json = {"password": CREDENTIALS["password"]}
    response = SERVER.put("/api/user", json=json, headers=headers)
    assert response.status_code == 409

    # JSON without an email or password key
    response = SERVER.put("/api/user", json={"test": "example"}, headers=headers)
    assert response.status_code == 409

def test_user_put_valid(mocker: pytest_mock.MockerFixture):
    login_response = login_helper(mocker, VALID_USERS_DB_ENTRY)
    headers = {"Content-Type": "application/json", "X-CSRF-TOKEN": extract_csrf_token_helper(login_response.headers)}
    json = {"email": CREDENTIALS["email"] + "test"}

    # different email than in user's account
    response = SERVER.put("/api/user", json=json, headers=headers)
    assert response.status_code == 200
    headers["X-CSRF-TOKEN"] = extract_csrf_token_helper(response.headers)

    # different password than in user's account
    json = {"password": CREDENTIALS["password"] + "test"}
    response = SERVER.put("/api/user", json=json, headers=headers)
    assert response.status_code == 200

def test_user_delete(mocker: pytest_mock.MockerFixture):
    login_response = login_helper(mocker, VALID_USERS_DB_ENTRY)
    headers = {"Content-Type": "application/json", "X-CSRF-TOKEN": extract_csrf_token_helper(login_response.headers)}
    mocker.patch.object(users_db, "delete_one")
    response = SERVER.delete("/api/user", headers=headers)
    assert response.status_code == 200

    # check no access tokens remain
    response = SERVER.get("/api/user")
    assert response.status_code == 401

def test_bookmarks_no_access_tokens():
    response = SERVER.get("/api/bookmarks")
    assert response.status_code == 401

def test_bookmarks_get(mocker: pytest_mock.MockerFixture):
    login_helper(mocker, VALID_USERS_DB_ENTRY)
    mocker.patch.object(users_db, "find_one", return_value=VALID_USERS_DB_ENTRY)
    mocker.patch.object(papers_db, "find", return_value=db_papers_response)
    response = SERVER.get("/api/bookmarks")
    assert response.status_code == 200
    assert response.json == parsed_db_papers_response
    papers_db.find.assert_called_once_with({"_id": {"$in": [ObjectId(paper_id) for paper_id in VALID_USERS_DB_ENTRY["bookmarks"]]}})

def test_bookmarks_put(mocker: pytest_mock.MockerFixture):
    login_response = login_helper(mocker, VALID_USERS_DB_ENTRY)
    headers = {"Content-Type": "application/json", "X-CSRF-TOKEN": extract_csrf_token_helper(login_response.headers)}
    json = {"uid": "645cfd573007dd700aa1fe80"}
    mocker.patch.object(users_db, "update_one")
    response = SERVER.post("/api/bookmarks", json=json, headers=headers)
    assert response.status_code == 201
    users_db.update_one.assert_called_once_with({"email": VALID_USERS_DB_ENTRY["email"]}, {"$addToSet": {"bookmarks": json["uid"]}})

def test_bookmarks_delete(mocker: pytest_mock.MockerFixture):
    login_response = login_helper(mocker, VALID_USERS_DB_ENTRY)
    headers = {"Content-Type": "application/json", "X-CSRF-TOKEN": extract_csrf_token_helper(login_response.headers)}
    json = {"uid": "645cfd573007dd700aa1fe80"}
    mocker.patch.object(users_db, "update_one")
    response = SERVER.delete("/api/bookmarks", json=json, headers=headers)
    assert response.status_code == 200
    users_db.update_one.assert_called_once_with({"email": VALID_USERS_DB_ENTRY["email"]}, {"$pull": {"bookmarks": json["uid"]}})