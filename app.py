from flask import Flask, render_template, request
from helpers import create_query, fetch_data, topic_dictionary

# configure the application
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', topic_buttons=topic_dictionary)


@app.route('/result', methods=['POST', 'GET'])
def result():
    # request the computer science topic from the template form submission
    output = request.form.to_dict()
    topic = output['topic']
    
    # make an API call with the selected topic
    query_url = create_query(topic)
    api_data = fetch_data(topic, query_url)
    return render_template('index.html', topic_buttons=topic_dictionary, research_data=api_data)


if __name__ == '__main__':
    app.run(debug=True)