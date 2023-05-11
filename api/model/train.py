import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from keras import Sequential, metrics
from keras.layers import StringLookup, Dense, Dropout, TextVectorization
from keras.callbacks import EarlyStopping, History
from keras.optimizers import Adam
from sklearn.metrics import multilabel_confusion_matrix
from preprocesser import preprocess_data
from constants import Constants

METRICS = [
    metrics.TruePositives(),
    metrics.FalsePositives(),
    metrics.TrueNegatives(),
    metrics.FalseNegatives(), 
    metrics.BinaryAccuracy(),
    metrics.Precision(),
    metrics.Recall(),
]

def create_model(lookup_layer: StringLookup) -> Sequential:
    # feed-forward neural network
    model = Sequential([
        Dense(150, activation="relu"),
        Dropout(0.2),
        Dense(150, activation="relu"),
        Dropout(0.2),
        Dense(150, activation="relu"),
        Dropout(0.2),
        Dense(lookup_layer.vocabulary_size(), activation="sigmoid")
    ])
    optimizer = Adam(learning_rate=0.001)
    model.compile(loss="binary_crossentropy", optimizer=optimizer, metrics=METRICS)
    return model

def fit_model(model: Sequential, class_weights: dict, train_dataset: tf.data.Dataset, validation_dataset: tf.data.Dataset) -> History:
    # implement early stopping to reduce overfitting
    early_stop = EarlyStopping(monitor="loss", patience=5)

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

def plot_confusion_matrix(model: Sequential, actual_probailities: np.ndarray, predicted_probailities: np.ndarray) -> None:
    # compute confusion matrix for each label seperately, sum up, and plot
    confusion_matrix = multilabel_confusion_matrix(actual_probailities, predicted_probailities)
    confusion_matrix = np.sum(confusion_matrix, axis=0)

    plt.imshow(confusion_matrix, cmap=plt.cm.Blues, interpolation="nearest")
    plt.colorbar()
    plt.xlabel("Predicted label")
    plt.ylabel("True label")
    plt.xticks([0, 1])
    plt.yticks([0, 1])
    for i in range(2):
        for j in range(2):
            color = "white" if confusion_matrix[i, j] > confusion_matrix.max() / 2 else "black"
            plt.text(j, i, format(confusion_matrix[i, j]), horizontalalignment="center", color=color)
    plt.title("Confusion matrix")

    if not os.path.exists("plots"): os.mkdir("plots")
    plt.savefig(f"plots/confusion_matrix.png")
    plt.show()

def plot_history(history: History, metric: str) -> None:
    plt.plot(history.history[metric], label=metric)
    plt.plot(history.history["val_" + metric], label="val_" + metric)
    plt.xlabel("Epochs")
    plt.ylabel(metric)
    plt.title(f"Train and Validation {metric} Over Epochs", fontsize=14)
    plt.legend()
    plt.grid()

    if not os.path.exists("plots"): os.mkdir("plots")
    plt.savefig(f"plots/train_validation_{metric}_over_epochs.png")
    plt.show()

if __name__ == "__main__":
    training_data = pd.read_csv("data/training_data.csv")
    lookup_layer, text_vectorizer, class_weights, datasets = preprocess_data(training_data)
    test_text, test_labels = next(iter(datasets["test"]))

    model = create_model(lookup_layer)
    history = fit_model(model, class_weights, datasets["train"], datasets["validation"])
    save_model(model, text_vectorizer, lookup_layer)
    evaluate_model(model, datasets["test"])

    predicted_probailities = predict(model, test_text)
    print(history)
    plot_history(history, "loss")
    plot_history(history, "binary_accuracy")
    plot_confusion_matrix(model, test_labels, predicted_probailities)