from collections import OrderedDict
from typing import Optional

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: str) -> Optional[list]:
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
        
    def put(self, key: str, value: list) -> None:
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
        self.cache.move_to_end(key)