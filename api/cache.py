from collections import OrderedDict
from typing import Optional

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, id: str) -> Optional[list]:
        if id in self.cache:
            self.cache.move_to_end(id)
            return self.cache[id]
        return None
        
    def put(self, id: str, papers: list) -> None:
        self.cache[id] = papers
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
        self.cache.move_to_end(id)