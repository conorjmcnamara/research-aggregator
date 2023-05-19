# NLP Research Aggregator
A natural language processing (NLP)-driven web app that aggregates and displays computer science research papers from multiple scholarly sources. A mulit-label text classification model, trained with Keras, tags papers by topic areas. 

The web app features a TypeScript React frontend and Flask backend REST API with MongoDB that supports user authentication and CRUD operations on users and bookmarks.

## Installation

### Prerequisites

- Python - [install](https://www.python.org/)
- Node.js and npm - [install](https://nodejs.org/)

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

Execute the following commands where appropriate:

```bash
# 1. generate training dataset
$ cd api/model && python -m scraper

# 2. train model
$ cd api/model && python -m train

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
$ cd api/tests && pytest -v

# run frontend tests
$ npm run test
```

## Multi-label Text Classification

Given that the application aggregates data from multple scholarly sources, a model was needed to standardise topic area classification. Using Keras, a feedforward neural network was trained on >143K research paper abstracts across 39 classes. Unseen abstracts can be passed into the model, and it will predict one or more topic area labels for each.

### Dataset Analysis

The training dataset is generated and compressed by running the multi-threaded ```scraper.py``` program, which aggregates research paper abstracts and their respective topic area tags from arXiv.org

![Distribution of Individual Class Counts](api/model/plots/individual_class_counts.png)

The plot above illustrates class imbalance in the dataset, meaning classes such as LG (machine learning) are overrepresented. To handle this, class weights were computed based off their frequencies and then integrated during training, which gives more importance to underrepresented classes.

### Model Architecture

The model is a sequential neural network starting with a text vectorization preprocessing layer that standardises text (lowercase + punctuation stripping), splits the result into substrings and applies tokenization and indexing before converting the text into a numerical vector.

There are 3 hidden dense layers, each with 100 neurons and the ReLU activation function, which introduces non-linearity to help identify patterns in the text. Between each of these is a dropout layer with a rate of 0.3 to mitigate overfitting by randomly setting output features of the layer to 0. The final layer has the same number of neurons as the number of classes and uses the sigmoid activation function, which estimates probabilities for each label.

The model is compiled using the binary crossentropy loss function, which measures dissimilarity between the predicted probabilities and true labels. The Adam optimiser determines how the model's weights are updated during training in order to minimise the loss function. The output of the model is a probability distribution over all labels.

### Model Evaluation

The dataset was split into 70% training data, 15% validation data and 15% testing data.

The following metrics were monitored during training:
- **Binary Accuracy**: percentage of correct predictions over all predictions, where each label is treated as an independent binary classification problem.
- **Precision**: percentage of correct positive predictions over all positive predictions. Low precision indicates a high number of false positives.
- **Recall**: percentage of correct positive predictions over all actual positive data points. Low recall indicates a high number of false negatives.

#### Binary Accuracy
![Training and Validation Binary Accuracy](api/model/plots/training_and_validation_binary_accuracy.png)

The graph above shows a relatively high binary accuracy for both the training and validation datasets. However, since the dataset is imbalanced binary accuracy may not be a suitable metric. The binary accuracy on the evaluated test dataset was 97%.

#### Confusion Matrix
![Confusion Matrix](api/model/plots/confusion_matrix.png)

The above matrix is formatted as follows:

[True Negatives (TN), False Positives (FP)]

[False Negatives (FN), True Positives (TP)]

A confusion matrix represents the model's performance on unseen data. It visualises how many labels were correctly and incorrectly predicted. The above plot is the aggregated confusion matrix for each class, it uses a threshold of 0.5 on the probability distribution and is based off the test dataset. It has more TP than FP and more TN than FN, which is generally considered good peformance.

Summary metrics obtained on the test dataset include:
- Binary Accuracy: 97%
- Precision: 80%
- Recall: 47%
- Loss: 9%