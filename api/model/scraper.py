import sys
sys.path.append("..")
import os
import requests
import xmltodict
import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from typing import Optional, List, DefaultDict, Dict, Any
from utils import topics

MAX_PAPERS_REQUEST = 5000
seen_papers = set()

def parse_arxiv(data: Dict[str, Any], id: str) -> List[DefaultDict[str, list]]:
    result = []
    for entry in data["feed"]["entry"]:
        if entry["id"] in seen_papers:
            continue
        paper = defaultdict(list)
        paper["abstract"] = entry["summary"]

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
        seen_papers.add(entry["id"])
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

if __name__ == "__main__":
    # create a pool of threads and a session object for persistent HTTP connections
    session = requests.Session()
    executor = ThreadPoolExecutor(10)

    futures = []
    for id, name in topics.items():
        futures.append(executor.submit(fetch_arxiv, id, session))
    session.close()
    
    all_abstracts = []
    all_topics = []
    for future in futures:
        if future.result():
            for paper in future.result():
                all_abstracts.append(paper["abstract"])
                all_topics.append(paper["topics"])

    data = pd.DataFrame({
        "abstracts": all_abstracts,
        "topics": all_topics
    })

    if not os.path.exists("data"):
        os.makedirs("data")
    data.to_csv("data/training_data.csv", index=False, mode="w")