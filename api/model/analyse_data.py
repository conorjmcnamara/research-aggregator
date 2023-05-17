import os
import gzip
import pandas as pd
import matplotlib.pyplot as plt
from ast import literal_eval

def show_basic_info(data: pd.DataFrame) -> None:
    print(data.head())
    print(f"Rows: {len(data)}")
    print(f"Duplicate rows: {sum(data['abstracts'].duplicated())}")
    print(f"Classes: {data.explode('topics')['topics'].nunique()}")
    print(f"Rows with zero labels: {len(data[data['topics'].apply(len) == 0])}")

def plot_label_count_distribution(data: pd.DataFrame) -> None:
    # distribution of label counts per paper
    paper_counts = data["topics"].apply(len).value_counts()
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
    class_counts = data["topics"].explode().value_counts()
    axis = class_counts.plot(kind="bar", width=0.5)
    axis.tick_params(axis="x", labelsize=9)

    plt.title("Distribution of Individual Class Counts")
    plt.xlabel("Class")
    plt.ylabel("Count")
    plt.savefig("plots/individual_class_counts.png")
    plt.show()

if __name__ == "__main__":
    # decompress the data
    with gzip.open("data/training_data.csv", "rt", encoding="utf-8") as file:
        training_data = pd.read_csv(file)
    # convert the labels to lists of strings
    training_data["topics"] = training_data["topics"].apply(lambda id: literal_eval(id))
    show_basic_info(training_data)
    plot_label_count_distribution(training_data)