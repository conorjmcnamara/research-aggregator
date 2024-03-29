import pickle
import concurrent.futures
import pandas as pd
import tensorflow as tf
from keras import models, Sequential
from keras.layers import StringLookup
from typing import Tuple, List
from .preprocessor import normalize_text
from .constants import Constants

def load_model() -> Tuple[Sequential, StringLookup]:
    model = models.load_model(f"model/{Constants.MODEL_FILE}")
    with open(f"model/{Constants.CLASSES_FILE}", "rb") as file:
        classes = pickle.load(file)
    lookup_classes = StringLookup(vocabulary=classes, output_mode="multi_hot")
    return (model, lookup_classes)

def predict_labels(model: Sequential, lookup_classes: StringLookup, abstracts: List[str]) -> List[List[str]]:
    df = pd.DataFrame(abstracts, columns=["abstracts"])
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=Constants.NUM_PREPROCESSING_THREADS)
    df["abstracts"] = list(executor.map(lambda text: normalize_text(text), df["abstracts"]))
    executor.shutdown()

    dataset = tf.data.Dataset.from_tensor_slices(df["abstracts"].values)
    dataset = dataset.batch(Constants.BATCH_SIZE).prefetch(Constants.AUTO)

    predicted_probailities = model.predict(dataset)
    predicted_probailities = (predicted_probailities >= Constants.PREDICTION_THRESHOLD).astype(int)
    predicted_labels = []

    classes = lookup_classes.get_vocabulary()
    for individual_probailities in predicted_probailities:
        labels = []
        for i, prob in enumerate(individual_probailities):
            if prob == 1:
                labels.append(classes[i])
        predicted_labels.append(labels)
    return predicted_labels