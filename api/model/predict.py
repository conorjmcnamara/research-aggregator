import pickle
import pandas as pd
import tensorflow as tf
from keras import models, Sequential
from keras.layers import StringLookup
from typing import Tuple, List
from constants import Constants

def load_model() -> Tuple[Sequential, StringLookup]:
    model = models.load_model(Constants.MODEL_FILE)
    with open(Constants.VOCAB_FILE, "rb") as file:
        vocab = pickle.load(file)
    file.close()
    lookup_layer = StringLookup(vocabulary=vocab, output_mode="multi_hot")
    return (model, lookup_layer)

def get_tf_dataset(data: pd.DataFrame) -> tf.data.Dataset:
    dataset = tf.data.Dataset.from_tensor_slices(data["abstracts"].values)
    dataset = dataset.batch(Constants.BATCH_SIZE)
    return dataset

def predict(model, dataset: tf.data.Dataset, lookup_layer: StringLookup) -> List[str]:
    predicted_probailities = model.predict(dataset)
    predicted_probailities = (predicted_probailities >= Constants.PREDICTION_THRESHOLD).astype(int)
    predicted_labels = []
    vocab = lookup_layer.get_vocabulary()

    for i, prob in enumerate(predicted_probailities[0]):
        if prob == 1:
            predicted_labels.append(vocab[i])
    return predicted_labels

if __name__ == "__main__":
    model, lookup_layer = load_model()
    # data = [""]
    # df = pd.DataFrame(data, columns=["abstracts"])
    # dataset = get_tf_dataset(df)
    # predict(model, dataset, lookup_layer)