import re
import concurrent.futures
import nltk
import numpy as np
import pandas as pd
import tensorflow as tf
from keras.layers import StringLookup, TextVectorization
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
from nltk.corpus import stopwords
from ast import literal_eval
from typing import Tuple, Dict
from .constants import Constants

nltk.download("stopwords")
STOP_WORDS = set(stopwords.words("english"))
AUTO = tf.data.AUTOTUNE

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\n", r" ", text)
    text = remove_urls_and_latex(text)
    text = remove_non_alpha(text)
    text = remove_stop_words(text)
    text = remove_extra_spaces(text)
    return text

def remove_urls_and_latex(text: str) -> str:
    latex_regex = r"\$.*?\$"
    url_regex = r"(http[s]?://|www\.)\S+"
    text = re.sub(latex_regex, "", text)
    text = re.sub(url_regex, "", text)
    return text

def remove_non_alpha(text: str) -> str:
    return re.sub(r"[^a-z A-Z]+", " ", text)

def remove_stop_words(text: str) -> str:
    words = text.split()
    return " ".join(word for word in words if word not in STOP_WORDS)

def remove_extra_spaces(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def multi_label_binarization(df: pd.DataFrame) -> StringLookup:
    # create a dictionary-like object with labels and their respective binary vector representations
    classes = tf.ragged.constant(df["topics"].values)
    lookup_classes = StringLookup(output_mode="multi_hot")
    lookup_classes.adapt(classes)
    return lookup_classes

def get_class_weights(df: pd.DataFrame, lookup_classes: StringLookup) -> Dict[int, float]:
    # compute class weights to handle class imbalance during model training
    # low weights reduce impact during training compared to higher weights
    classes = [x for x in lookup_classes.get_vocabulary() if x != "[UNK]"]
    class_instances = np.concatenate(df["topics"].values)
    class_weights = class_weight.compute_class_weight(class_weight="balanced", classes=classes, y=class_instances)
    result = {0: 0}
    for i in range(len(classes)):
        result[i+1] = class_weights[i]
    return result

def split_data(df: pd.DataFrame) -> Tuple[pd.DataFrame]:
    train_df, test_df = train_test_split(df, test_size=0.3, shuffle=True, random_state=42)
    # generate a random validation dataset from the test dataset
    validation_df = test_df.sample(frac=0.5)
    test_df.drop(validation_df.index, inplace=True)
    return (train_df, validation_df, test_df)

def get_tf_dataset(df: pd.DataFrame, lookup_classes: StringLookup) -> tf.data.Dataset:
    classes = tf.ragged.constant(df["topics"].values)
    classes_binarized = lookup_classes(classes)
    dataset = tf.data.Dataset.from_tensor_slices((df["abstracts"].values, classes_binarized))
    return dataset.batch(Constants.BATCH_SIZE).prefetch(AUTO)

def get_tfidf_vectorizer(train_df: pd.DataFrame) -> TextVectorization:
    tokens = set()
    train_df["abstracts"].str.split().apply(tokens.update)

    # object to convert text into a vector using TF-IDF weighting
    text_vectorizer = TextVectorization(max_tokens=len(tokens), split="whitespace", ngrams=2, output_mode="tf_idf")

    # create a vocabulary by tokenizing text into distinct terms, counting their occurrences and assigning indicies
    text_vectorizer.adapt(train_df["abstracts"])
    return text_vectorizer

def preprocess_data(df: pd.DataFrame) -> Tuple[StringLookup, TextVectorization, Dict[str, tf.data.Dataset]]:
    # remove duplicates
    df = df[~df["abstracts"].duplicated()]

    # convert the labels to lists of strings
    df["topics"] = df["topics"].apply(literal_eval)

    # multi-threaded abstract text cleaning
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=Constants.NUM_PREPROCESSING_THREADS)
    df["abstracts"] = list(executor.map(lambda text: normalize_text(text), df["abstracts"]))
    executor.shutdown()

    lookup_classes = multi_label_binarization(df)
    class_weights = get_class_weights(df, lookup_classes)

    train_df, validation_df, test_df = split_data(df)
    train_dataset = get_tf_dataset(train_df, lookup_classes)
    validation_dataset = get_tf_dataset(validation_df, lookup_classes)
    test_dataset = get_tf_dataset(test_df, lookup_classes)

    # vectorize the datasets
    text_vectorizer = get_tfidf_vectorizer(train_df)
    train_dataset = train_dataset.map(
        lambda text, labels: (text_vectorizer(text), labels), num_parallel_calls=AUTO
    ).prefetch(AUTO)

    validation_dataset = validation_dataset.map(
        lambda text, labels: (text_vectorizer(text), labels), num_parallel_calls=AUTO
    ).prefetch(AUTO)

    test_dataset = test_dataset.map(
        lambda text, labels: (text_vectorizer(text), labels), num_parallel_calls=AUTO
    ).prefetch(AUTO)

    datasets = {"train": train_dataset, "validation": validation_dataset, "test": test_dataset}
    print("Preprocessing successfully completed")
    return (lookup_classes, text_vectorizer, class_weights, datasets)