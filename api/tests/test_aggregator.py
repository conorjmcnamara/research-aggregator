import json
from ..aggregator import parse_arxiv, Node, parse_semantic_scholar

FIELDS = ["title", "date", "abstract", "url", "source", "authors", "topics"]

def test_parse_arxiv():
    with open("tests/arxiv_mock.json") as file:
        data = json.load(file)
    papers = parse_arxiv(data, "AI")
    assert len(papers) == 2
    assert len(papers[0]) == len(FIELDS)
    for field in FIELDS:
        assert papers[0][field] != None
    assert papers[0]["source"] == "arXiv.org"
    assert len(papers[0]["topics"]) == 3
    assert len(papers[0]["authors"]) == 3
    assert len(papers[1]["authors"]) == 1

def test_node():
    node = Node("2023-02-25", 1)
    assert node.date == "2023-02-25"
    assert node.json_index == 1

def test_parse_semantic_scholar():
    with open("tests/semantic_scholar_mock.json") as file:
        data = json.load(file)
    papers = parse_semantic_scholar(data, "AI")
    assert len(papers) == 2
    assert len(papers[0]) == len(FIELDS)
    for field in FIELDS:
        assert papers[0][field] != None
    assert papers[0]["source"] == "SemanticScholar.org"
    assert len(papers[0]["authors"]) == 2
    assert len(papers[1]["authors"]) == 3