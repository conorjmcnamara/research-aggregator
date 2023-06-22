import os
import pickle
import gzip
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from keras import Sequential, metrics, layers
from keras.callbacks import EarlyStopping, History
from sklearn.metrics import multilabel_confusion_matrix
from typing import Dict
from .preprocessor import preprocess_data
from .constants import Constants

def get_model(text_vectorizer: layers.TextVectorization, lookup_classes: layers.StringLookup) -> Sequential:
    model = Sequential([
        layers.Embedding(
            input_dim=text_vectorizer.vocabulary_size(),
            output_dim=Constants.EMBEDDING_VECTOR_LENGTH,
            input_length=Constants.VECTORIZER_SEQUENCE_LENGTH
        ),
        layers.Dropout(0.3),
        layers.GlobalAveragePooling1D(),
        layers.Dropout(0.3),
        layers.Dense(100, activation="relu"),
        layers.Dropout(0.3),
        layers.Dense(lookup_classes.vocabulary_size(), activation="sigmoid")
    ])

    METRICS = [
        metrics.BinaryAccuracy(),
        metrics.Precision(),
        metrics.Recall(),
        metrics.F1Score(average="macro")
    ]
    model.compile(loss="binary_crossentropy", optimizer="adam", metrics=METRICS)
    model.summary()
    return model

def fit_model(model: Sequential, class_weights: Dict[int, float], train_dataset: tf.data.Dataset, validation_dataset: tf.data.Dataset) -> History:
    early_stop = EarlyStopping(monitor="recall", mode="max", patience=Constants.EARLY_STOP_PATIENCE)
    history = model.fit(
        train_dataset.shuffle(int(train_dataset.cardinality()/5)),
        validation_data=validation_dataset.shuffle(int(validation_dataset.cardinality()/5)),
        epochs=Constants.EPOCHS,
        class_weight=class_weights,
        callbacks=early_stop,
        verbose=2
    )
    return history

def save_model(model: Sequential, text_vectorizer: layers.TextVectorization, lookup_classes: layers.StringLookup) -> None:
    model = Sequential([text_vectorizer, model])
    model.save(Constants.MODEL_FILE, overwrite=True)

    with open(Constants.CLASSES_FILE, "wb") as file:
        pickle.dump(lookup_classes.get_vocabulary(), file)

def evaluate_model(model: Sequential, test_dataset: tf.data.Dataset) -> None:
    test_metrics = model.evaluate(test_dataset)
    for name, value in zip(model.metrics_names, test_metrics):
        print(f"{name}: {value:.3f}")

def predict(model: Sequential, dataset: tf.data.Dataset) -> np.ndarray:
    predicted_probailities = model.predict(dataset)
    predicted_probailities = (predicted_probailities >= Constants.PREDICTION_THRESHOLD).astype(int)
    return predicted_probailities

def plot_metrics(history: History) -> None:
    PLOT_METRICS = ["binary_accuracy", "precision", "recall", "f1_score", "loss"]
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
    plt.title(f"Confusion matrix @ {Constants.PREDICTION_THRESHOLD} Threshold")
    plt.savefig(f"plots/confusion_matrix.png")
    plt.show()

if __name__ == "__main__":
    with gzip.open("data/training_data.csv", "rt", encoding="utf-8") as file:
        df = pd.read_csv(file)

    lookup_classes, text_vectorizer, class_weights, datasets = preprocess_data(df)
    model = get_model(text_vectorizer, lookup_classes)
    history = fit_model(model, class_weights, datasets["train"], datasets["validation"])
    save_model(model, text_vectorizer, lookup_classes)
    evaluate_model(model, datasets["test"])
    
    test_text, test_labels = next(iter(datasets["test"]))
    predicted_probailities = predict(model, test_text)

    if not os.path.exists("plots"):
        os.mkdir("plots")

    plot_metrics(history)
    plot_confusion_matrix(test_labels, predicted_probailities)