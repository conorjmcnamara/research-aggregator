import logging
import requests
import os
import xmltodict
import pymongo
from dotenv import load_dotenv
from collections import defaultdict
from typing import Optional

# constant num of research papers to request from arXiv.org
MAX_RESULTS = 10

# IDs for fetching data by topic
topic_id = ("AI", "CC", "CE", "CG", "CL", "CR", "CV", "CY", "DB", "DC", "DL", "DM", "DS", "ET", "FL", 
            "GL", "GR", "GT", "AR", "HC", "IR", "IT", "LG", "LO", "MA", "MM", "MS", "NA", "NE", "NI",
            "OH", "OS", "PF", "PL", "RO", "SC", "SD", "SE", "SI", "SY")

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

# function to fetch arXiv.org data for a passed topic ID
def fetch_data(id: str) -> Optional[list]:
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
            # parse the raw data
            result = []
            for entry in data["feed"]["entry"]:
                paper = defaultdict(list)
                paper["topic"] = id
                paper["title"] = entry["title"]
                paper["date"] = entry["updated"]
                paper["summary"] = entry["summary"]
                paper["web_url"] = entry["id"]
                paper["pdf_url"] = entry["link"][1]["@href"]

                # check for multiple authors
                authors = []
                if len(entry["author"]) == 1:
                    authors.append(entry["author"]["name"])
                else:
                    for author in entry["author"]:
                        if len(author) == 1:
                            authors.append(author["name"])
                paper["authors"] = authors
                result.append(paper)
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

# read environment variables
load_dotenv()
user = os.getenv("USER")
password = os.getenv("PASSWORD")
db = get_db(user, password, "papers")

if __name__ == "__main__":
    # fetch data with each topic ID   
    topic_data = []
    for id in topic_id:
        for json_obj in fetch_data(id):
            topic_data.append(json_obj)

    # batch upload to MongoDB Atlas
    upload_data(db, topic_data)