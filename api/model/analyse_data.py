import os
import gzip
import pandas as pd
import matplotlib.pyplot as plt
from ast import literal_eval

def show_basic_info(df: pd.DataFrame) -> None:
    print(df.head())
    print(f"Rows: {len(df)}")
    print(f"Duplicate rows: {sum(df['abstracts'].duplicated())}")
    print(f"Classes: {df.explode('topics')['topics'].nunique()}")
    print(f"Rows with zero labels: {len(df[df['topics'].apply(len) == 0])}")

def plot_label_count_distribution(df: pd.DataFrame) -> None:
    # distribution of label counts per paper
    paper_counts = df["topics"].apply(len).value_counts()
    axis = paper_counts.plot(kind="bar")
    for i, count in enumerate(paper_counts):
        axis.text(i, count, str(count), ha="center", va="bottom")
    
    if not os.path.exists("plots"):
        os.mkdir("plots")

    plt.title("Distribution of Label Counts per Paper")
    plt.xlabel("Number of Labels")
    plt.ylabel("Count")
    plt.savefig("plots/label_counts_per_paper.png")
    plt.show()

    # distribution of individual class counts
    class_counts = df["topics"].explode().value_counts()
    axis = class_counts.plot(kind="bar", width=0.5)
    axis.tick_params(axis="x", labelsize=9)

    plt.title("Distribution of Individual Class Counts")
    plt.xlabel("Class")
    plt.ylabel("Count")
    plt.savefig("plots/individual_class_counts.png")
    plt.show()

def plot_words_per_abstract(df: pd.DataFrame) -> None:
    df["word_count"] = df["abstracts"].apply(lambda x: len(x.split()))
    word_count_freq = df["word_count"].value_counts().sort_index()
    plt.bar(word_count_freq.index, word_count_freq.values)
    plt.title("Distribution of Abstract Word Counts")
    plt.xlabel("Word Count")
    plt.ylabel("Abstract Count")
    plt.savefig("plots/abstract_word_counts.png")
    plt.show()

if __name__ == "__main__":
    # decompress the data
    with gzip.open("data/training_df.csv", "rt", encoding="utf-8") as file:
        df = pd.read_csv(file)

    # convert the labels to lists of strings
    df["topics"] = df["topics"].apply(literal_eval)
    show_basic_info(df)

    # remove duplicates from abstracts
    df = df[~df["abstracts"].duplicated()]

    plot_label_count_distribution(df)
    plot_words_per_abstract(df)