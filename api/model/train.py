import os
import pickle
import gzip
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from keras import Sequential, metrics
from keras.layers import StringLookup, Dense, Dropout, TextVectorization
from keras.callbacks import EarlyStopping, History
from sklearn.metrics import multilabel_confusion_matrix
from typing import Dict
from .preprocesser import preprocess_data
from .constants import Constants

METRICS = [
    metrics.TruePositives(),
    metrics.FalsePositives(),
    metrics.TrueNegatives(),
    metrics.FalseNegatives(), 
    metrics.BinaryAccuracy(),
    metrics.Precision(),
    metrics.Recall()
]

def get_model(lookup_layer: StringLookup) -> Sequential:
    # feedforward neural network
    model = Sequential([
        Dense(100, activation="relu"),
        Dropout(0.3),
        Dense(100, activation="relu"),
        Dropout(0.3),
        Dense(100, activation="relu"),
        Dropout(0.3),
        Dense(lookup_layer.vocabulary_size(), activation="sigmoid")
    ])
    model.compile(loss="binary_crossentropy", optimizer="adam", metrics=METRICS)
    return model

def fit_model(model: Sequential, class_weights: Dict[int, float], train_dataset: tf.data.Dataset, validation_dataset: tf.data.Dataset) -> History:
    # implement early stopping to reduce overfitting
    early_stop = EarlyStopping(monitor="loss", patience=3)

    # set class weights to handle class imbalance
    history = model.fit(train_dataset, validation_data=validation_dataset, epochs=Constants.EPOCHS,
                        class_weight=class_weights, callbacks=early_stop, verbose=2)
    return history

def save_model(model: Sequential, text_vectorizer_layer: TextVectorization, lookup_layer: StringLookup) -> None:
    model = Sequential([text_vectorizer_layer, model])
    model.summary()
    model.save(Constants.MODEL_FILE, overwrite=True)

    with open(Constants.VOCAB_FILE, "wb") as file:
        pickle.dump(lookup_layer.get_vocabulary(), file)
    file.close()

def evaluate_model(model: Sequential, dataset: tf.data.Dataset) -> None:
    test_metrics = model.evaluate(dataset)
    for name, value in zip(model.metrics_names, test_metrics):
        print("{}: {:.3f}".format(name, value))

def predict(model: Sequential, dataset: tf.data.Dataset) -> np.ndarray:
    predicted_probailities = model.predict(dataset)
    predicted_probailities = (predicted_probailities >= Constants.PREDICTION_THRESHOLD).astype(int)
    return predicted_probailities

def plot_metrics(history: History) -> None:
    if not os.path.exists("plots"):
        os.mkdir("plots")
    
    PLOT_METRICS = ["binary_accuracy", "precision", "recall", "loss"]
    for metric in PLOT_METRICS:
        name = metric.replace("_", " ").capitalize()
        plt.figure()
        plt.plot(history.epoch, history.history[metric], label="Training")
        plt.plot(history.epoch, history.history["val_" + metric], label="Validation")
        plt.xlabel("Epoch")
        plt.ylabel(name)
        plt.title(f"Training and Validation {name}")
        plt.legend()
        plt.savefig(f"plots/training_and_validation_{metric}.png")
        plt.show()

def plot_confusion_matrix(actual_probailities: np.ndarray, predicted_probailities: np.ndarray) -> None:
    # compute confusion matrix for each class seperately, sum up, and plot
    confusion_matrix = multilabel_confusion_matrix(actual_probailities, predicted_probailities)
    confusion_matrix = np.sum(confusion_matrix, axis=0)

    plt.figure()
    plt.imshow(confusion_matrix, cmap=plt.cm.Blues, interpolation="nearest")
    plt.colorbar()
    plt.xlabel("Predicted label")
    plt.ylabel("Actual label")
    plt.xticks([0, 1])
    plt.yticks([0, 1])
    for i in range(2):
        for j in range(2):
            color = "white" if confusion_matrix[i, j] > confusion_matrix.max() / 2 else "black"
            plt.text(j, i, format(confusion_matrix[i, j]), horizontalalignment="center", color=color)
    plt.title(f"Confusion matrix @ {Constants.PREDICTION_THRESHOLD}")

    if not os.path.exists("plots"):
        os.mkdir("plots")
    plt.savefig(f"plots/confusion_matrix.png")
    plt.show()

if __name__ == "__main__":
    # decompress the data
    with gzip.open("data/training_data.csv", "rt", encoding="utf-8") as file:
        training_data = pd.read_csv(file)
    lookup_layer, text_vectorizer, class_weights, datasets = preprocess_data(training_data)
    test_text, test_labels = next(iter(datasets["test"]))

    model = get_model(lookup_layer)
    history = fit_model(model, class_weights, datasets["train"], datasets["validation"])
    save_model(model, text_vectorizer, lookup_layer)

    evaluate_model(model, datasets["test"])
    predicted_probailities = predict(model, test_text)
    plot_metrics(history)
    plot_confusion_matrix(test_labels, predicted_probailities)