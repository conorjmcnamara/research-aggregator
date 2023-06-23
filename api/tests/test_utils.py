import pymongo
import pytest_mock
import sys
sys.path.append("..")
from utils import get_env_var, get_db_connection, upload_db_data, LRUCache, topics

def test_get_env_var_with_jwt_key(mocker: pytest_mock.MockFixture):
    mocker.patch.dict("os.environ", {
        "GITHUB_ACTIONS": "",
        "MONGODB_USERNAME": "username",
        "MONGODB_PASSWORD": "password",
        "JWT_KEY": "jwt_key",
    })
    env = get_env_var(get_jwt_key=True)
    assert env == ("username", "password", "jwt_key")

def test_get_env_var_without_jwt_key(mocker: pytest_mock.MockFixture):
    mocker.patch("dotenv.load_dotenv")
    mocker.patch.dict("os.environ", {
        "MONGODB_USERNAME": "username",
        "MONGODB_PASSWORD": "password",
        "JWT_KEY": "jwt_key",
    })
    env = get_env_var()
    assert env == ("username", "password")

def test_get_db_connection():
    username, password = get_env_var()
    assert get_db_connection(username, password, "example_collection") == None
    assert get_db_connection("username", "password", "example_collection") == None

    papers_db = get_db_connection(username, password, "papers")
    users_db = get_db_connection(username, password, "users")
    assert papers_db != None and users_db != None
    assert type(papers_db) == pymongo.collection.Collection and type(users_db) == pymongo.collection.Collection

def test_upload_db_data_(mocker: pytest_mock.MockFixture):
    username, password = get_env_var()
    papers_db = get_db_connection(username, password, "papers")
    paper = {"title": "example_title", "topics": ["AI"]}
    assert upload_db_data("", [paper]) == False
    assert upload_db_data("papers_db", [paper]) == False
    assert upload_db_data(papers_db, []) == False

    mocker.patch.object(papers_db, "delete_many", return_value=None)
    mocker.patch.object(papers_db, "insert_many", return_value=None)
    assert upload_db_data(papers_db, [paper]) == True
    papers_db.delete_many.assert_called_once_with({})
    papers_db.insert_many.assert_called_once_with([paper])

def test_lru_cache():
    lru_cache = LRUCache(3)
    lru_cache.put("AI", [{"_id": {"topics": ["AI"]}}])
    lru_cache.put("DB", [{"_id": {"topics": ["DB"]}}])
    lru_cache.put("DS", [{"_id": {"topics": ["DS"]}}])
    lru_cache.put("LG", [{"_id": {"topics": ["LG"]}}])
    assert lru_cache.get("AI") == None
    assert lru_cache.get("DB") == [{"_id": {"topics": ["DB"]}}]
    
    lru_cache.put("DB", [{"_id1": {"topics": ["DB"]}, "_id2": {"topics": ["DB"]}}])
    lru_cache.put("OS", [{"_id": {"topics": ["OS"]}}])
    assert lru_cache.get("DS") == None
    assert lru_cache.get("DB") == [{"_id1": {"topics": ["DB"]}, "_id2": {"topics": ["DB"]}}]

def test_topics_list():
    verify = ["AI", "AR", "CC", "CE", "CG", "CL", "CR", "CV", "CY", "DB", "DC", "DL",
              "DM", "DS", "ET", "FL", "GT", "GR", "HC", "IR", "IT", "LG", "LO", "MA",
              "MM", "MS", "NA", "NE", "NI", "OS", "PF", "PL", "RO", "SC", "SD", "SE",
              "SI", "SY"]
    for id in verify:
        assert topics.get(id) != None