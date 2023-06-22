# NLP Research Aggregator
A natural language processing (NLP)-driven web app that aggregates and displays computer science research papers from multiple scholarly sources. A mulit-label text classification model, trained with Keras, tags papers by topic areas. 

The web app features a TypeScript React frontend and Flask backend REST API with MongoDB that supports user authentication and CRUD operations on users and bookmarks.

![NLP Research Aggregator GIF](assets/demo.gif)

## Installation

### Prerequisites

- Python
- Node.js and npm

```bash
# install backend dependencies
$ cd api && pip install -r requirements.txt

# install model depdendencies
$ cd api/model && pip install -r requirements.txt

# install frontend depdendencies
$ npm install
```

In the ```/api``` directory, remove the ```.example``` extension from the ```.env.example``` file and replace the variable values.

### Running the Application

```bash
# 1. generate training dataset
$ cd api && python -m model.scraper

# 2. train model
$ cd api && python -m model.train

# 3. aggregate database papers
$ cd api && python aggregator.py

# 4. start backend server
$ npm run api

# 5. start frontend server
$ npm start
```

### Testing

```bash
# run backend tests
$ cd api/tests && pytest -v --cov

# run frontend tests
$ npm run test
```

## Multi-label Text Classification

The application aggregates data from multiple scholarly sources, so a model is needed to standardize topic area classification. Using Keras, a neural network was trained on 141k research paper abstracts across 38 classes. Unseen abstracts can be passed into the model, and each will have one or more topic area labels predicted.