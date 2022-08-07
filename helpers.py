import urllib.request
import feedparser
import logging


# function that creates an arXiv.org API query URL for a passed topic
def create_query(topic):
    base_url = 'http://export.arxiv.org/api/query?'
    parameters = 'sortBy=submittedDate&max_results'
    max_results = 10

    # append the search parameters onto the base URL
    query_url = f"{base_url}search_query=cat:cs.{topic}&{parameters}={str(max_results)}"
    return fetch_data(topic, query_url)


# function that calls the arXiv.org API and returns the response
def fetch_data(topic, query_url):
    response = urllib.request.urlopen(query_url)
    if response:
        logger.info(f"Successfully fetched data for the {topic} topic.")
        api_data = feedparser.parse(response)
        return api_data.entries

    else:
        logger.error(f"Error fetching data for the {topic} topic.")


# function to create a custom logger
def custom_logger(name, mode):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] - %(message)s')

    file_handler = logging.FileHandler('./log/output.log', mode=mode)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


# keys to be rendered on template buttons
topic_keys = ['Artificial Intelligence', 'Hardware Architecture', 'Computational Complexity', 'Computational Engineering, Finance, and Science', 
              'Computational Geometry', 'Computation and Language', 'Cryptography and Security', 'Computer Vision and Pattern Recognition', 
              'Computers and Society', 'Databases', 'Distributed, Parallel, and Cluster Computing', 'Digital Libraries', 'Discrete Mathematics', 
              'Data Structures and Algorithms', 'Emerging Technologies', 'Formal Languages and Automata Theory', 'General Literature',
              'Graphics', 'Computer Science and Game Theory', 'Human-Computer Interaction', 'Information Retrieval', 'Information Theory',
              'Machine Learning', 'Logic in Computer Science', 'Multiagent Systems', 'Multimedia', 'Mathematical Software',
              'Numerical Analysis', 'Neural and Evolutionary Computing', 'Networking and Internet Architecture', 'Other Computer Science',
              'Operating Systems', 'Performance', 'Programming Languages', 'Robotics', 'Symbolic Computation', 'Sound', 'Software Engineering',
              'Social and Information Networks', 'Systems and Control']

# values for fetching data by topic
topic_values = ['AI', 'AR', 'CC', 'CE', 'CG', 'CL', 'CR', 'CV', 'CY', 'DB', 'DC', 'DL', 'DM', 'DS', 'ET', 'FL', 'GL', 'GR', 'GT', 'HC', 'IR',
                'IT', 'LG', 'LO', 'MA', 'MM', 'MS', 'NA', 'NE', 'NI', 'OH', 'OS', 'PF', 'PL', 'RO', 'SC', 'SD', 'SE', 'SI', 'SY']

topic_dictionary = {}
for i in range(len(topic_keys)):
    topic_dictionary[topic_keys[i]] = topic_values[i]

logger = custom_logger(__name__, 'w')