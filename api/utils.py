import logging
import pymongo
from collections import OrderedDict
from typing import Optional

def get_db_connection(username: str, password: str, collection: str) -> Optional[pymongo.collection.Collection]:
    connection = f"mongodb+srv://{username}:{password}@research.holkbao.mongodb.net/?retryWrites=true&w=majority"
    try:
        client = pymongo.MongoClient(connection)
        db = client["research"]
        if collection not in db.list_collection_names():
            logging.critical(f"Collection {collection} does not exist")
            return None
        logging.info("Connected to MongoDB Atlas")
        return db[collection]
    except:
        logging.critical("Failed to connect to MongoDB Atlas")
        return None

def upload_db_data(papers_db: pymongo.collection.Collection, papers: list) -> bool:
    try:
        papers_db.delete_many({})
        papers_db.insert_many(papers)
        logging.info("Successfully updated the MongoDB Atlas database")
        return True
    except:
        logging.critical("Failed to update the MongoDB Atlas database")
        return False

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

# simplify topic names for the Semantic Scholar API
topics = {
    "AI": "artificial+intelligence",
    "CC": "computational+complexity",
    "CE": "computational+engineering+finance+science",
    "CG": "computational+geometry",
    "CL": "computation+language",
    "CR": "cryptography+security",
    "CV": "computer+vision+pattern+recognition",
    "CY": "computers+society",
    "DB": "databases",
    "DC": "distributed+parallel+cluster+computing",
    "DL": "digital+libraries",
    "DM": "discrete+mathematics",
    "DS": "data+structures+algorithms",
    "ET": "emerging+technologies",
    "FL": "formal+languages+automata+theory",
    "GT": "game+theory",
    "GL": "general+literature",
    "GR": "graphics",
    "AR": "hardware+architecture",
    "HC": "human+computer+interaction", 
    "IR": "information+retrieval",
    "IT": "information+theory",
    "LG": "machine+learning",
    "LO": "logic+in+computer+science",
    "MA": "multiagent+systems",
    "MM": "multimedia",
    "MS": "mathematical+software",
    "NA": "numerical+analysis",
    "NE": "neural+evolutionary+computing",
    "NI": "networking+internet+architecture",
    "OH": "other",
    "OS": "operating+systems",
    "PF": "performance",
    "PL": "programming+languages",
    "RO": "robotics",
    "SC": "symbolic+computation",
    "SD": "sound",
    "SE": "software+sngineering",
    "SI": "social+information+networks",
    "SY": "systems+control"
}