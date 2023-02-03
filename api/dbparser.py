import logging
import requests
import os
import xmltodict
import pymongo
from dotenv import load_dotenv
from collections import defaultdict
from typing import Optional

# constant num of research papers to request
MAX_RESULTS = "10"

# IDs for fetching data by topic
topic_id = ("AI", "CC", "CE", "CG", "CL", "CR", "CV", "CY", "DB", "DC", "DL", "DM", "DS", "ET", "FL", 
            "GL", "GR", "GT", "AR", "HC", "IR", "IT", "LG", "LO", "MA", "MM", "MS", "NA", "NE", "NI",
            "OH", "OS", "PF", "PL", "RO", "SC", "SD", "SE", "SI", "SY")

# function to create a MongoDB Atlas connection
def get_db(user: str, password: str) -> Optional[pymongo.collection.Collection]:
    connection = f"mongodb+srv://{user}:{password}@research.holkbao.mongodb.net/?retryWrites=true&w=majority"
    try:
        client = pymongo.MongoClient(connection)
        logging.info("Connected to MongoDB Atlas")
        return client["research"]["data"]
    except:
        logging.critical("Failed to connect to MongoDB Atlas")
        return None

# function to fetch arXiv.org data for a passed topic ID
def fetch_data(id: str) -> Optional[defaultdict]:
    if id not in topic_id:
        logging.critical("Invalid topic ID")
        return None
    else:
        base_url = "http://export.arxiv.org/api/query?"
        param = "sortBy=submittedDate&max_results"
        url = f"{base_url}search_query=cat:cs.{id}&{param}={MAX_RESULTS}"

        # HTTP GET request to arXiv.org API
        try:
            req = requests.get(url)
            try:
                data = xmltodict.parse(req.text)
            except:
                logging.critical("Failed to parse XML to dictionary")
                return None
        except:
            logging.critical(f"Failed to make a HTTP GET request with topic ID: {id}")
            return None
        else:
            result = defaultdict(list)
            result["topic"] = id

            # parse the raw data
            for entry in data["feed"]["entry"]:
                result["web_url"].append(entry["id"])
                result["date"].append(entry["updated"])
                result["title"].append(entry["title"])
                result["summary"].append(entry["summary"])
                
                # check for multiple authors
                authors = []
                if len(entry["author"]) == 1:
                    authors.append(entry["author"]["name"])
                else:
                    for person in entry["author"]:
                        if len(person) == 1:
                            authors.append(person["name"])
                
                result["authors"].append(authors)
                result["pdf_url"].append(entry["link"][1]["@href"])
            logging.info(f"Successfully made a HTTP GET request with topic ID: {id}")
            return result

# function to upload data to MongoDB Atlas
def upload_data(db: pymongo.collection.Collection, data: list) -> bool:
    try:
        db.delete_many({})
        db.insert_many(data)
        logging.info("Successfully updated the MongoDB Atlas database")
        return True
    except:
        logging.critical("Failed to update the MongoDB Atlas database")
        return False

# read environmental variables
load_dotenv()
user = os.getenv('USER')
password = os.getenv('PASSWORD')
db = get_db(user, password)

if __name__ == "__main__":
    # fetch data with each topic ID   
    topic_data = []
    for id in topic_id:
        topic_data.append(fetch_data(id))
    
    # batch upload to MongoDB Atlas
    upload_data(db, topic_data)