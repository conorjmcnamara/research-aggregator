import logging
import requests
import heapq
import xmltodict
from concurrent.futures import ThreadPoolExecutor, wait
from collections import defaultdict
from typing import Optional, List, DefaultDict, Dict, Tuple, Any
from utils import get_env_var, get_db_connection, upload_db_data, topics
from model.predict import load_model, predict_labels

MAX_PAPERS_REQUEST = 25
NUM_THREADS = 10
LEN_YYYY_MM_DD = 10
seen_arxiv_papers = set()
seen_semantic_scholar_papers = set()

def fetch_arxiv(session: requests.Session, id: str) -> Optional[List[DefaultDict[str, list]]]:
    base_url = "http://export.arxiv.org/api/query?"
    param = "sortBy=submittedDate&max_results"
    url = f"{base_url}search_query=cat:cs.{id}&{param}={MAX_PAPERS_REQUEST}"
    try:
        response = session.get(url)
        json_data = xmltodict.parse(response.text)
    except Exception as error:
        logging.critical(f"Failed to make a GET request to arXiv with topic ID: {id}. Error: {error}")
        return None
    else:
        return parse_arxiv(json_data, id)

def parse_arxiv(json_data: Dict[str, Any], id: str) -> List[DefaultDict[str, list]]:
    result = []
    for entry in json_data["feed"]["entry"]:
        if not entry["id"] or entry["id"] in seen_arxiv_papers:
            continue
        paper = defaultdict(list)
        paper["title"] = entry["title"]
        paper["date"] = entry["published"][:LEN_YYYY_MM_DD]
        paper["abstract"] = entry["summary"]
        paper["url"] = entry["id"]
        paper["source"] = "arXiv.org"

        authors = []
        for author in entry["author"]:
            if len(author) == 1:
                authors.append(author["name"])
        paper["authors"] = authors
        
        paper_topics = []
        for paper_id in entry["category"]:
            if type(paper_id) == str:
                continue
            elif paper_id["@term"][3:] in topics:
                paper_topics.append(paper_id["@term"][3:])
        
        if not paper_topics:
            paper_topics.append(id)
        paper["topics"] = paper_topics
        result.append(paper)
        seen_arxiv_papers.add(entry["id"])
    return result

def fetch_semantic_scholar(session: requests.Session, id: str, name: str) -> Optional[Tuple[List[DefaultDict[str, list]], List[str]]]:
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search?query="
    param = "&year=2023&fieldsOfStudy=Computer+Science&fields=title,url,abstract,publicationDate,authors"
    url = f"{base_url}{name}{param}&limit={MAX_PAPERS_REQUEST+50}"
    try:
        response = session.get(url)
        data = response.json()["data"]
    except Exception as error:
        logging.critical(f"Failed to make a GET request to Semantic Scholar with topic ID: {id}. Error: {error}")
        return None
    else:
        return parse_semantic_scholar(data, id)

def parse_semantic_scholar(json_data: List[Dict[str, Any]], id: str) -> Tuple[List[DefaultDict[str, list]], List[str]]:
    min_heap = []
    size = 0

    # maintain a min heap of the most recent research papers by date
    for i in range(len(json_data)):
        date = json_data[i]["publicationDate"]
        if not date or not json_data[i]["abstract"] or json_data[i]["paperId"] in seen_semantic_scholar_papers:
            continue
        if size < MAX_PAPERS_REQUEST:
            heapq.heappush(min_heap, (date, i))
        else:
            if date > min_heap[0][0]:
                heapq.heappop(min_heap)
                heapq.heappush(min_heap, (date, i))
        size += 1
        seen_semantic_scholar_papers.add(json_data[i]["paperId"])

    result = []
    abstracts = []
    for entry in min_heap:
        json = json_data[entry[1]]
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

if __name__ == "__main__":
    session = requests.Session()
    executor = ThreadPoolExecutor(NUM_THREADS)

    futures = []
    for id, name in topics.items():
        futures.append(executor.submit(fetch_arxiv, session, id))
        futures.append(executor.submit(fetch_semantic_scholar, session, id, name))
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
        else:
            # predict topic areas for Semantic Scholar abstracts
            data, abstracts = future.result()
            predicted_labels = predict_labels(model, lookup_layer, abstracts)
            for i, labels in enumerate(predicted_labels):
                data[i]["topics"] = labels
                papers.append(data[i])
    
    username, password = get_env_var()
    papers_db = get_db_connection(username, password, "papers")
    upload_db_data(papers_db, papers)