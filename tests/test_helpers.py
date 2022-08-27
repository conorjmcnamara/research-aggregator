import urllib.request, urllib.error
import helpers


# check the HTTP status codes of valid and invalid arXiv.org API query URLs
def test_create_query():
    # valid queries:
    def valid_query(topic):
        query_url = helpers.create_query(topic)
        response = urllib.request.urlopen(query_url)
        assert response.code == 200
    valid_query('AI')
    
    # invalid queries:
    def invalid_query(topic):
        query_url = helpers.create_query(topic) + 'test'
        try:
            urllib.request.urlopen(query_url)
            assert False
        except urllib.error.HTTPError:
            assert True
    invalid_query('AI')


# check whether valid and invalid topics return data from arXiv.org
def test_fetch_data():
    # valid topics:
    def valid_topic(topic):
        query_url = helpers.create_query(topic)
        api_data = helpers.fetch_data(topic, query_url)
        assert api_data
    valid_topic('DB')
    
    # invalid topics:
    def invalid_topic(topic):
        query_url = helpers.create_query(topic)
        api_data = helpers.fetch_data(topic, query_url)
        assert not api_data
    invalid_topic('DB_')


# check that logs are written to the output.log file
def test_custom_logger():
    logger = helpers.custom_logger(__name__, 'a')
    log_message = 'test log'
    logger.info(log_message)

    # read the contents of the outlog.log file
    file = open('./log/output.log', 'r')
    file_contents = file.read()

    if log_message in file_contents:
        assert True
    else:
        assert False
    file.close()
    open('./log/output.log', 'w').close()