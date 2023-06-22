import os
import logging
import pymongo
from dotenv import load_dotenv
from collections import OrderedDict
from typing import Union, Tuple, Optional, List, DefaultDict, Dict, Any

def get_env_var(get_jwt_key: bool = False) -> Union[Tuple[str, str], Tuple[str, str, str]]:
    if "GITHUB_ACTIONS" in os.environ:
        username = os.environ["MONGODB_USERNAME"]
        password = os.environ["MONGODB_PASSWORD"]
        jwt_key = os.environ["JWT_KEY"]
    else:
        load_dotenv()
        username = os.getenv("MONGODB_USERNAME")
        password = os.getenv("MONGODB_PASSWORD")
        jwt_key = os.getenv("JWT_KEY")
    if get_jwt_key:
        return (username, password, jwt_key)
    return (username, password)

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
    except Exception as error:
        logging.critical(f"Failed to connect to MongoDB Atlas. Error: {error}")
        return None

def upload_db_data(papers_db: pymongo.collection.Collection, papers: List[DefaultDict[str, list]]) -> bool:
    if papers_db is None or not papers:
        logging.critical("Invalid MongoDB Atlas collection or upload list")
        return False
    try:
        papers_db.delete_many({})
        papers_db.insert_many(papers)
        logging.info("Successfully updated the MongoDB Atlas database")
        return True
    except Exception as error:
        logging.critical(f"Failed to update the MongoDB Atlas database. Error: {error}")
        return False

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, id: str) -> Optional[Dict[str, Dict[str, Any]]]:
        if id in self.cache:
            self.cache.move_to_end(id)
            return self.cache[id]
        return None
        
    def put(self, id: str, papers: Dict[str, Dict[str, Any]]) -> None:
        self.cache[id] = papers
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
        self.cache.move_to_end(id)

# simplify topic names for the Semantic Scholar API
topics = {
    "AI": "artificial+intelligence",
    "AR": "hardware+architecture",
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
    "GR": "graphics",
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