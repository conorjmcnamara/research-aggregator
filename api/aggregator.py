import logging
import requests
import heapq
import xmltodict
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from typing import Optional
from utils import get_db_connection, upload_db_data, topics

MAX_PAPERS_REQUEST = 10

def fetch_arxiv(id: str, session: requests.Session) -> Optional[list]:
    base_url = "http://export.arxiv.org/api/query?"
    param = "sortBy=submittedDate&max_results"
    url = f"{base_url}search_query=cat:cs.{id}&{param}={MAX_PAPERS_REQUEST}"

    try:
        response = session.get(url)
        data = xmltodict.parse(response.text)
    except:
        logging.critical(f"Failed to make a GET request to arXiv with topic ID: {id}. HTTP code {response.status_code}")
        return None
    else:
        result = []
        for entry in data["feed"]["entry"]:
            paper = defaultdict(list)
            paper["topic"] = id
            paper["title"] = entry["title"]
            paper["date"] = entry["updated"][:10]
            paper["abstract"] = entry["summary"]
            paper["url"] = entry["id"]
            paper["source"] = "arXiv.org"

            authors = []
            if len(entry["author"]) == 1:
                authors.append(entry["author"]["name"])
            else:
                for author in entry["author"]:
                    if len(author) == 1:
                        authors.append(author["name"])
            paper["authors"] = authors
            result.append(paper)
        logging.info(f"Successfully made a GET request to arXiv with topic ID: {id}. HTTP code {response.status_code}")
        return result

# node used for Semantic Scholar parsing
class Node:
    def __init__(self, date: str, json_index: int):
        self.date = date
        self.json_index = json_index

def fetch_semantic_scholar(id: str, name: str, session: requests.Session) -> Optional[list]:
    if id == "OH":
        return None
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search?query="
    param = "&year=2023&fieldsOfStudy=Computer+Science&fields=title,url,abstract,publicationDate,authors&limit=20"
    url = f"{base_url}{name}{param}"

    try:
        response = session.get(url)
        data = response.json()["data"]
    except:
        logging.critical(f"Failed to make a GET request to Semantic Scholar with topic name: {name}. HTTP code {response.status_code}")
        return None
    else:
        heap = []
        size = 0

        # maintain a heap of the most recent research papers by date
        for i in range(len(data)):
            date = data[i]["publicationDate"]
            if not date:
                continue
            if size < MAX_PAPERS_REQUEST:
                node = Node(i, date)
                heapq.heappush(heap, (i, node))
            else:
                if date > heap[0][1].date:
                    node = Node(i, date)
                    heapq.heappop(heap)
                    heapq.heappush(heap, (i, node))
            size += 1
        
        result = []
        for entry in heap:
            json = data[entry[0]]
            paper = defaultdict(list)
            paper["topic"] = id
            paper["title"] = json["title"]
            paper["date"] = json["publicationDate"]
            paper["abstract"] = json["abstract"]
            paper["url"] = json["url"]
            paper["source"] = "SemanticScholar.org"

            authors = []
            for author in json["authors"]:
                authors.append(author["name"])
            paper["authors"] = authors
            result.append(paper)
        logging.info(f"Successfully made a GET request to Semantic Scholar with topic name: {name}. HTTP code {response.status_code}")
        return result

if __name__ == "__main__":
    # create a pool of threads and a session object for persistent HTTP connections
    session = requests.Session()
    executor = ThreadPoolExecutor(10)

    futures = []
    for id, name in topics.items():
        futures.append(executor.submit(fetch_arxiv, id, session))
        futures.append(executor.submit(fetch_semantic_scholar, id, name, session))
    session.close()
    
    papers = []
    for future in futures:
        if future.result():
            for paper in future.result():
                papers.append(paper)
    
    load_dotenv()
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")
    papers_db = get_db_connection(user, password, "papers")
    upload_db_data(papers_db, papers)