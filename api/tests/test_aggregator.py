import json
import requests
import xmltodict
import pytest_mock
import sys
sys.path.append("..")
from aggregator import fetch_arxiv, parse_arxiv, fetch_semantic_scholar, parse_semantic_scholar

PAPER_FIELDS = ["title", "date", "abstract", "url", "source", "authors", "topics"]

def test_parse_arxiv():
    with open("mocks/arxiv_api_mock.xml", "r") as file:
        json_data = xmltodict.parse(file.read())

    papers = parse_arxiv(json_data, "AI")
    assert len(papers) == 2
    assert len(papers[0]) == len(PAPER_FIELDS)
    for field in PAPER_FIELDS:
        assert papers[0][field] != None
    assert papers[0]["source"] == "arXiv.org"
    assert len(papers[0]["topics"]) == 3
    assert len(papers[0]["authors"]) == 6

def test_fetch_arxiv(mocker: pytest_mock.MockerFixture):
    with open("mocks/arxiv_api_mock.xml", "r") as file:
        xml_data = file.read()

    session = requests.Session()
    mocker.patch.object(session, "get")
    session.get.return_value.text = xml_data
    assert fetch_arxiv(session, "AI") == parse_arxiv(xmltodict.parse(xml_data), "AI")

    session.get.side_effect = Exception("Mocked exception")
    assert fetch_arxiv(session, "AI") == None

def test_parse_semantic_scholar():
    with open("mocks/semantic_scholar_api_mock.json") as file:
        json_data = json.load(file)

    papers, abstracts = parse_semantic_scholar(json_data, "AI")
    assert len(papers) == 2
    assert len(abstracts) == 2
    assert len(papers[0]) == len(PAPER_FIELDS)
    for field in PAPER_FIELDS:
        assert papers[0][field] != None
    assert papers[0]["source"] == "SemanticScholar.org"
    assert len(papers[0]["authors"]) == 3
    
def test_fetch_semantic_scholar(mocker: pytest_mock.MockFixture):
    with open("mocks/semantic_scholar_api_mock.json") as file:
        json_data = json.load(file)

    session = requests.Session()
    mocker.patch.object(session, "get")
    session.get.json.return_value = json_data
    assert fetch_semantic_scholar(session, "AI", "artificial+intelligence") == parse_semantic_scholar(json_data, "AI")

    session.get.side_effect = Exception("Mocked exception")
    assert fetch_semantic_scholar(session, "AI", "artificial+intelligence") == None