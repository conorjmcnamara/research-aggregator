import pickle
import pandas as pd
import tensorflow as tf
from keras import models, Sequential
from keras.layers import StringLookup
from typing import Tuple, List
from .preprocesser import remove_substrings
from .constants import Constants

def load_model() -> Tuple[Sequential, StringLookup]:
    model = models.load_model(f"model/{Constants.MODEL_FILE}")
    with open(f"model/{Constants.VOCAB_FILE}", "rb") as file:
        vocab = pickle.load(file)
    lookup_layer = StringLookup(vocabulary=vocab, output_mode="multi_hot")
    return (model, lookup_layer)

def get_tf_dataset(data: pd.DataFrame) -> tf.data.Dataset:
    dataset = tf.data.Dataset.from_tensor_slices(data["abstracts"].values)
    dataset = dataset.batch(Constants.BATCH_SIZE)
    return dataset

def predict(model: Sequential, lookup_layer: StringLookup, abstracts: List[str]) -> List[List[str]]:
    df = pd.DataFrame(abstracts, columns=["abstracts"])
    df["abstracts"] = df["abstracts"].apply(lambda x: remove_substrings(x))
    dataset = get_tf_dataset(df)

    predicted_probailities = model.predict(dataset)
    predicted_probailities = (predicted_probailities >= Constants.PREDICTION_THRESHOLD).astype(int)
    predicted_labels = []
    vocab = lookup_layer.get_vocabulary()

    for individual_probailities in predicted_probailities:
        labels = []
        for i, prob in enumerate(individual_probailities):
            if prob == 1:
                labels.append(vocab[i])
        predicted_labels.append(labels)
    return predicted_labels