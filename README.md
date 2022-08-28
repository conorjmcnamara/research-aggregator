# Computer Science Research Aggregator

A Flask web application to access recent research papers by computer science topic using the arXiv.org API.

[![Computer Science Research Aggregator GIF](assets/sample.gif)](https://github.com/conorjmcnamara/research-aggregator)

## Installation

### Prerequisites
- Python 3 - [install](https://www.python.org/downloads/)

### Running the Application
Run the following commands:

```bash
# Clone the repository
$ git clone https://github.com/conorjmcnamara/research-aggregator.git

# Change directory
$ cd research-aggregator

# Install dependencies
$ pip install -r requirements.txt

# Start the development server
$ flask run
```

Open http://127.0.0.1:5000 to view it in the browser.

### Unit Testing
Run the following command from the ```research-aggregator``` directory:

```bash
# Start test session
$ python -m pytest tests -v
```

## Resources
- [Flask](https://palletsprojects.com/p/flask)
- [arXiv.org API](https://arxiv.org/help/api)