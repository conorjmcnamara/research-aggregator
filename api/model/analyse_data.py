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

def plot_num_labels_distribution(df: pd.DataFrame) -> None:
    num_labels = df["topics"].apply(len).value_counts()
    axis = num_labels.plot(kind="bar")
    for i, count in enumerate(num_labels):
        axis.text(i, count, str(count), ha="center", va="bottom")
    plt.title("Distribution of Number of Labels in Papers")
    plt.xlabel("Number of labels")
    plt.ylabel("Number of papers")
    plt.savefig("plots/num_labels_in_papers_distribution.png")
    plt.show()

def plot_class_instance_distribution(df: pd.DataFrame) -> None:
    class_instances = df["topics"].explode().value_counts()
    axis = class_instances.plot(kind="bar", width=0.5)
    axis.tick_params(axis="x", labelsize=9)
    plt.title("Distribution of Class Instances")
    plt.xlabel("Class ID")
    plt.ylabel("Number of instances")
    plt.savefig("plots/class_instance_distribution.png")
    plt.show()

def plot_abstract_length_distribution(df: pd.DataFrame) -> None:
    df["word_count"] = df["abstracts"].apply(lambda x: len(x.split()))
    word_count_freq = df["word_count"].value_counts().sort_index()
    plt.bar(word_count_freq.index, word_count_freq.values)
    plt.title("Distribution of Abstract Lengths")
    plt.xlabel("Length of abstract")
    plt.ylabel("Number of abstracts")
    plt.savefig("plots/abstract_length_distribution.png")
    plt.show()

if __name__ == "__main__":
    with gzip.open("data/training_data.csv", "rt", encoding="utf-8") as file:
        df = pd.read_csv(file)

    df["topics"] = df["topics"].apply(literal_eval)
    show_basic_info(df)
    df = df[~df["abstracts"].duplicated()]

    if not os.path.exists("plots"):
        os.mkdir("plots")

    plot_num_labels_distribution(df)
    plot_class_instance_distribution(df)
    plot_abstract_length_distribution(df)