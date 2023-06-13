import os
import pymongo
import sys
sys.path.append("..")
from dotenv import load_dotenv
from utils import get_db_connection, upload_db_data, LRUCache, topics

def test_get_db_connection():
    if "GITHUB_ACTIONS" in os.environ:
        user = os.environ["MONGODB_USERNAME"]
        password = os.environ["MONGODB_PASSWORD"]
    else:
        load_dotenv()
        user = os.getenv("MONGODB_USERNAME")
        password = os.getenv("MONGODB_PASSWORD")
    
    db = get_db_connection(user, password, "papers")
    assert db != None
    assert type(db) == pymongo.collection.Collection
    assert get_db_connection("username", "password", "collection") == None

def test_upload_db_data():
    demo_paper = {"topic": "AI"}
    assert upload_db_data("collection", [demo_paper]) == False
    assert upload_db_data("", [demo_paper]) == False
    assert upload_db_data("collection", []) == False

def test_lru_cache():
    # cache condensed versions of papers
    lru_cache = LRUCache(3)
    lru_cache.put("AI", [{"_id": {"topic": "AI"}}])
    lru_cache.put("DB", [{"_id": {"topic": "DB"}}])
    lru_cache.put("DS", [{"_id": {"topic": "DS"}}])
    lru_cache.put("LG", [{"_id": {"topic": "LG"}}])
    assert lru_cache.get("AI") == None
    assert lru_cache.get("DB") == [{"_id": {"topic": "DB"}}]
    
    lru_cache.put("DB", [{"_id1": {"topic": "DB"}, "_id2": {"topic": "DB"}}])
    lru_cache.put("OS", [{"_id": {"topic": "OS"}}])
    assert lru_cache.get("DS") == None
    assert lru_cache.get("DB") == [{"_id1": {"topic": "DB"}, "_id2": {"topic": "DB"}}]

def test_topics_list():
    verify = ["AI", "CC", "CE", "CG", "CL", "CR", "CV", "CY", "DB", "DC", "DL",
              "DM", "DS", "ET", "FL", "GT", "GR", "AR", "HC", "IR", "IT", "LG",
              "LO", "MA", "MM", "MS", "NA", "NE", "NI", "OS", "PF", "PL", "RO",
              "SC", "SD", "SE", "SI", "SY"]
    for id in verify:
        assert topics.get(id) != None