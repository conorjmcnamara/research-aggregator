import os
import pymongo
from dotenv import load_dotenv
from ..utils import *

def test_get_db_connection():
    # read from GitHub Actions
    if "GITHUB_ACTIONS" in os.environ:
        user = os.environ["MONGODB_USERNAME"]
        password = os.environ["MONGODB_PASSWORD"]
    # read from .env
    else:
        load_dotenv()
        user = os.getenv("USER")
        password = os.getenv("PASSWORD")
    
    db = get_db_connection(user, password, "papers")
    assert db is not None
    assert type(db) == pymongo.collection.Collection
    assert get_db_connection("username", "password", "collection") is None

def test_upload_db_data():
    demo_paper = {"topic": "AI"}
    assert upload_db_data("collection", [demo_paper]) is False
    assert upload_db_data("", [demo_paper]) is False
    assert upload_db_data("collection", []) is False

def test_lru_cache():
    lru_cache = LRUCache(3)
    lru_cache.put("AI", [{"paper_id": {"topic": "AI"}}])
    lru_cache.put("DB", [{"paper_id": {"topic": "DB"}}])
    lru_cache.put("DS", [{"paper_id": {"topic": "DS"}}])
    lru_cache.put("LG", [{"paper_id": {"topic": "LG"}}])
    assert lru_cache.get("AI") is None
    assert lru_cache.get("DB") == [{"paper_id": {"topic": "DB"}}]
    lru_cache.put("DB", [{"paper_id1": {"topic": "DB"}, "paper_id2": {"topic": "DB"}}])
    lru_cache.put("OS", [{"paper_id": {"topic": "OS"}}])
    assert lru_cache.get("DS") is None
    assert lru_cache.get("DB") == [{"paper_id1": {"topic": "DB"}, "paper_id2": {"topic": "DB"}}]

def test_topics_list():
    verify = ["AI", "CC", "CE", "CG", "CL", "CR", "CV", "CY", "DB", "DC", "DL",
             "DM", "DS", "ET", "FL", "GT", "GL", "GR", "AR", "HC", "IR", "IT",
             "LG", "LO", "MA", "MM", "MS", "NA", "NE", "NI", "OS", "PF", "PL",
             "RO", "SC", "SD", "SE", "SI", "SY"]
    for id in verify:
        assert topics.get(id)