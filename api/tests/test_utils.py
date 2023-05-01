from api.utils import LRUCache

def test_lru_cache():
    lru = LRUCache(5)
    lru.put("DB", [{"topic": "DB"}])
    assert lru.get("DB") == [{"topic": "DB"}]
    assert lru.get("AI") == None