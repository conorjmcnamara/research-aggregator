import urllib.request
import feedparser


# function that creates an arXiv.org API query URL for a passed category
def create_query(category):
        base_url = 'http://export.arxiv.org/api/query?'
        parameters = 'sortBy=submittedDate&max_results'
        max_results = 10

        # append the search parameters onto the base URL
        query_url = f"{base_url}search_query=cat:cs.{category}&{parameters}={str(max_results)}"
        return fetch_data(category, query_url)


# function that calls the arXiv.org API and returns the response
def fetch_data(category, query_url):
    response = urllib.request.urlopen(query_url)
    if response:
        print(f"Successfully fetched data for the {category} category.")
        data = feedparser.parse(response)
        return data.entries

    else:
        print(f"Error fetching data for the {category} category.")
