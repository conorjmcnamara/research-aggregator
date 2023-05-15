import logging
import requests
import heapq
import xmltodict
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, wait
from collections import defaultdict
from typing import Optional, List, DefaultDict, Dict, Tuple, Any
from utils import get_db_connection, upload_db_data, topics
from model.predict import load_model, predict

MAX_PAPERS_REQUEST = 25
seen_arxiv_papers = set()
seen_semantic_scholar_papers = set()

def parse_arxiv(data: Dict[str, Any], id: str) -> List[DefaultDict[str, list]]:
    result = []
    for entry in data["feed"]["entry"]:
        if not entry["id"] or entry["id"] in seen_arxiv_papers:
            continue
        paper = defaultdict(list)
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
        
        paper_topics = []
        for paper_id in entry["category"]:
            if type(paper_id) == str:
                continue
            if paper_id["@term"][3:] in topics:
                paper_topics.append(paper_id["@term"][3:])
        
        if not paper_topics:
            paper_topics.append(id)
        paper["topics"] = paper_topics
        result.append(paper)
        seen_arxiv_papers.add(entry["id"])
    return result

def fetch_arxiv(id: str, session: requests.Session) -> Optional[List[DefaultDict[str, list]]]:
    base_url = "http://export.arxiv.org/api/query?"
    param = "sortBy=submittedDate&max_results"
    url = f"{base_url}search_query=cat:cs.{id}&{param}={MAX_PAPERS_REQUEST}"
    try:
        response = session.get(url)
        data = xmltodict.parse(response.text)
    except Exception as e:
        logging.critical(f"Failed to make a GET request to arXiv with topic ID: {id}. Error: {e}")
        return None
    else:
        return parse_arxiv(data, id)

# node used for Semantic Scholar parsing
class Node:
    def __init__(self, date: str, json_index: int):
        self.date = date
        self.json_index = json_index

def parse_semantic_scholar(data: List[Dict[str, Any]], id: str) -> Tuple[List[DefaultDict[str, list]], List[str]]:
    heap = []
    size = 0

    # maintain a heap of the most recent research papers by date
    for i in range(len(data)):
        date = data[i]["publicationDate"]
        if not date or not data[i]["abstract"] or data[i]["paperId"] in seen_semantic_scholar_papers:
            continue
        if size < MAX_PAPERS_REQUEST:
            node = Node(date, i)
            heapq.heappush(heap, (i, node))
        else:
            if date > heap[0][1].date:
                node = Node(date, i)
                heapq.heappop(heap)
                heapq.heappush(heap, (i, node))
        size += 1
        seen_semantic_scholar_papers.add(data[i]["paperId"])

    result = []
    abstracts = []
    for entry in heap:
        json = data[entry[0]]
        paper = defaultdict(list)
        paper["title"] = json["title"]
        paper["date"] = json["publicationDate"]
        paper["abstract"] = json["abstract"]
        paper["url"] = json["url"]
        paper["source"] = "SemanticScholar.org"

        authors = []
        for author in json["authors"]:
            authors.append(author["name"])
        paper["authors"] = authors
        paper["topics"] = [id]
        result.append(paper)
        abstracts.append(paper["abstract"])
    return (result, abstracts)

def fetch_semantic_scholar(id: str, name: str, session: requests.Session) -> Optional[List[DefaultDict[str, list]]]:
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search?query="
    param = "&year=2023&fieldsOfStudy=Computer+Science&fields=title,url,abstract,publicationDate,authors&limit=20"
    url = f"{base_url}{name}{param}"
    try:
        response = session.get(url)
        data = response.json()["data"]
    except Exception as e:
        logging.critical(f"Failed to make a GET request to Semantic Scholar with topic ID: {id}. Error: {e}")
        return None
    else:
        return parse_semantic_scholar(data, id)

if __name__ == "__main__":
    # create a pool of threads and a session object for persistent HTTP connections
    session = requests.Session()
    executor = ThreadPoolExecutor(10)

    futures = []
    for id, name in topics.items():
        futures.append(executor.submit(fetch_arxiv, id, session))
        futures.append(executor.submit(fetch_semantic_scholar, id, name, session))
    session.close()
    wait(futures)
    
    papers = []
    model, lookup_layer = load_model()
    for i, future in enumerate(futures):
        if not future.result():
            continue
        if i % 2 == 0:
            for paper in future.result():
                papers.append(paper)
        # model prediction for Semantic Scholar
        else:
            data, abstracts = future.result()
            predicted_labels = predict(model, lookup_layer, abstracts)
            for i, labels in enumerate(predicted_labels):
                data[i]["topics"] = labels
                papers.append(data[i])
    
    load_dotenv()
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")
    papers_db = get_db_connection(user, password, "papers")
    upload_db_data(papers_db, papers)