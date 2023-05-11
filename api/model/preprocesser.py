import re
import numpy as np
import pandas as pd
import tensorflow as tf
from keras.layers import StringLookup, TextVectorization
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
from ast import literal_eval
from typing import Tuple, Dict
from constants import Constants

AUTO = tf.data.AUTOTUNE

def remove_substrings(text: str, latex_regex: str, url_regex: str) -> str:
    text = re.sub(latex_regex, "", text)
    text = re.sub(url_regex, "", text)
    return text

def split_data(data: pd.DataFrame) -> Tuple[pd.DataFrame]:
    train_df, test_df = train_test_split(data, test_size=0.2, shuffle=True)
    # generate a random validation dataset from the test dataset
    validation_df = test_df.sample(frac=0.5)
    test_df.drop(validation_df.index, inplace=True)
    return (train_df, validation_df, test_df)

def multi_label_binarization(data: pd.DataFrame) -> StringLookup:
    labels = tf.ragged.constant(data["topics"].values)
    lookup_layer = StringLookup(output_mode="multi_hot")
    lookup_layer.adapt(labels)
    return lookup_layer

def get_class_weights(data: pd.DataFrame, lookup_layer: StringLookup) -> Dict[int, float]:
    # compute class weights to handle class imbalance during model creation
    classes = [x for x in lookup_layer.get_vocabulary() if x != "[UNK]"]
    class_instances = np.concatenate(data["topics"].values)
    class_weights = class_weight.compute_class_weight(class_weight="balanced", classes=classes, y=class_instances)
    result = {0: 0}
    for i in range(len(classes)):
        result[i+1] = class_weights[i]
    return result

def create_tf_dataset(data: pd.DataFrame, lookup_layer: StringLookup) -> tf.data.Dataset:
    labels = tf.ragged.constant(data["topics"].values)
    labels_binarized = lookup_layer(labels).numpy()
    dataset = tf.data.Dataset.from_tensor_slices((data["abstracts"].values, labels_binarized))
    return dataset.batch(Constants.BATCH_SIZE).prefetch(AUTO)

def create_text_vectorizer(train_df: pd.DataFrame, train_dataset: tf.data.Dataset) -> TextVectorization:
    vocab = set()
    train_df["abstracts"].str.lower().str.split().apply(vocab.update)
    vocab_size = len(vocab)

    text_vectorizer = TextVectorization(
        max_tokens=vocab_size, ngrams=2, output_mode="tf_idf", standardize="lower_and_strip_punctuation"
    )
    text_vectorizer.adapt(train_dataset.map(lambda text, label: text))
    return text_vectorizer

def preprocess_data(data: pd.DataFrame) -> Tuple[StringLookup, TextVectorization, Dict[str, tf.data.Dataset]]:
    # remove duplicates
    data = data[~data["abstracts"].duplicated()]

    # convert the labels to lists of strings
    data["topics"] = data["topics"].apply(lambda x: literal_eval(x))

    # remove LaTex and URL substrings from abstracts
    latex_regex = r"\$.*?\$"
    url_regex = r"(http[s]?://|www\.)\S+"
    data["abstracts"] = data["abstracts"].apply(lambda x: remove_substrings(x, latex_regex, url_regex))

    train_df, validation_df, test_df = split_data(data)
    lookup_layer = multi_label_binarization(train_df)
    class_weights = get_class_weights(data, lookup_layer)

    train_dataset = create_tf_dataset(train_df, lookup_layer)
    validation_dataset = create_tf_dataset(validation_df, lookup_layer)
    test_dataset = create_tf_dataset(test_df, lookup_layer)

    text_vectorizer = create_text_vectorizer(train_df, train_dataset)
    train_dataset = train_dataset.map(
        lambda text, label: (text_vectorizer(text), label), num_parallel_calls=AUTO
    ).prefetch(AUTO)

    validation_dataset = validation_dataset.map(
        lambda text, label: (text_vectorizer(text), label), num_parallel_calls=AUTO
    ).prefetch(AUTO)

    test_dataset = test_dataset.map(
        lambda text, label: (text_vectorizer(text), label), num_parallel_calls=AUTO
    ).prefetch(AUTO)

    datasets = {"train": train_dataset, "validation": validation_dataset, "test": test_dataset}
    print("Preprocessing successfully completed")
    return (lookup_layer, text_vectorizer, class_weights, datasets)