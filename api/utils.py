import logging
import os
import pymongo
from dotenv import load_dotenv
from typing import Optional

# function to create a MongoDB Atlas connection
def get_db(user: str, password: str, collection: str) -> Optional[pymongo.collection.Collection]:
    connection = f"mongodb+srv://{user}:{password}@research.holkbao.mongodb.net/?retryWrites=true&w=majority"
    try:
        client = pymongo.MongoClient(connection)
        logging.info("Connected to MongoDB Atlas")
        return client["research"][collection]
    except:
        logging.critical("Failed to connect to MongoDB Atlas")
        return None

# function to upload data to MongoDB Atlas
def upload_data(db: pymongo.collection.Collection, papers: list) -> bool:
    try:
        db.delete_many({})
        db.insert_many(papers)
        logging.info("Successfully updated the MongoDB Atlas database")
        return True
    except:
        logging.critical("Failed to update the MongoDB Atlas database")
        return False

# read environment variables
load_dotenv()
user = os.getenv("USER")
password = os.getenv("PASSWORD")
db = get_db(user, password, "papers")

# remove unnecessary grammar from the topic names for the Semantic Scholar API
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