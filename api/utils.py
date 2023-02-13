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
    "AI": "Artificial Intelligence",
    "CL": "Computation and Language",
    "CC": "Computational Complexity",
    "CE": "Computational Engineering, Finance, and Science",
    "CG": "Computational Geometry",
    "CV": "Computer Vision and Pattern Recognition",
    "CY": "Computers and Society",
    "CR": "Cryptography and Security",
    "DS": "Data Structures and Algorithms",
    "DB": "Databases",
    "DL": "Digital Libraries",
    "DM": "Discrete Mathematics",
    "DC": "Distributed, Parallel, and Cluster Computing",
    "ET": "Emerging Technologies",
    "FL": "Formal Languages and Automata Theory",
    "GT": "Game Theory",
    "GL": "General Literature",
    "GR": "Graphics",
    "AR": "Hardware Architecture",
    "HC": "Human-Computer Interaction", 
    "IR": "Information Retrieval",
    "IT": "Information Theory",
    "LO": "Logic in Computer Science",
    "LG": "Machine Learning",
    "MS": "Mathematical Software",
    "MA": "Multiagent Systems",
    "MM": "Multimedia",
    "NI": "Networking and Internet Architecture",
    "NE": "Neural and Evolutionary Computing",
    "NA": "Numerical Analysis",
    "OS": "Operating Systems",
    "OH": "Other",
    "PF": "Performance",
    "PL": "Programming Languages",
    "RO": "Robotics",
    "SI": "Social and Information Networks",
    "SE": "Software Engineering",
    "SD": "Sound",
    "SC": "Symbolic Computation",
    "SY": "Systems and Control"
}