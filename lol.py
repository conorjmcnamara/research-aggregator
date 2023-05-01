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
        return client["research"][collection]
    except:
        logging.critical("Failed to connect to MongoDB Atlas")
        return None

get_db_connection("hhisgsg", "jgodjj", "ggidg")