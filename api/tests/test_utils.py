import os
from dotenv import load_dotenv
from api.utils import LRUCache, get_db_connection

def test_lru_cache():
    lru = LRUCache(5)
    lru.put("DB", [{"topic": "DB"}])
    assert lru.get("DB") == [{"topic": "DB"}]
    assert lru.get("AI") == None

def test_get_db_connection():
    # read secrets from GitHub Actions
    if "GITHUB_ACTIONS" in os.environ:
        user = os.environ["MONGODB_USERNAME"]
        password = os.environ["MONGODB_PASSWORD"]
    # read secrets from .env file
    else:
        load_dotenv()
        user = os.getenv("USER")
        password = os.getenv("PASSWORD")

    assert get_db_connection(user, password, "papers") is not None
    assert get_db_connection("foo", "bar", "baz") is None